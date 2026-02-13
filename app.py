import streamlit as st

st.set_page_config(
    page_title="Stock Risk Analyzer",
    layout="wide"
)

st.title("Stock Risk Analyzer")
st.caption(
    "Multi-source, explainable stock risk assessment "
    "(financials, news, macro, and regulatory filings)"
)

# USER INPUT
ticker = st.text_input(
    "Enter a US stock ticker (e.g. AAPL, MSFT, NVDA)",
    placeholder="AAPL"
).upper()

#analyse btn
st.button("Analyze")

#risk_score
st.caption("SEC Data Source: ")

col1, col2 = st.columns(2)
col1.metric("Overall Risk Level","NA")
col2.metric("Risk Score","NA / 10")

#explanation
st.subheader("Risk Explanation")

#Risk breakdown chart
st.subheader("Risk Breakdown")\

#metrics
st.subheader("Key Financial Metrics")

metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

metrics_col1.metric(
    "Current Price",
    "NA"
)
metrics_col2.metric(
    "P/E Ratio",
    "NA"
)
metrics_col3.metric(
    "Debt-to-Equity",
    "NA"
)

#volatility
st.subheader("Volatility")

#price history
st.subheader("Price History (1 Year)")

#news
st.subheader("Recent News")

#8-K filings
st.subheader("Recent SEC 8-K Filings")

#disclaimer
st.markdown("---")
st.markdown(
    """
**Disclaimer**

This application is a student-built analytical tool intended for **educational purposes only**.

- The analysis is based on a limited subset of publicly available data.
- Data may be incomplete, delayed, or unavailable due to third-party API limitations.
- Risk scores are simplified models and do not capture all real-world factors.
- AI-generated explanations may contain inaccuracies.

**This tool does NOT provide investment, financial, or legal advice.**
Do not make investment decisions based solely on this application.
"""
)
