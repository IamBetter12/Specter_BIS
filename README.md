# Stock Risk Analyzer

A hackathon project that analyzes stock risk using multiple public data sources,
including market prices, financial ratios, news, macroeconomic indicators, and
regulatory filings.

The system generates an explainable risk score and highlights why a stock may
be considered low, medium, or high risk.

- This tool is for educational purposes only and does not provide investment advice.

## How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
