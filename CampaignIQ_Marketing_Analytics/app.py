import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="CampaignIQ Dashboard",
    layout="wide",
    page_icon="📊"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("dataset/marketing_data.csv")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert types
    df["Income"] = pd.to_numeric(df["Income"], errors="coerce")
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["TotalSpend"] = pd.to_numeric(df["TotalSpend"], errors="coerce")

    df = df.dropna()

    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("🎯 CampaignIQ")

country_filter = st.sidebar.multiselect(
    "Select Country",
    options=df["Country"].unique(),
    default=df["Country"].unique()
)

segment_filter = st.sidebar.multiselect(
    "Select Segment",
    options=df["Segment"].unique(),
    default=df["Segment"].unique()
)

df = df[
    (df["Country"].isin(country_filter)) &
    (df["Segment"].isin(segment_filter))
]

# ---------------- HEADER ----------------
st.title("📊 CampaignIQ Marketing Dashboard")
st.caption("Customer Behavior • Revenue • Campaign Insights")

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Customers", len(df))
col2.metric("Total Revenue", f"${df['TotalSpend'].sum():,.0f}")
col3.metric("Avg Income", f"${df['Income'].mean():,.0f}")
col4.metric("Avg Spend", f"${df['TotalSpend'].mean():,.0f}")

st.divider()

# ---------------- ROW 1 ----------------
col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        df.groupby("Country")["TotalSpend"].sum().reset_index(),
        x="Country",
        y="TotalSpend",
        title="Revenue by Country",
        color="Country"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.pie(
        df,
        names="Segment",
        title="Customer Segmentation"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- ROW 2 ----------------
col3, col4 = st.columns(2)

with col3:
    fig3 = px.scatter(
        df,
        x="Income",
        y="TotalSpend",
        color="Priority_Tier",
        size="TotalSpend",
        title="Income vs Spending Behavior"
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    campaign_cols = [
        "AcceptedCmp1","AcceptedCmp2","AcceptedCmp3",
        "AcceptedCmp4","AcceptedCmp5","Response"
    ]

    campaign_rate = df[campaign_cols].mean().reset_index()
    campaign_rate.columns = ["Campaign", "Success Rate"]

    fig4 = px.bar(
        campaign_rate,
        x="Campaign",
        y="Success Rate",
        title="Campaign Performance",
        color="Campaign"
    )
    st.plotly_chart(fig4, use_container_width=True)

# ---------------- ROW 3 ----------------
col5, col6 = st.columns(2)

with col5:
    fig5 = px.histogram(
        df,
        x="Age",
        nbins=30,
        title="Customer Age Distribution"
    )
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    risk_df = df.groupby("Priority_Tier")[["HighValue", "AtRisk"]].mean().reset_index()

    fig6 = px.bar(
        risk_df,
        x="Priority_Tier",
        y=["HighValue", "AtRisk"],
        barmode="group",
        title="High Value vs At Risk Customers"
    )
    st.plotly_chart(fig6, use_container_width=True)