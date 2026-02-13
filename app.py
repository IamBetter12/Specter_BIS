import streamlit as st #used for turning python into websites easily
import pandas as pd #used for data manipulation
import plotly.express as px #used for prccesing the graphs and pie charts
from analysis import run_analysis #returns the analysis from analysis.py so that it can be displayed on streamlit

#starting the page using streamlit
st.set_page_config(
    page_title="Stock Risk Analyzer",
    layout="wide"
)

st.title("Stock Risk Analyzer")
st.caption(
    "Multi-source, explainable stock risk assessment "
    "(financials, news, macro, and regulatory filings)"
)
#the user input
ticker = st.text_input(
    "Enter a US stock ticker (e.g. AAPL, MSFT, NVDA)",
    placeholder="AAPL"
).upper()
#runing analysis
if st.button("Analyze"):
    with st.spinner("Running analysis..."):
        result = run_analysis(ticker)

    if "error" in result:
        st.error(result["error"])
        st.stop()
    #header summmary
    st.caption(f"SEC Data Source: {result.get('sec_status')}")

    st.subheader(f"{result['company_name']} ({result['ticker']})")
    col1, col2 = st.columns(2)
    col1.metric("Overall Risk Level", result["risk"]["risk_level"])
    col2.metric("Risk Score", f"{result['risk']['total_score']} / 10")
    #explanaiton
    st.subheader("Risk Explanation")
    st.write(result["explanation"])
    #risk breakdown chart
    st.subheader("Risk Breakdown")

    components = result.get("risk_components", {})
    if components and sum(components.values()) > 0:
        df_risk = pd.DataFrame({
            "Risk Category": components.keys(),
            "Score": components.values()
        })

        fig = px.pie(
            df_risk,
            names="Risk Category",
            values="Score",
            title="Contribution to Overall Risk",
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No significant risk contributions detected.")

    #dashboard scorecard
    st.subheader("Key Financial Metrics")

    stock = result["stock_data"]

    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

    metrics_col1.metric(
        "Current Price",
        f"${stock.get('current_price', 'N/A')}"
    )
    metrics_col2.metric(
        "P/E Ratio",
        stock.get("pe_ratio", "N/A")
    )
    metrics_col3.metric(
        "Debt-to-Equity",
        stock.get("debt_to_equity", "N/A")
    )

    #prints the volatility
    st.subheader("Volatility")

    volatility = stock.get("volatility")
    source = stock.get("volatility_source")

    if volatility is not None:
        st.write(f"Annualized volatility: **{volatility:.4f}**")
        st.caption(f"Source: {source}")
    else:
        st.info("Volatility data unavailable.")

    #price history
    st.subheader("Price History (1 Year)")

    price_history = stock.get("price_history")

    if price_history:
        df_price = pd.DataFrame(
            price_history.items(),
            columns=["Date", "Price"]
        )
        df_price["Date"] = pd.to_datetime(df_price["Date"])

        fig_price = px.line(
            df_price,
            x="Date",
            y="Price",
            title="Closing Price"
        )
        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.info("Price history unavailable.")

    #news
    st.subheader("Recent News")

    news = result.get("news", [])
    if news:
        for article in news[:5]:
            st.markdown(f"- [{article['title']}]({article['url']})")
    else:
        st.info("No recent news found.")

    #reporting any filings
    st.subheader("Recent SEC 8-K Filings")

    filings = result.get("filings", [])
    if filings:
        for f in filings[:3]:
            st.write(f"- {f['form']} filed on {f['date']}")
    else:
        st.info("No recent 8-K filings detected.")

    #final disclaimer
    st.markdown("---")
    st.markdown(
        """
**Disclaimer**

This application is a student-built analytical tool intended for **educational purposes only**

- The analysis is based on a limited subset of publicly available data.
- Risk scores are simplified models and do not capture all real-world factors.

**This tool does NOT provide investment, financial, or legal advice.**
Do not make investment decisions based solely on this application.
"""
    )
