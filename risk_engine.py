def assess_financial_risk(yahoo_data: dict, fmp_data: dict):
    score = 0
    reasons = []

    pe = yahoo_data.get("pe_ratio")
    debt_equity = yahoo_data.get("debt_to_equity")

    # High valuation or Missing Earnings (Negative Earnings)
    if pe is None:
        score += 1
        reasons.append("P/E ratio unavailable (possible negative earnings)")
    elif pe > 30:
        score += 2
        reasons.append("High valuation (P/E ratio above 30)")

    # High leverage
    if debt_equity and debt_equity > 150:
        score += 2
        reasons.append("High debt-to-equity ratio")

    # Cross-check with FMP
    roe = fmp_data.get("roe")
    if roe is not None and roe < 0:
        score += 1
        reasons.append("Negative return on equity")

    return {
        "score": score,
        "reasons": reasons
    }


def assess_news_risk(news: list):
    score = 0
    reasons = []

    if not news:
        return {"score": 0, "reasons": []}

    # Expanded keyword list to catch general market sentiment, not just crimes
    negative_keywords = [
        "lawsuit", "investigation", "fraud", "recall",
        "layoffs", "probe", "antitrust", "bankruptcy",
        "drop", "fall", "decline", "plunge", "tumble", # Price action
        "miss", "weak", "disappoint", "lower", "cut",  # Earnings
        "downgrade", "sell", "bearish", "risk", "concern" # Analyst sentiment
    ]

    hits = 0
    for article in news:
        title = article.get("title", "").lower()
        if any(word in title for word in negative_keywords):
            hits += 1

    if hits >= 3:
        score += 2
        reasons.append("Multiple negative news events detected")
    elif hits > 0:
        score += 1
        reasons.append("Some negative news coverage detected")

    return {
        "score": score,
        "reasons": reasons
    }


def assess_market_risk(interest_rate):
    score = 0
    reasons = []

    if interest_rate and interest_rate > 4.5:
        score += 1
        reasons.append("High interest rate environment")

    return {
        "score": score,
        "reasons": reasons
    }


def assess_filing_risk(filings: list):
    score = 0
    reasons = []

    if filings:
        score += 2
        reasons.append("Recent 8-K regulatory filings detected")

    return {
        "score": score,
        "reasons": reasons
    }


def combine_risks(financial, news, market, filings):
    total_score = (
        financial["score"]
        + news["score"]
        + market["score"]
        + filings["score"]
    )

    reasons = (
        financial["reasons"]
        + news["reasons"]
        + market["reasons"]
        + filings["reasons"]
    )

    if total_score <= 2:
        level = "Low"
    elif total_score <= 5:
        level = "Medium"
    else:
        level = "High"

    return {
        "risk_level": level,
        "total_score": total_score,
        "reasons": reasons
    }
