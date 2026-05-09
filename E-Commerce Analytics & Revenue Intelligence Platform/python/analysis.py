"""
ShopSmart India — Python Analysis Layer  (20% of project)
Covers:
  1. Cohort retention heatmap (Pandas pivot)
  2. Customer value distribution (NumPy + Pandas)
  3. Simple churn prediction score (rule-based, no heavy ML)
  4. Campaign attribution model (linear touch)
  5. Export summary for dashboard
"""

import pandas as pd
import numpy as np
import sqlite3, os, json

DB   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/ecom.db")
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/python_outputs.json")

conn = sqlite3.connect(DB)
def q(sql): return pd.read_sql(sql, conn)


# ═══════════════════════════════════════════════════════════════════
# 1. COHORT RETENTION HEATMAP
# ═══════════════════════════════════════════════════════════════════
print("1. Building cohort retention heatmap...")

cohort_raw = q("SELECT * FROM v_cohort_retention ORDER BY cohort_month, month_number")

# Get cohort sizes (month_number = 0 = first purchase month)
cohort_sizes = (
    cohort_raw[cohort_raw.month_number == 0]
    .set_index("cohort_month")["active_customers"]
)

# Pivot: rows = cohort month, cols = month_number 0..11
pivot = cohort_raw.pivot_table(
    index="cohort_month", columns="month_number", values="active_customers"
).iloc[:, :13]  # 0 to 12 months

# Retention % = each cell / cohort size at month 0
retention_pct = pivot.div(pivot[0], axis=0).round(3) * 100

# Keep only cohorts with enough data (at least 6 months visible)
retention_pct = retention_pct[retention_pct.index <= "2024-06"]

# Summary stats
avg_m1_retention = retention_pct[1].mean()
avg_m3_retention = retention_pct[3].mean()
avg_m6_retention = retention_pct[6].mean() if 6 in retention_pct.columns else None

print(f"   Avg Month-1 Retention : {avg_m1_retention:.1f}%")
print(f"   Avg Month-3 Retention : {avg_m3_retention:.1f}%")
if avg_m6_retention:
    print(f"   Avg Month-6 Retention : {avg_m6_retention:.1f}%")


# ═══════════════════════════════════════════════════════════════════
# 2. CUSTOMER VALUE DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════
print("\n2. Customer value distribution...")

clv_df = q("SELECT * FROM v_clv")

# Value tier counts
tier_counts = clv_df["value_tier"].value_counts().to_dict()

# Channel-wise average CLV
channel_clv = (
    clv_df.groupby("acq_channel")["total_spend"]
    .agg(["mean","median","count"])
    .round(2)
    .rename(columns={"mean":"avg_spend","median":"median_spend","count":"customers"})
    .reset_index()
    .to_dict("records")
)

# Age bucket analysis
clv_df["age_bucket"] = pd.cut(
    clv_df["age"],
    bins=[18,25,35,45,55,65],
    labels=["18-25","26-35","36-45","46-55","55+"]
)
age_clv = (
    clv_df.groupby("age_bucket", observed=True)["total_spend"]
    .agg(["mean","count"])
    .round(2)
    .rename(columns={"mean":"avg_spend","count":"customers"})
    .reset_index()
)
age_clv["age_bucket"] = age_clv["age_bucket"].astype(str)
age_clv_records = age_clv.to_dict("records")

print(f"   Tier breakdown: {tier_counts}")


# ═══════════════════════════════════════════════════════════════════
# 3. CHURN RISK SCORING  (rule-based — no scikit-learn needed)
# ═══════════════════════════════════════════════════════════════════
print("\n3. Churn risk scoring...")

rfm_df = q("SELECT * FROM v_rfm")

def churn_score(row):
    """
    Score 0–100. Higher = more likely to churn.
    Factors: recency, frequency, monetary, premium status
    """
    score = 0
    # Recency penalty (main driver)
    if row["recency_days"] > 180: score += 40
    elif row["recency_days"] > 90: score += 25
    elif row["recency_days"] > 45: score += 10
    # Low frequency
    if row["frequency"] == 1: score += 25
    elif row["frequency"] <= 3: score += 10
    # Low monetary
    if row["monetary"] < 1000: score += 15
    elif row["monetary"] < 3000: score += 7
    # Premium customers less likely to churn
    if row["is_premium"]: score -= 15
    return min(100, max(0, score))

rfm_df["churn_score"] = rfm_df.apply(churn_score, axis=1)
rfm_df["churn_risk"]  = pd.cut(
    rfm_df["churn_score"],
    bins=[-1,30,60,100],
    labels=["Low","Medium","High"]
)

churn_summary = rfm_df["churn_risk"].value_counts().to_dict()
churn_summary = {str(k): int(v) for k, v in churn_summary.items()}

