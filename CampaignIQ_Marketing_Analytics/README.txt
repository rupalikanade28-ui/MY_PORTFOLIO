╔══════════════════════════════════════════════════════════════════╗
║         CampaignIQ — Predictive Customer Analytics              ║
║              & Marketing Optimization                           ║
╚══════════════════════════════════════════════════════════════════╝

DOMAIN   : Marketing / E-Commerce
DATASET  : 2,240 customers · 28 features · 6 marketing campaigns
TOOLS    : Python · Pandas · NumPy · Matplotlib · Seaborn · Scikit-learn
AUTHOR   : Rupali Kanade
──────────────────────────────────────────────────────────────────
PROJECT STRUCTURE
──────────────────────────────────────────────────────────────────
CampaignIQ_Marketing_Analytics/
│
├── marketing_analysis.ipynb       ← Main Jupyter Notebook (run this)
│
├── dataset/
│   ├── marketing_data.csv         ← Raw customer + campaign data
│   └── marketing_data_dictionary.csv  ← Column descriptions
│
├── visualizations/                ← All 15 output charts (PNG)
│   ├── Q1_Segmentation.png
│   ├── Q2_Priority_Tiers.png
│   ├── Q3_Campaign_Response_Rates.png
│   ├── Q4_Product_Revenue.png
│   ├── Q5_Country_Analysis.png
│   ├── Q6_HighValue_AtRisk.png
│   ├── Q7_Recency_Response.png
│   ├── Q8_Income_Spending.png
│   ├── Q9_Channels.png
│   ├── Q10_Discount_Sensitivity.png
│   ├── Q11_Children_Behaviour.png
│   ├── Q12_Campaign_Strategy.png
│   ├── Q13_Predictive_Model.png
│   ├── Q14_Personalisation.png
│   └── Dashboard_Executive.png
│
└── README.txt                     ← This file

──────────────────────────────────────────────────────────────────
HOW TO RUN
──────────────────────────────────────────────────────────────────
1. Install dependencies:
   pip install pandas numpy matplotlib seaborn scikit-learn jupyter

2. Launch Jupyter:
   jupyter notebook

3. Open marketing_analysis.ipynb

4. Run All Cells:
   Kernel → Restart & Run All

   Charts will be saved to the visualizations/ folder automatically.

──────────────────────────────────────────────────────────────────
14 BUSINESS QUESTIONS SOLVED
──────────────────────────────────────────────────────────────────
Q1  Which customer segments are most likely to respond?
    → Method : KMeans Clustering (k=4, Elbow Method)
    → Finding: Segment 0 has 52% response rate (highest)

Q2  Which customers should be prioritized for campaigns?
    → Method : RFM Scoring (Recency + Frequency + Monetary)
    → Finding: High-tier (827 customers) respond at 43%

Q3  What is the overall campaign response rate?
    → Method : Aggregation across 6 campaign columns
    → Finding: 27.3% overall; Last Campaign best at 15%

Q4  Which product categories generate the most revenue?
    → Method : Sum aggregation across product spend columns
    → Finding: Wines = $675K (50%+ of all revenue)

Q5  Which countries have the strongest customer base?
    → Method : GroupBy Country multi-metric analysis
    → Finding: Spain dominates with 1,092 customers (49%)

Q6  Which customers are high-value but at risk?
    → Method : Rule-based dual flagging (spend + recency)
    → Finding: 221 customers, avg spend $1,500, avg recency 80d

Q7  How does recency affect campaign response?
    → Method : Binned recency → response rate trend
    → Finding: 37% response (0-15d) drops to 22% (76-100d)

Q8  How does income relate to spending behavior?
    → Method : Pearson Correlation + Quartile breakdown
    → Finding: r = 0.79 strong positive — income predicts spend

Q9  Which purchase channels are most used?
    → Method : Volume aggregation + segment cross-tab
    → Finding: Store #1 (12,791), Web #2 (9,046)

Q10 Which customers are more discount-sensitive?
    → Method : DealRate quartile threshold flagging
    → Finding: Discount buyers earn $15K less, spend $510 less

Q11 Do customers with children behave differently?
    → Method : Binary group comparison across all metrics
    → Finding: Child-free spend 44% more, respond at 44% vs 20%

Q12 Which groups need premium/discount/win-back campaigns?
    → Method : Rule-based strategy assignment per segment
    → Finding: 3 strategies mapped — Premium, Discount, Win-Back

Q13 How can we reduce wasted marketing spend?
    → Method : Gradient Boosting Classifier + threshold simulation
    → Finding: AUC = 0.77 | 73.8% fewer wasted contacts

Q14 How can campaigns be personalized?
    → Method : idxmax per segment for product + channel
    → Finding: Wines + Store = universal; tailor message by segment

──────────────────────────────────────────────────────────────────
KEY METRICS AT A GLANCE
──────────────────────────────────────────────────────────────────
  Total Customers       :  2,213
  Overall Response Rate :  27.3%
  Avg Annual Income     :  $52,237
  Avg Total Spend       :  $607
  Top Product Revenue   :  Wines ($675K)
  Top Purchase Channel  :  In-Store (12,791 purchases)
  HV At-Risk Customers  :  221 (10%)
  ML Model AUC          :  0.77
  Contact Reduction     :  73.8%

──────────────────────────────────────────────────────────────────
AUTHOR NOTE
──────────────────────────────────────────────────────────────────
This project follows a real-world senior data analyst workflow:

  1. Understand the data (dictionary + EDA)
  2. Clean and engineer features
  3. Match each business question to the right method
  4. Visualise every answer with proof
  5. Build ML for predictive/actionable output
  6. Deliver clean, reproducible outputs

Built with Python 3 · No proprietary tools required.


## Author

**Rupali Kanade**  
Aspiring Data Analyst  
SQL | Python | Tableau | Streamlit | Business Intelligence

GitHub: https://github.com/rupalikanade28-ui  
LinkedIn: https://linkedin.com/in/rupalikanade
══════════════════════════════════════════════════════════════════
