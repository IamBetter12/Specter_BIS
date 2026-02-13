import os
import requests
import feedparser
import yfinance as yf
import numpy as np
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# Use UPPERCASE to match your .env file
ALPHA_VANTAGE_KEY = os.getenv("alpha_vantage")
FMP_KEY = os.getenv("fmp")
GNEWS_KEY = os.getenv("gnews")
FRED_KEY = os.getenv("fred")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_yahoo_data(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        current_price = stock.fast_info.last_price 
        if not current_price:
            current_price = stock.info.get("currentPrice")

        hist = stock.history(period="1y")
        price_history = hist["Close"].dropna()

        yahoo_volatility = 0.0
        if len(price_history) > 1:
            returns = price_history.pct_change().dropna()
            yahoo_volatility = float(np.std(returns) * np.sqrt(252))

        # Get PE ratio with fallback
        pe = stock.info.get("trailingPE")
        if pe is None:
            pe = stock.info.get("forwardPE")

        return {
            "current_price": round(current_price, 2) if current_price else None,
            "pe_ratio": pe,
            "debt_to_equity": stock.info.get("debtToEquity"),
            "yahoo_volatility": yahoo_volatility,
            "price_history": price_history.to_dict() # Added price_history to return for chart
        }
    except Exception as e:
        print(f"Yahoo Error: {e}")
        return {}

def fetch_alpha_vantage_volatility(ticker: str):
    if not ALPHA_VANTAGE_KEY:
        return None
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        prices = [float(v["4. close"]) for v in data.get("Time Series (Daily)", {}).values()]
        if len(prices) < 2: return None
        returns = np.diff(prices) / prices[:-1]
        return float(np.std(returns) * np.sqrt(252))
    except Exception:
        return None

def fetch_fmp_metrics(ticker: str):
    if not FMP_KEY:
        return {}
    url = f"https://financialmodelingprep.com/api/v3/key-metrics/{ticker}?apikey={FMP_KEY}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return data[0] if isinstance(data, list) and data else {}
    except Exception:
        return {}

def fetch_gnews(company_name: str):
    if not GNEWS_KEY:
        return []
    url = f"https://gnews.io/api/v4/search?q={quote_plus(company_name)}&lang=en&token={GNEWS_KEY}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return []
        data = r.json()
        return [{"title": a["title"], "url": a["url"], "source": a["source"]["name"]} for a in data.get("articles", [])[:3]]
    except Exception:
        return []

def fetch_google_news_rss(company_name: str):
    query = quote_plus(company_name)
    feed_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    try:
        response = requests.get(feed_url, headers=HEADERS, timeout=10)
        feed = feedparser.parse(response.content)
        return [{"title": e.title, "url": e.link, "source": "Google News"} for e in feed.entries[:3]]
    except Exception:
        return []

def fetch_recent_filings(cik: str):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200: return []
        data = r.json()
        recent = data.get("filings", {}).get("recent", {})
        filings = []
        for form, date in zip(recent.get("form", []), recent.get("filingDate", [])):
            if form in ["8-K", "10-K", "10-Q"]:
                filings.append({"form": form, "date": date})
        return filings[:5]
    except Exception:
        return []

def fetch_interest_rate():
    if not FRED_KEY: return 4.5 # Default fallback
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=FEDFUNDS&api_key={FRED_KEY}&file_type=json"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return float(data["observations"][-1]["value"])
    except Exception:
        return 4.5