# Top 20 high-risk high-value customers to win back
high_risk_high_value = (
    rfm_df[(rfm_df["churn_risk"]=="High") & (rfm_df["monetary"]>=10000)]
    .nlargest(20, "monetary")[
        ["customer_id","city","monetary","frequency","recency_days","acq_channel"]
    ]
    .to_dict("records")
)

print(f"   Churn risk distribution: {churn_summary}")
print(f"   High-risk high-value customers: {len(high_risk_high_value)}")


# ═══════════════════════════════════════════════════════════════════
# 4. CAMPAIGN MULTI-TOUCH ATTRIBUTION  (linear model)
# ═══════════════════════════════════════════════════════════════════
print("\n4. Campaign attribution analysis...")

camp_perf = q("SELECT * FROM v_campaign_performance")

# ROI tiering
camp_perf["roi_tier"] = pd.cut(
    camp_perf["roi_pct"].fillna(0),
    bins=[-999, 0, 100, 300, 9999],
    labels=["Loss","Low ROI","Good ROI","Excellent ROI"]
)

# Best channel by avg ROAS
channel_roas = (
    camp_perf.groupby("channel")["roas"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
    .to_dict()
)

# Seasonal vs Product campaign comparison
type_summary = (
    camp_perf.groupby("type")[["total_spend","attributed_revenue","roas","roi_pct"]]
    .mean()
    .round(2)
    .reset_index()
    .to_dict("records")
)

print(f"   Best channel ROAS: {list(channel_roas.items())[:3]}")


# ═══════════════════════════════════════════════════════════════════
# 5. PRODUCT CROSS-SELL OPPORTUNITY
# ═══════════════════════════════════════════════════════════════════
print("\n5. Cross-sell category analysis...")

# Which category pairs are bought together most often?
multi_item = q("""
    SELECT o.order_id, oi.category
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status != 'Cancelled'
""")

# Orders with 2+ categories
order_cats = multi_item.groupby("order_id")["category"].apply(list)
pairs = {}
for cats in order_cats:
    cats = sorted(set(cats))
    if len(cats) >= 2:
        for i in range(len(cats)):
            for j in range(i+1, len(cats)):
                key = f"{cats[i]} + {cats[j]}"
                pairs[key] = pairs.get(key, 0) + 1

top_pairs = sorted(pairs.items(), key=lambda x: -x[1])[:10]
top_pairs_list = [{"pair": k, "count": v} for k,v in top_pairs]
print(f"   Top pair: {top_pairs[0]}")


# ═══════════════════════════════════════════════════════════════════
# 6. DEVICE & CHANNEL PERFORMANCE MATRIX
# ═══════════════════════════════════════════════════════════════════
print("\n6. Device × channel matrix...")

device_channel = q("""
    SELECT
        device, channel,
        COUNT(DISTINCT order_id)        AS orders,
        ROUND(SUM(total),0)             AS revenue,
        ROUND(AVG(total),0)             AS aov,
        ROUND(AVG(is_premium)*100,1)    AS premium_pct
    FROM orders
    WHERE status != 'Cancelled'
    GROUP BY device, channel
    ORDER BY revenue DESC
""").to_dict("records")


# ═══════════════════════════════════════════════════════════════════
# SAVE ALL OUTPUTS
# ═══════════════════════════════════════════════════════════════════
output = {
    "cohort_retention_pct": {
        str(idx): {str(int(col)): (round(val,1) if not pd.isna(val) else None)
                   for col, val in row.items()}
        for idx, row in retention_pct.iterrows()
    },
    "cohort_summary": {
        "avg_m1_retention": round(avg_m1_retention, 1),
        "avg_m3_retention": round(avg_m3_retention, 1),
        "avg_m6_retention": round(avg_m6_retention, 1) if avg_m6_retention else None,
    },
    "tier_counts":          tier_counts,
    "channel_clv":          channel_clv,
    "age_clv":              age_clv_records,
    "churn_summary":        churn_summary,
    "high_risk_customers":  high_risk_high_value,
    "channel_roas":         channel_roas,
    "campaign_type_summary":type_summary,
    "top_category_pairs":   top_pairs_list,
    "device_channel_matrix":device_channel,
}

with open(OUT, "w") as f:
    json.dump(output, f, indent=2, default=str)

conn.close()
print(f"\n✅ Python outputs saved → {OUT}")
print("\n══ SUMMARY ══════════════════════════════════════")
print(f"  Churn risk HIGH    : {churn_summary.get('High',0):,} customers")
print(f"  Month-1 retention  : {avg_m1_retention:.1f}%")
print(f"  Top cross-sell pair: {top_pairs[0][0]} ({top_pairs[0][1]:,} orders)")
print(f"  Best ROAS channel  : {list(channel_roas.keys())[0]} ({list(channel_roas.values())[0]}x)")
