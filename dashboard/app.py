"""Bluestock Mutual Fund Analytics Capstone Project."""

import pathlib
import os as st
import pandas
import pathlib
import pandas as pd
import sqlite3
import pathlib
import os
import plotly.express as px
import plotly.graph_objects as go

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
from plotly.subplots import make_subplots

# Set page config
st.set_page_config(page_title="Bluestock MF Dashboard", page_icon="📈", layout="wide")

# Custom CSS for Bluestock theme
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    h1 {
        color: #1f3a93;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to get DB connection
@st.cache_resource
def get_db_connection():
    return sqlite3.connect('bluestock_mf.db', check_same_thread=False)

conn = get_db_connection()

# Load specific data globally
@st.cache_data
def load_scorecard():
    return pd.read_csv(PROJECT_ROOT / 'data/processed/fund_scorecard.csv')

@st.cache_data
def load_benchmarks():
    return pd.read_csv(PROJECT_ROOT / 'data/processed/10_benchmark_indices_cleaned.csv')

st.sidebar.title("📈 Bluestock MF Analytics")
page = st.sidebar.radio("Navigation", [
    "Industry Overview", 
    "Fund Performance", 
    "Investor Analytics", 
    "SIP & Market Trends"
])

if page == "Industry Overview":
    st.title("Industry Overview")
    
    # KPIs
    st.markdown("### Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    # Queries for KPIs
    aum_total = pd.read_sql("SELECT MAX(aum_crore) as max_aum FROM fact_aum", conn)['max_aum'].iloc[0]
    sip_total = pd.read_sql("SELECT SUM(amount_inr) as total_sip FROM fact_transactions WHERE transaction_type='SIP'", conn)['total_sip'].iloc[0]
    folios = pd.read_sql("SELECT MAX(num_schemes) as folios FROM fact_aum", conn)['folios'].iloc[0]
    schemes = pd.read_sql("SELECT COUNT(*) as c FROM dim_fund", conn)['c'].iloc[0]
    
    col1.metric("Total AUM", f"₹ {aum_total/100000:,.1f}L Cr")
    col2.metric("Total SIP Inflows", f"₹ {sip_total/1000:,.1f}K Cr")
    col3.metric("Folio Proxies", f"{folios:,.0f}")
    col4.metric("Active Schemes", f"{schemes}")
    
    st.markdown("---")
    
    # AUM Trend
    st.markdown("### Industry AUM Trend (2022-2025)")
    aum_trend = pd.read_sql("""
        SELECT date, SUM(aum_crore) as total_aum 
        FROM fact_aum 
        GROUP BY date 
        ORDER BY date
    """, conn)
    aum_trend['date'] = pd.to_datetime(aum_trend['date'])
    fig1 = px.area(aum_trend, x='date', y='total_aum', color_discrete_sequence=['#1f3a93'])
    st.plotly_chart(fig1, use_container_width=True)
    
    # AUM by AMC
    st.markdown("### AUM by Fund House")
    aum_amc = pd.read_sql("""
        SELECT fund_house, MAX(aum_crore) as max_aum 
        FROM fact_aum 
        GROUP BY fund_house 
        ORDER BY max_aum DESC 
        LIMIT 10
    """, conn)
    fig2 = px.bar(aum_amc, x='fund_house', y='max_aum', color='max_aum', color_continuous_scale='Blues')
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Fund Performance":
    st.title("Fund Performance & Scorecard")
    scorecard = load_scorecard()
    
    # Filters
    st.sidebar.markdown("### Filters")
    category_filter = st.sidebar.selectbox("Select Category", ["All", "Equity", "Debt", "Hybrid"])
    
    # Load basic details
    dim_fund = pd.read_sql("SELECT * FROM dim_fund", conn)
    merged = pd.merge(scorecard, dim_fund, on='scheme_name')
    
    if category_filter != "All":
        merged = merged[merged['category'] == category_filter]
        
    # Scatter Plot
    st.markdown("### Risk vs Return (Size = Expense Ratio)")
    fig = px.scatter(merged, x='Max_Drawdown', y='CAGR_3yr', size='expense_ratio_pct', 
                     color='category', hover_name='scheme_name',
                     labels={'Max_Drawdown': 'Max Drawdown (Risk)', 'CAGR_3yr': '3-Yr CAGR (Return)'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Sortable Table
    st.markdown("### Fund Scorecard")
    st.dataframe(merged[['scheme_name', 'category', 'Score', 'CAGR_3yr', 'Sharpe_Ratio', 'Alpha', 'Max_Drawdown']].sort_values('Score', ascending=False), use_container_width=True)

elif page == "Investor Analytics":
    st.title("Investor Analytics")
    
    demo_df = pd.read_sql("SELECT state, age_group, transaction_type, amount_inr, city_tier FROM fact_transactions", conn)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Transaction Type Split")
        trans_counts = demo_df.groupby('transaction_type')['amount_inr'].sum().reset_index()
        fig_donut = px.pie(trans_counts, values='amount_inr', names='transaction_type', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col2:
        st.markdown("### Avg SIP by Age Group")
        sip_df = demo_df[demo_df['transaction_type'] == 'SIP']
        age_sip = sip_df.groupby('age_group')['amount_inr'].mean().reset_index()
        fig_bar = px.bar(age_sip, x='age_group', y='amount_inr', color='age_group')
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.markdown("### SIP Inflows by State")
    state_sip = sip_df.groupby('state')['amount_inr'].sum().reset_index().sort_values('amount_inr', ascending=False).head(15)
    fig_state = px.bar(state_sip, y='state', x='amount_inr', orientation='h', color='amount_inr', color_continuous_scale='teal')
    st.plotly_chart(fig_state, use_container_width=True)

elif page == "SIP & Market Trends":
    st.title("SIP & Market Trends")
    
    st.markdown("### Monthly SIP Inflows vs Nifty 50")
    
    # Fetch SIP
    sip_trend = pd.read_sql("""
        SELECT substr(transaction_date, 1, 7) as month, SUM(amount_inr) as total_sip 
        FROM fact_transactions 
        WHERE transaction_type='SIP' 
        GROUP BY month 
        ORDER BY month
    """, conn)
    
    # Fetch Nifty
    benchmarks = load_benchmarks()
    nifty = benchmarks[benchmarks['index_name'] == 'NIFTY50'].copy()
    nifty['date'] = pd.to_datetime(nifty['date'])
    nifty['month'] = nifty['date'].dt.strftime('%Y-%m')
    nifty_monthly = nifty.groupby('month')['close_value'].last().reset_index()
    
    merged_trend = pd.merge(sip_trend, nifty_monthly, on='month', how='inner')
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(x=merged_trend['month'], y=merged_trend['total_sip'], name="SIP Inflows", marker_color='rgba(50, 171, 96, 0.6)'),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=merged_trend['month'], y=merged_trend['close_value'], name="Nifty 50", line=dict(color='red', width=2)),
        secondary_y=True,
    )
    
    fig.update_layout(title_text="Sticky Capital: SIPs vs Market Performance")
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="SIP Amount (INR)", secondary_y=False)
    fig.update_yaxes(title_text="Nifty 50 Level", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Category Inflow Heatmap")
    cat_inflow = pd.read_sql("""
        SELECT substr(t.transaction_date, 1, 7) as month_year, f.category, SUM(t.amount_inr) as net_inflow
        FROM fact_transactions t
        JOIN dim_fund f ON t.amfi_code = f.amfi_code
        GROUP BY month_year, f.category
    """, conn)
    heatmap_data = cat_inflow.pivot(index='category', columns='month_year', values='net_inflow').fillna(0)
    
    fig_heat = px.imshow(heatmap_data, color_continuous_scale='YlGnBu', aspect="auto")
    st.plotly_chart(fig_heat, use_container_width=True)
