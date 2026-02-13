from data_sources import (
    fetch_yahoo_data,
    fetch_alpha_vantage_volatility,
    fetch_fmp_metrics,
    fetch_gnews,
    fetch_google_news_rss,
    fetch_recent_filings,
    fetch_interest_rate,
)

from risk_engine import (
    assess_financial_risk, #looks at the yahoo data to see if the company is going broke
    assess_news_risk, #reads the news and sees if the company or its investors and panicking
    assess_market_risk, #looks at the current interest rates
    assess_filing_risk, #checks for any issues in legal documents
    combine_risks, #takes the four previous checks and merges it into one for for final grade
)

from utils import get_company_info #to get the company name from the sticker name
from ai import generate_explanation


def run_analysis(ticker: str):

    # Resolve company info
    company_name, cik, sec_status = get_company_info(ticker)

    if not company_name or not cik:
        return {"error": sec_status}

    #getting the data
    yahoo_data = fetch_yahoo_data(ticker)

    av_volatility = fetch_alpha_vantage_volatility(ticker)
    volatility = av_volatility or yahoo_data.get("yahoo_volatility")
    volatility_source = (
        "Alpha Vantage" if av_volatility else "Yahoo Finance"
    )

    yahoo_data["volatility"] = volatility
    yahoo_data["volatility_source"] = volatility_source

    fmp_data = fetch_fmp_metrics(ticker)

    news_gnews = fetch_gnews(company_name)
    news_rss = fetch_google_news_rss(company_name)
    all_news = news_gnews + news_rss

    filings = fetch_recent_filings(cik)
    interest_rate = fetch_interest_rate()

   #assesin all the risks
    financial_risk = assess_financial_risk(yahoo_data, fmp_data)
    news_risk = assess_news_risk(all_news)
    market_risk = assess_market_risk(interest_rate)
    filing_risk = assess_filing_risk(filings)

    final_risk = combine_risks(
        financial_risk,
        news_risk,
        market_risk,
        filing_risk
    )

    #the ai explanetions using all the data fetched
    explanation = generate_explanation(
        ticker=ticker,
        company=company_name,
        risk=final_risk,
        components={
            "financial": financial_risk,
            "news": news_risk,
            "market": market_risk,
            "filings": filing_risk
        }
    )

    return {
        "ticker": ticker,
        "company_name": company_name,
        "stock_data": yahoo_data,
        "risk": final_risk,
        "risk_components": {
            "Financial": financial_risk["score"],
            "News": news_risk["score"],
            "Market": market_risk["score"],
            "Filings": filing_risk["score"],
        },
        "news": all_news,
        "filings": filings,
        "explanation": explanation,
    }
