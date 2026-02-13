import requests
import streamlit as st

SEC_TICKER_URL = "https://www.sec.gov/files/company_tickers.json"

HEADERS = {
    "User-Agent": "StockRiskAnalyzer/1.0 (contact: hackathon@student.edu)",
    "Accept-Encoding": "gzip, deflate",
}

# Minimal fallback to guarantee demos
KNOWN_TICKERS = {
    "AAPL": ("Apple Inc.", "0000320193"),
    "AMZN": ("Amazon.com, Inc.", "0001018724"),
    "MSFT": ("Microsoft Corporation", "0000789019"),
    "NVDA": ("NVIDIA Corporation", "0001045810"),
}


@st.cache_data(show_spinner=False)
def load_sec_ticker_map():
    try:
        r = requests.get(SEC_TICKER_URL, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def get_company_info(ticker: str):
    ticker = ticker.upper().strip()

    data = load_sec_ticker_map()
    if data:
        for item in data.values():
            if item.get("ticker", "").upper() == ticker:
                cik = str(item["cik_str"]).zfill(10)
                return item["title"], cik, "SEC Live"

    if ticker in KNOWN_TICKERS:
        name, cik = KNOWN_TICKERS[ticker]
        return name, cik, "SEC Fallback"

    return None, None, "Not Found"
