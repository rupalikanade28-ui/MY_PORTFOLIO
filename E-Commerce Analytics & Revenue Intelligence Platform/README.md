# 🛒 ShopSmart India — E-Commerce Analytics Project
### Fresher Data Analyst Portfolio | SQL + Python + Streamlit

---

## The Business Problem This Solves

A mid-sized Indian D2C e-commerce brand (like Nykaa, Mamaearth, or a Myntra seller) has 3 years of sales data and needs answers to real questions their leadership team asks every week:

| Business Question |
|---|---|
| Is our revenue growing or shrinking? | Revenue trend + MoM/YoY SQL view |
| Which customers are most valuable? | RFM segmentation (8 segments) |
| Are customers coming back after 1st purchase? | Cohort retention heatmap |
| Which products should we push / drop? | ABC analysis + margin view |
| Which marketing campaigns had the best ROI? | Campaign ROAS + ROI view |
| Where do users drop off before buying? | Funnel analysis by channel |
| Which customers might stop buying? | Python churn risk scorer |
| Which cities drive the most revenue? | Geographic heatmap |

---

##  Project Structure

```
ecom_analytics/
├── data/
│   ├── generate_data.py      ← 50K orders, 8K customers, 3 years
│   ├── ecom.db               ← SQLite database (pre-built)
│   └── python_outputs.json   ← Pre-computed Python analysis
├── sql/
│   └── analytics_views.sql   ← 10 SQL views (the core of the project)
├── python/
│   └── analysis.py           ← Cohort, churn, attribution, cross-sell
├── dashboard/
│   └── app.py                ← 9-page Streamlit dashboard
└── requirements.txt
```

---

##  How to Run

```bash
# 1. Install
pip install -r requirements.txt

# 2. Data already generated — or regenerate:
python data/generate_data.py

# 3. Run Python analysis
python python/analysis.py

# 4. Launch dashboard
streamlit run dashboard/app.py
```

---

##  Database Schema

| Table | Rows | Description |
|---|---|---|
| customers | 8,000 | Demographics, acquisition channel, city |
| products | 498 | Category, brand, price, cost, margin |
| orders | 50,423 | Order-level data with campaign and channel |
| order_items | 84,183 | Product-level items per order |
| sessions | 175,697 | Web sessions: device, bounce, conversion |
| campaign_stats | 349 | Daily campaign impressions, clicks, spend |
| campaigns | 10 | 10 campaigns across 3 years |

---

##  SQL Skills Demonstrated

| Concept | Where |
|---|---|
| `LAG()` / `LEAD()` | Revenue trend MoM/YoY |
| `SUM() OVER()` | Cumulative YTD, Pareto cumulative |
| `AVG() OVER (ROWS BETWEEN…)` | 3-month rolling average |
| `NTILE(5)` | RFM scoring quintiles |
| `RANK()` / `DENSE_RANK()` | Product ranking, geo ranking |
| `PARTITION BY` | Segment-level averages, seasonal index |
| Multi-table `JOIN` | Orders + items + products + customers |
| `CASE WHEN` | Segment labels, alert levels, ABC class |
| CTEs (`WITH`) | Multi-step RFM, cohort, CLV calculations |
| Subqueries | Retention rate calculation |
| `NULLIF()` | Division-safe ratio calculations |
| `julianday()` | Date difference in days |
| `strftime()` | Month/year extraction |
| `CREATE VIEW` | 10 reusable analytical views |

---

##  Python Skills Demonstrated

| Analysis | Tool |
|---|---|
| Cohort retention pivot | `pandas.pivot_table` |
| Customer value distribution | `pandas.cut`, `groupby` |
| Churn risk scoring | Custom rule-based function |
| Cross-sell pair mining | Dictionary frequency counting |
| Campaign type comparison | GroupBy aggregation |
| JSON export for dashboard | `json.dump` |

---

## Important Points

1. **"Designed an RFM segmentation model** in pure SQL using NTILE window functions, classifying 8K customers into 8 actionable segments — identifying ₹X Cr of at-risk revenue."

2. **"Built a cohort retention analysis** that revealed Month-1 retention was only ~15%, which means 85% of new customers don't return — a key insight for re-engagement campaigns."

3. **"Calculated ROAS for 10 campaigns** and found Paid Search delivered 14x return vs Email's 5x — actionable budget reallocation recommendation."

4. **"Created a churn risk scorer** in Python that flagged 105 high-value customers at risk, enabling proactive win-back outreach."

5. **"Discovered Electronics + Fashion is the #1 cross-sell pair** (2,173 co-purchases) — business case for a 'Complete the Look' bundle feature."

---

##  Tech Stack

- **Database**: SQLite (production-equivalent SQL; same patterns on PostgreSQL / BigQuery / Snowflake)
- **Language**: Python 3.10+
- **Data layer**: Pandas, NumPy
- **Dashboard**: Streamlit + Plotly
- **SQL ratio**: ~80% SQL, ~20% Python

---

## Dashboard Pages

1. Executive Summary — KPIs + revenue + category split
2. Revenue Trends — MoM growth + rolling average + YoY
3. RFM Segments — scatter map + segment pie + revenue bars
4. Cohort Retention — heatmap + decay curve
5. Product ABC — Pareto chart + discount vs margin
6. Campaign ROI — ROI bars + spend vs revenue + ROAS
7. Funnel Analysis — sessions → conversion by channel + device
8. Geographic View — city bars + treemap
9. Churn Risk — risk distribution + win-back list + cross-sell pairs
