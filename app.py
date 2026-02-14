import streamlit as st #used for turning python into websites easily
import pandas as pd #used for data manipulation
import plotly.express as px #used for prccesing the graphs and pie charts
import plotly.graph_objects as go
from analysis import run_analysis #returns the analysis from analysis.py so that it can be displayed on streamlit

#starting the page using streamlit
st.set_page_config(
    page_title="Specter Risk Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
# FIX: Adjusted padding and added specific alignment classes
st.markdown("""
    <style>
        .block-container {
            padding-top: 3.5rem; 
            padding-bottom: 0rem;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
        /* Custom class for aligning risk metrics */
        .risk-metric {
            font-size: 40px !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
        }
        .risk-label {
            font-size: 14px !important;
            font-weight: 600 !important;
            color: #8b949e !important;
            margin-bottom: 5px !important;
        }
    </style>
""", unsafe_allow_html=True)

#sidebar
with st.sidebar:
    st.title("🛡️ Specter Risk Analyzer")
    st.caption("Financial Intelligence Tool")
    
    #the user input
    ticker = st.text_input(
        "Stock Ticker",
        placeholder="AAPL",
    ).upper()
    
    analyze_btn = st.button("Analyze Stock", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("### About")
    st.info(
        "This tool analyzes stocks using 4 data sources: \n"
        "1. Financials (Yahoo/FMP)\n"
        "2. News Sentiment (GNews)\n"
        "3. Macro Data (FRED)\n"
        "4. Legal Filings (SEC)"
    )
    st.caption("Made by Ayan Das and Harshvardhan Dhami")

#main page

if analyze_btn or ticker:
    if not ticker:
        st.warning("Please enter a ticker symbol.")
        st.stop()
        
    with st.spinner(f"Analyzing {ticker}..."):
        result = run_analysis(ticker)

    if "error" in result:
        st.error(result["error"])
        st.stop()

    #header and score
    with st.container():
        st.subheader(f"{result['company_name']} ({result['ticker']})")
        
        # Risk Badge Logic
        risk_level = result["risk"]["risk_level"]
        if risk_level == "High":
            risk_color_hex = "#ff4b4b" # Red
        elif risk_level == "Medium":
            risk_color_hex = "#ffa421" # Orange
        else:
            risk_color_hex = "#21c354" # Green
        
        col1, col2 = st.columns([1, 1])
        
        #the html for alignment
        with col1:
            st.markdown(f"""
                <div style="text-align: left;">
                    <p class="risk-label">RISK LEVEL</p>
                    <p class="risk-metric" style="color: {risk_color_hex};">{risk_level}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div style="text-align: left;">
                    <p class="risk-label">RISK SCORE</p>
                    <p class="risk-metric" style="color: {risk_color_hex};">{result['risk']['total_score']}/10</p>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    #ai explenation
    st.subheader("🤖 AI Risk Analysis")
    st.info(result["explanation"])

    #the visuals
    st.subheader("Risk Factors")
    
    components = result.get("risk_components", {})
    if components and sum(components.values()) > 0:
        df_risk = pd.DataFrame({
            "Risk Category": components.keys(),
            "Score": components.values()
        })
        
        #the donut chart
        fig = px.pie(
            df_risk,
            names="Risk Category",
            values="Score",
            hole=0.6,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        #the background
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            margin=dict(t=0, b=0, l=0, r=0),
            height=250
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No significant risk factors detected across any category.")

    st.divider()

    #key financials
    st.subheader("Key Financials")
    
    stock = result["stock_data"]
    
    #the colum layout
    m1, m2, m3 = st.columns(3)
    m1.metric("Price", f"${stock.get('current_price', 'N/A')}")
    m2.metric("P/E Ratio", stock.get('pe_ratio', 'N/A'))
    m3.metric("Debt/Equity", stock.get('debt_to_equity', 'N/A'))

    #the volatility
    vol = stock.get("yahoo_volatility", 0)
    st.caption(f"Annualized Volatility: {vol:.2f} (Source: {stock.get('volatility_source', 'Yahoo')})")

    #the price chart
    price_history = stock.get("price_history")
    if price_history:
        df_price = pd.DataFrame(price_history.items(), columns=["Date", "Price"])
        df_price["Date"] = pd.to_datetime(df_price["Date"])
        
        fig_price = px.area(
            df_price, x="Date", y="Price", 
            color_discrete_sequence=["#00e5ff"]
        )
        fig_price.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(showgrid=False),
            xaxis=dict(showgrid=False),
            margin=dict(t=10, b=10, l=0, r=0),
            height=200
        )
        st.plotly_chart(fig_price, use_container_width=True)

    #news filings tab
    st.subheader("Deep Dive")
    tab1, tab2 = st.tabs(["📰 Recent News", "⚖️ SEC Filings"])

    with tab1:
        news = result.get("news", [])
        if news:
            for article in news[:5]:
                with st.expander(f"{article['title']}"):
                    st.write(f"Source: {article.get('source', 'Unknown')}")
                    st.markdown(f"[Read Article]({article['url']})")
        else:
            st.info("No major news headlines found.")

    with tab2:
        filings = result.get("filings", [])
        if filings:
            for f in filings[:5]:
                st.write(f"**{f['form']}** filed on {f['date']}")
        else:
            st.info("No recent 8-K filings found.")

else:
    #Replaced unreadable st.info with a custom styled HTML card
    st.markdown("""
    <div style="
        background-color: #1e2129;
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 12px;
        text-align: left;
        margin-top: 20px;
    ">
        <h3 style="color: #00e5ff; margin: 0 0 10px 0;">Ready to Analyze</h3>
        <p style="color: #e6edf3; font-size: 16px; margin: 0;">
            👈 <b>Start here:</b> Enter a stock ticker (like AAPL or TSLA) in the sidebar on the left.
        </p>
    </div>
    """, unsafe_allow_html=True)
