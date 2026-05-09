"""
ShopSmart India — E-Commerce Analytics Dashboard
Run: streamlit run dashboard/app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3, json, os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="ShopSmart Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB    = os.path.join(BASE, "data", "ecom.db")
PY_OUT= os.path.join(BASE, "data", "python_outputs.json")

C = {
    "primary": "#FF6B35", "secondary": "#004E89",
    "success": "#1A936F", "warning":  "#F4A261",
    "danger":  "#E63946", "purple":   "#7B2D8B",
    "teal":    "#2EC4B6", "gold":     "#E9C46A",
    "bg":      "#0F172A", "card":     "#1E293B",
}

@st.cache_resource
def get_conn(): return sqlite3.connect(DB, check_same_thread=False)
@st.cache_data(ttl=300)
def q(sql): return pd.read_sql(sql, get_conn())
@st.cache_data
def load_py(): return json.load(open(PY_OUT))

def fmt_inr(v):
    if v >= 1e7:  return f"₹{v/1e7:.2f} Cr"
    if v >= 1e5:  return f"₹{v/1e5:.1f} L"
    if v >= 1000: return f"₹{v/1000:.1f}K"
    return f"₹{v:.0f}"

st.markdown("""
<style>
.stMetric{background:#1E293B;border-radius:12px;padding:14px;border-left:4px solid #FF6B35;}
.stMetric label{color:#94A3B8!important;font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;}
div[data-testid="metric-container"]>div{font-size:1.55rem;font-weight:700;}
.section-title{font-size:1.05rem;font-weight:700;color:#FF6B35;
  border-bottom:2px solid #FF6B35;padding-bottom:5px;margin:18px 0 12px 0;}
</style>
""", unsafe_allow_html=True)

_LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#CBD5E1",
    legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#CBD5E1"),
)
def L(**overrides):
    """Return layout dict, merging any overrides (avoids duplicate-key errors)"""
    return {**_LAYOUT_BASE, **overrides}
LAYOUT = _LAYOUT_BASE   # kept for backward compat
GRID = dict(gridcolor="#334155")

# ── SIDEBAR ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 ShopSmart India")
    st.markdown("*E-Commerce Analytics*")
    st.markdown("---")
    page = st.radio("Navigate", [
        "🏠  Executive Summary",
        "📈  Revenue Trends",
        "👥  Customer RFM Segments",
        "🔁  Cohort Retention",
        "📦  Product Performance",
        "📣  Campaign ROI",
        "🌐  Funnel Analysis",
        "🗺️  Geographic View",
        "⚠️  Churn Risk",
    ])
    st.markdown("---")
    st.caption("📅 Jan 2022 – Dec 2024")
    st.caption("🏪 50K orders · 8K customers · 498 products")

py = load_py()

# ════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ════════════════════════════════════════════════════════════════════
if page == "🏠  Executive Summary":
    st.title("🛒 ShopSmart India — Analytics Dashboard")
    st.markdown("**3-Year E-Commerce Performance Overview · Jan 2022 – Dec 2024**")
    st.markdown("---")

    kpi = q("""
        SELECT ROUND(SUM(total),0) AS rev,
               COUNT(DISTINCT order_id) AS orders,
               COUNT(DISTINCT customer_id) AS customers,
               ROUND(AVG(total),0) AS aov,
               SUM(CASE WHEN status='Returned' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS return_rate
        FROM orders WHERE status != 'Cancelled'
    """).iloc[0]

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("💰 Total Revenue",  fmt_inr(kpi["rev"]))
    c2.metric("🛍️ Total Orders",   f"{int(kpi['orders']):,}")
    c3.metric("👥 Customers",      f"{int(kpi['customers']):,}")
    c4.metric("🎯 Avg Order Value",fmt_inr(kpi["aov"]))
    c5.metric("↩️ Return Rate",    f"{kpi['return_rate']:.1f}%")

    st.markdown("---")
    col1, col2 = st.columns([2,1])

    with col1:
        st.markdown('<div class="section-title">📈 Monthly Revenue + Orders</div>', unsafe_allow_html=True)
        trend = q("SELECT * FROM v_revenue_trend ORDER BY yr_mo")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=trend["yr_mo"], y=trend["revenue"],
            name="Revenue", marker_color=C["primary"], opacity=0.85), secondary_y=False)
        fig.add_trace(go.Scatter(x=trend["yr_mo"], y=trend["aov"],
            name="AOV", line=dict(color=C["teal"], width=2.5), mode="lines"),
            secondary_y=True)
        fig.update_layout(**L())
        fig.update_yaxes(**GRID); fig.update_xaxes(tickangle=-40)
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.markdown('<div class="section-title">🛍️ Revenue by Category</div>', unsafe_allow_html=True)
        cat_rev = q("""
            SELECT oi.category, ROUND(SUM(oi.revenue),0) AS rev
            FROM order_items oi JOIN orders o ON oi.order_id=o.order_id
            WHERE o.status != 'Cancelled'
            GROUP BY oi.category ORDER BY rev DESC
        """)
        fig2 = px.pie(cat_rev, names="category", values="rev",
            hole=0.5, color_discrete_sequence=px.colors.sequential.Sunset_r)
        fig2.update_layout(**L(margin=dict(l=0,r=0,t=10,b=0)))
        st.plotly_chart(fig2, width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-title">📣 Channel Acquisition Mix</div>', unsafe_allow_html=True)
        ch = q("SELECT acq_channel, COUNT(*) AS n FROM customers GROUP BY acq_channel ORDER BY n DESC")
        fig3 = px.bar(ch, x="acq_channel", y="n", color="n",
            color_continuous_scale="Oranges", text="n")
        fig3.update_traces(textposition="outside")
        fig3.update_layout(**L(showlegend=False, coloraxis_showscale=False,
            xaxis_title="", yaxis_title="Customers"))
        fig3.update_yaxes(**GRID)
        st.plotly_chart(fig3, width='stretch')

    with col4:
        st.markdown('<div class="section-title">📱 Device Split</div>', unsafe_allow_html=True)
        dev = q("SELECT device, COUNT(DISTINCT order_id) AS orders FROM orders WHERE status!='Cancelled' GROUP BY device")
        fig4 = px.pie(dev, names="device", values="orders", hole=0.55,
            color_discrete_map={"Mobile":C["primary"],"Desktop":C["secondary"],"Tablet":C["teal"]})
        fig4.update_layout(**L(margin=dict(l=0,r=0,t=10,b=0)))
        st.plotly_chart(fig4, width='stretch')


# ════════════════════════════════════════════════════════════════════
# PAGE 2 — REVENUE TRENDS
# ════════════════════════════════════════════════════════════════════
elif page == "📈  Revenue Trends":
    st.title("📈 Revenue Trend Analysis")
    st.markdown("*MoM growth · YoY comparison · Rolling averages · YTD tracking*")

    trend = q("SELECT * FROM v_revenue_trend ORDER BY yr_mo")
    yr_filter = st.multiselect("Year", ["2022","2023","2024"], default=["2022","2023","2024"])
    trend = trend[trend["yr"].isin(yr_filter)]

    c1,c2,c3 = st.columns(3)
    c1.metric("📈 Best MoM Growth",
        f"{trend['mom_growth_pct'].max():.1f}%",
        trend.loc[trend['mom_growth_pct'].idxmax(),'yr_mo'] if len(trend) else "")
    c2.metric("📉 Worst MoM",
        f"{trend['mom_growth_pct'].min():.1f}%",
        trend.loc[trend['mom_growth_pct'].idxmin(),'yr_mo'] if len(trend) else "")
    c3.metric("📊 Avg AOV", fmt_inr(trend["aov"].mean()))

    st.markdown("---")
    # MoM growth bars
    fig = go.Figure()
    colors = [C["success"] if v>=0 else C["danger"] for v in trend["mom_growth_pct"].fillna(0)]
    fig.add_trace(go.Bar(x=trend["yr_mo"], y=trend["mom_growth_pct"],
        marker_color=colors, name="MoM %"))
    fig.add_hline(y=0, line_color="white", line_width=1)
    fig.update_layout(**L(title="Month-over-Month Revenue Growth %",
        yaxis_title="Growth %"))
    fig.update_yaxes(**GRID); fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, width='stretch')

    col1,col2 = st.columns(2)
    with col1:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=trend["yr_mo"], y=trend["revenue"],
            name="Actual", line=dict(color=C["primary"],width=2)))
        fig2.add_trace(go.Scatter(x=trend["yr_mo"], y=trend["rolling_avg_3m"],
            name="3M Rolling Avg", line=dict(color=C["teal"],width=2,dash="dot")))
        fig2.update_layout(**L(title="Revenue vs 3-Month Rolling Average"))
        fig2.update_yaxes(**GRID)
        st.plotly_chart(fig2, width='stretch')

    with col2:
        fig3 = px.bar(trend, x="mo", y="ytd_revenue", color="yr",
            barmode="group", title="YTD Revenue by Month",
            color_discrete_sequence=[C["primary"],C["teal"],C["gold"]])
        fig3.update_layout(**L())
        fig3.update_yaxes(**GRID)
        st.plotly_chart(fig3, width='stretch')


# ════════════════════════════════════════════════════════════════════
# PAGE 3 — RFM CUSTOMER SEGMENTS
# ════════════════════════════════════════════════════════════════════
elif page == "👥  Customer RFM Segments":
    st.title("👥 RFM Customer Segmentation")
    st.markdown("*Recency · Frequency · Monetary — who are your best customers?*")

    rfm = q("SELECT * FROM v_rfm")
    seg_counts = rfm["rfm_segment"].value_counts().reset_index()
    seg_counts.columns = ["segment","count"]
    seg_rev = rfm.groupby("rfm_segment")["monetary"].sum().reset_index()
    seg_rev.columns = ["segment","revenue"]

    c1,c2,c3,c4 = st.columns(4)
    champions = rfm[rfm["rfm_segment"]=="Champions"]
    at_risk   = rfm[rfm["rfm_segment"]=="At Risk"]
    c1.metric("🏆 Champions",    len(champions), fmt_inr(champions["monetary"].sum()))
    c2.metric("⚠️  At Risk",     len(at_risk),   fmt_inr(at_risk["monetary"].sum()))
    c3.metric("💤 Hibernating",  len(rfm[rfm["rfm_segment"]=="Hibernating"]))
    c4.metric("🆕 New Customers",len(rfm[rfm["rfm_segment"]=="New Customers"]))

    col1,col2 = st.columns([3,2])
    with col1:
        # Scatter: Recency vs Monetary, colored by segment
        sample = rfm.sample(min(2000,len(rfm)), random_state=42)
        fig = px.scatter(sample, x="recency_days", y="monetary",
            color="rfm_segment", size="frequency",
            hover_data=["customer_id","city"],
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Customer Map: Recency vs Spend")
        fig.update_layout(**L())
        fig.update_xaxes(**GRID, title="Days since last order")
        fig.update_yaxes(**GRID, title="Total spend ₹")
        st.plotly_chart(fig, width='stretch')

    with col2:
        fig2 = px.pie(seg_counts, names="segment", values="count",
            hole=0.5, title="Customers per Segment",
            color_discrete_sequence=px.colors.qualitative.Bold)
        fig2.update_layout(**L(margin=dict(l=0,r=0,t=30,b=0)))
        st.plotly_chart(fig2, width='stretch')

    # Revenue per segment bar
    merged = seg_counts.merge(seg_rev, on="segment")
    merged["avg_value"] = (merged["revenue"]/merged["count"]).round(0)
    fig3 = px.bar(merged.sort_values("revenue",ascending=False),
        x="segment", y="revenue", color="avg_value",
        color_continuous_scale="Oranges",
        text="count", title="Revenue & Customer Count per Segment")
    fig3.update_traces(texttemplate="%{text} cust", textposition="outside")
    fig3.update_layout(**L(xaxis_tickangle=-25, coloraxis_showscale=False))
    fig3.update_yaxes(**GRID)
    st.plotly_chart(fig3, width='stretch')


# ════════════════════════════════════════════════════════════════════
# PAGE 4 — COHORT RETENTION
# ════════════════════════════════════════════════════════════════════
elif page == "🔁  Cohort Retention":
    st.title("🔁 Cohort Retention Analysis")
    st.markdown("*How many customers from each joining month come back to buy again?*")

    py = load_py()
    c1,c2,c3 = st.columns(3)
    c1.metric("Month 1 Retention", f"{py['cohort_summary']['avg_m1_retention']}%")
    c2.metric("Month 3 Retention", f"{py['cohort_summary']['avg_m3_retention']}%")
    if py["cohort_summary"]["avg_m6_retention"]:
        c3.metric("Month 6 Retention", f"{py['cohort_summary']['avg_m6_retention']}%")

    # Build heatmap from python output
    cr = py["cohort_retention_pct"]
    cohorts = sorted(cr.keys())[-18:]  # last 18 cohorts
    months  = list(range(0,10))
    z_data, y_labels = [], []
    for coh in cohorts:
        row = [cr[coh].get(str(m)) for m in months]
        z_data.append(row)
        y_labels.append(coh)

    fig = go.Figure(go.Heatmap(
        z=z_data, x=[f"M+{m}" for m in months], y=y_labels,
        colorscale="YlOrRd", reversescale=True,
        text=[[f"{v:.0f}%" if v else "" for v in row] for row in z_data],
        texttemplate="%{text}", hovertemplate="Cohort %{y}<br>Month %{x}<br>Retention: %{z:.1f}%<extra></extra>",
        zmin=0, zmax=60
    ))
    fig.update_layout(**L(title="Retention % by Cohort (M+0 = first month = 100%)",
        height=500, xaxis_title="Months since first purchase", yaxis_title="Cohort"))
    st.plotly_chart(fig, width='stretch')

    # Month-by-month retention curve
    cohort_raw = q("SELECT * FROM v_cohort_retention WHERE month_number <= 12")
    avg_ret = cohort_raw.groupby("month_number")["active_customers"].mean().reset_index()
    fig2 = px.line(avg_ret, x="month_number", y="active_customers",
        markers=True, title="Average Retention Curve (All Cohorts)",
        color_discrete_sequence=[C["primary"]])
    fig2.update_layout(**L(xaxis_title="Months after first purchase",
        yaxis_title="Avg active customers"))
    fig2.update_xaxes(**GRID); fig2.update_yaxes(**GRID)
    st.plotly_chart(fig2, width='stretch')


# ════════════════════════════════════════════════════════════════════
# PAGE 5 — PRODUCT PERFORMANCE
# ════════════════════════════════════════════════════════════════════
elif page == "📦  Product Performance":
    st.title("📦 Product Performance — ABC Analysis")
    st.markdown("*Revenue, profit margin, ABC classification, top/bottom performers*")

    prod = q("SELECT * FROM v_product_performance ORDER BY rev_rank")
    cat_sel = st.selectbox("Category", ["All"] + sorted(prod["category"].unique().tolist()))
    if cat_sel != "All": prod = prod[prod["category"]==cat_sel]

    a = prod[prod["abc_class"].str.startswith("A")]
    b = prod[prod["abc_class"].str.startswith("B")]
    c_ = prod[prod["abc_class"].str.startswith("C")]
    col1,col2,col3 = st.columns(3)
    col1.metric("🥇 A-Class Products", len(a), fmt_inr(a["total_revenue"].sum()))
    col2.metric("🥈 B-Class Products", len(b), fmt_inr(b["total_revenue"].sum()))
    col3.metric("🥉 C-Class Products", len(c_),fmt_inr(c_["total_revenue"].sum()))

    col1,col2 = st.columns([2,1])
    with col1:
        top20 = prod.nlargest(20,"total_revenue")
        colors = [{"A — High Value":C["success"],"B — Medium Value":C["warning"],
                   "C — Low Value":C["danger"]}.get(r,C["teal"]) for r in top20["abc_class"]]
        fig = go.Figure(go.Bar(x=top20["product_name"], y=top20["total_revenue"],
            marker_color=colors, text=top20["abc_class"],
            textposition="outside"))
        fig.update_layout(**L(title="Top 20 Products by Revenue",
            xaxis_tickangle=-40, margin=dict(b=140)))
        fig.update_yaxes(**GRID)
        st.plotly_chart(fig, width='stretch')

    with col2:
        fig2 = px.scatter(prod.sample(min(200,len(prod))),
            x="avg_discount_pct", y="profit_margin_pct",
            color="abc_class", size="units_sold",
            color_discrete_map={"A — High Value":C["success"],
                "B — Medium Value":C["warning"],"C — Low Value":C["danger"]},
            title="Discount vs Profit Margin", hover_data=["product_name"])
        fig2.update_layout(**L())
        fig2.update_xaxes(**GRID); fig2.update_yaxes(**GRID)
        st.plotly_chart(fig2, width='stretch')

    # Category profit comparison
    cat_profit = q("""
        SELECT oi.category,
               ROUND(AVG(oi.gross_profit/oi.revenue*100),1) AS margin_pct,
               ROUND(SUM(oi.revenue),0) AS revenue
        FROM order_items oi JOIN orders o ON oi.order_id=o.order_id
        WHERE o.status!='Cancelled' AND oi.revenue > 0
        GROUP BY oi.category
    """)
    fig3 = px.bar(cat_profit.sort_values("margin_pct",ascending=False),
        x="category", y="margin_pct", color="revenue",
        color_continuous_scale="Greens", text="margin_pct",
        title="Gross Margin % by Category")
    fig3.update_traces(texttemplate="%{text}%", textposition="outside")
    fig3.update_layout(**L(coloraxis_showscale=False))
    fig3.update_yaxes(**GRID)
    st.plotly_chart(fig3, width='stretch')


# ════════════════════════════════════════════════════════════════════
# PAGE 6 — CAMPAIGN ROI
# ════════════════════════════════════════════════════════════════════
elif page == "📣  Campaign ROI":
    st.title("📣 Marketing Campaign Performance")
    st.markdown("*CTR · CVR · ROAS · ROI — which campaigns really paid off?*")

    camp = q("SELECT * FROM v_campaign_performance")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📣 Campaigns Run",   len(camp))
    c2.metric("💸 Total Spend",     fmt_inr(camp["total_spend"].sum()))
    c3.metric("💰 Attributed Rev",  fmt_inr(camp["attributed_revenue"].sum()))
    c4.metric("📊 Avg ROAS",        f"{camp['roas'].mean():.1f}x")

    col1,col2 = st.columns(2)
    with col1:
        camp_s = camp.sort_values("roi_pct",ascending=True)
        colors = [C["success"] if v>=0 else C["danger"] for v in camp_s["roi_pct"].fillna(0)]
        fig = go.Figure(go.Bar(y=camp_s["name"], x=camp_s["roi_pct"],
            orientation="h", marker_color=colors, text=camp_s["roi_pct"],
            texttemplate="%{text:.0f}%"))
        fig.add_vline(x=0, line_color="white")
        fig.update_layout(**L(title="Campaign ROI %", xaxis_title="ROI %", yaxis_title=""))
        fig.update_xaxes(**GRID)
        st.plotly_chart(fig, width='stretch')

    with col2:
        fig2 = px.scatter(camp, x="total_spend", y="attributed_revenue",
            size="conversions", color="type", text="name",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            title="Spend vs Revenue (bubble = conversions)")
        fig2.add_shape(type="line", x0=0,y0=0, x1=camp["total_spend"].max(),
            y1=camp["total_spend"].max(), line=dict(color="white",dash="dot"))
        fig2.update_layout(**L())
        fig2.update_xaxes(**GRID); fig2.update_yaxes(**GRID)
        st.plotly_chart(fig2, width='stretch')

    # Channel ROAS from Python output
    py = load_py()
    ch_roas = pd.DataFrame(list(py["channel_roas"].items()),columns=["channel","roas"])
    fig3 = px.bar(ch_roas.sort_values("roas",ascending=False), x="channel", y="roas",
        color="roas", color_continuous_scale="YlOrRd", text="roas",
        title="Average ROAS by Channel")
    fig3.update_traces(texttemplate="%{text:.1f}x", textposition="outside")
    fig3.update_layout(**L(coloraxis_showscale=False))
    fig3.update_yaxes(**GRID)
    st.plotly_chart(fig3, width='stretch')


# ════════════════════════════════════════════════════════════════════
# PAGE 7 — FUNNEL ANALYSIS
# ════════════════════════════════════════════════════════════════════
elif page == "🌐  Funnel Analysis":
    st.title("🌐 Conversion Funnel by Channel")
    st.markdown("*Sessions → Engagement → Conversion. Where does traffic drop off?*")

    funnel = q("SELECT * FROM v_channel_funnel ORDER BY total_sessions DESC")
    c1,c2,c3 = st.columns(3)
    c1.metric("🌐 Total Sessions",      f"{funnel['total_sessions'].sum():,}")
    c2.metric("✅ Avg Engagement Rate", f"{funnel['engagement_rate_pct'].mean():.1f}%")
    c3.metric("🛒 Avg Conversion Rate", f"{funnel['session_cvr_pct'].mean():.2f}%")

    col1,col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        for label, col_, color in [
            ("Total Sessions","total_sessions",C["secondary"]),
            ("Engaged Sessions","engaged_sessions",C["teal"]),
            ("Converted","converted_sessions",C["primary"]),
        ]:
            fig.add_trace(go.Bar(name=label, x=funnel["channel"], y=funnel[col_],
                marker_color=color))
        fig.update_layout(**L(barmode="group", title="Funnel Stages by Channel",
            xaxis_tickangle=-30))
        fig.update_yaxes(**GRID)
        st.plotly_chart(fig, width='stretch')

    with col2:
        fig2 = px.scatter(funnel, x="avg_session_secs", y="session_cvr_pct",
            size="total_sessions", color="channel", text="channel",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            title="Session Duration vs Conversion Rate")
        fig2.update_layout(**L())
        fig2.update_xaxes(**GRID, title="Avg session (seconds)")
        fig2.update_yaxes(**GRID, title="CVR %")
        st.plotly_chart(fig2, width='stretch')

    # Device CVR
    dev_data = q("""
        SELECT device,
               ROUND(AVG(CASE WHEN bounced=0 THEN 1.0 ELSE 0 END)*100,1) AS engagement_pct,
               ROUND(AVG(converted)*100,2) AS cvr_pct,
               COUNT(*) AS sessions
        FROM sessions GROUP BY device
    """)
    fig3 = px.bar(dev_data, x="device", y="cvr_pct",
        color="engagement_pct", text="cvr_pct",
        color_continuous_scale="Blues", title="Conversion Rate by Device")
    fig3.update_traces(texttemplate="%{text}%", textposition="outside")
    fig3.update_layout(**L(coloraxis_showscale=False))
    fig3.update_yaxes(**GRID)
    st.plotly_chart(fig3, width='stretch')


# ════════════════════════════════════════════════════════════════════
# PAGE 8 — GEO VIEW
# ════════════════════════════════════════════════════════════════════
elif page == "🗺️  Geographic View":
    st.title("🗺️ Geographic Revenue Analysis")
    st.markdown("*Which cities and states drive the most orders and revenue?*")

    geo = q("SELECT * FROM v_geo_performance ORDER BY revenue_rank")
    c1,c2,c3 = st.columns(3)
    c1.metric("🏙️ Top City",     geo.iloc[0]["city"])
    c2.metric("💰 Top City Rev", fmt_inr(geo.iloc[0]["revenue"]))
    c3.metric("🛍️ Top City AOV", fmt_inr(geo.iloc[0]["aov"]))

    col1,col2 = st.columns(2)
    with col1:
        fig = px.bar(geo, x="city", y="revenue", color="state",
            text="revenue_share_pct",
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Revenue by City")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(**L(xaxis_tickangle=-30))
        fig.update_yaxes(**GRID)
        st.plotly_chart(fig, width='stretch')

    with col2:
        fig2 = px.scatter(geo, x="orders_per_customer", y="aov",
            size="revenue", color="city", text="city",
            color_discrete_sequence=px.colors.qualitative.Vivid,
            title="Orders/Customer vs AOV — Bubble = Revenue")
        fig2.update_layout(**L())
        fig2.update_xaxes(**GRID); fig2.update_yaxes(**GRID)
        st.plotly_chart(fig2, width='stretch')

    fig3 = px.treemap(geo, path=["state","city"], values="revenue",
        color="aov", color_continuous_scale="Oranges",
        title="Revenue Treemap: State → City")
    fig3.update_layout(**L())
    st.plotly_chart(fig3, width='stretch')


# ════════════════════════════════════════════════════════════════════
# PAGE 9 — CHURN RISK
# ════════════════════════════════════════════════════════════════════
elif page == "⚠️  Churn Risk":
    st.title("⚠️ Churn Risk Dashboard")
    st.markdown("*Customers showing signs of dropping off — ranked by risk + value*")

    py = load_py()
    churn = py["churn_summary"]

    c1,c2,c3 = st.columns(3)
    c1.metric("🔴 High Risk",   churn.get("High",0), "Need immediate action")
    c2.metric("🟡 Medium Risk", churn.get("Medium",0),"Watch closely")
    c3.metric("🟢 Low Risk",    churn.get("Low",0),  "Healthy")

    churn_df = pd.DataFrame([{"risk":"High",  "count":churn.get("High",0)},
                              {"risk":"Medium","count":churn.get("Medium",0)},
                              {"risk":"Low",   "count":churn.get("Low",0)}])
    col1,col2 = st.columns([1,2])
    with col1:
        fig = px.pie(churn_df, names="risk", values="count", hole=0.55,
            color="risk",
            color_discrete_map={"High":C["danger"],"Medium":C["warning"],"Low":C["success"]},
            title="Churn Risk Distribution")
        fig.update_layout(**L(margin=dict(l=0,r=0,t=30,b=0)))
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.markdown("#### 🎯 High-Value Customers at Risk — Win Back Targets")
        hr = pd.DataFrame(py["high_risk_customers"])
        if len(hr):
            hr["monetary"] = hr["monetary"].apply(lambda x: fmt_inr(float(x)))
            st.dataframe(hr[["customer_id","city","monetary","frequency",
                              "recency_days","acq_channel"]].rename(columns={
                "customer_id":"ID","city":"City","monetary":"Total Spend",
                "frequency":"Orders","recency_days":"Days Inactive",
                "acq_channel":"Channel"}),
                use_container_width=True, height=300)

    # Retention from SQL
    ret = q("SELECT * FROM v_retention_monthly ORDER BY active_month")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=ret["active_month"], y=ret["retention_rate_pct"],
        mode="lines+markers", name="Retention %",
        line=dict(color=C["success"],width=2.5)))
    fig2.add_trace(go.Bar(x=ret["active_month"], y=ret["new_customers"],
        name="New Customers", marker_color=C["teal"], opacity=0.5, yaxis="y2"))
    fig2.update_layout(**L(title="Monthly Retention Rate + New Customer Inflow",
        yaxis=dict(**GRID, title="Retention %"),
        yaxis2=dict(title="New Customers", overlaying="y", side="right", showgrid=False),
        xaxis=dict(tickangle=-40),
        legend=dict(bgcolor="rgba(0,0,0,0)")))
    st.plotly_chart(fig2, use_container_width=True)

    # Category-wise cross-sell
    st.markdown("#### 🔗 Top Category Cross-Sell Pairs (Opportunity for Bundling)")
    pairs = pd.DataFrame(py["top_category_pairs"])
    fig3 = px.bar(pairs.head(8), x="count", y="pair", orientation="h",
        color="count", color_continuous_scale="Oranges",
        text="count", title="Most Frequently Co-Purchased Categories")
    fig3.update_layout(**L(coloraxis_showscale=False))
    fig3.update_xaxes(**GRID)
    st.plotly_chart(fig3, width='stretch') 
