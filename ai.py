import os #to react with api keys
import requests #access the internet and let the code talk to gemini
from dotenv import load_dotenv #to acces the .env file with all the API's and their keys

# Load up environment variables.
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def generate_explanation(ticker, company, risk, components):
    #try to get the gemini response first, then move on to the manual explanation incase of any errors
    prompt = build_prompt(ticker, company, risk, components)
    response = run_gemini(prompt)
    if response:
        return response
    return rule_based_explanation(company, risk, components)

#gemini logic

def find_working_model():
    #finds a usable gemini model
    try:
        BASE_URL = f"{BASE_URL}/models?key={GEMINI_API_KEY}"
        r = requests.get(BASE_URL, timeout=15)
        data = r.json()

        for model in data.get("models", []):
            methods = model.get("supportedGenerationMethods", [])
            name = model.get("name", "")
            if "generateContent" in methods:
                #from previous testing, the api returns model/gemini-pro, this extracts the gemini-pro part
                return name.replace("models/", "")
    except Exception:
        #incase we are unable to get the gemini-pro model, we use the next best model, very unlikey to happen just a fail-safe
        pass

    return None


def run_gemini(prompt: str):
    #execting the geminin prompt with a timeout feature to prevent hanging
    model = find_working_model()
    print('Attempting AI Response...') 
    
    if not model:
        return None
    # we are forming the link that gemini needs to get the answer, gemini needs it in a specific json format
    try:
        BASE_URL = f"{BASE_URL}/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        r = requests.post(BASE_URL, json=payload, timeout=20)
        data = r.json()
        #checks api rerros
        if "error" in data:
            return None

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception:
        return None



def build_prompt(ticker, company, risk, components):

    return f"""
You are a senior financial risk analyst reviewing a stock using multiple independent data sources.

Company: {company} ({ticker})

Overall Risk Classification:
-Risk Level: {risk['risk_level']}
-Risk Score: {risk['total_score']}

Component risk signals:
-Financial risk score: {components['financial']['score']}
-News risk score: {components['news']['score']}
-Market (macroeconomic) risk score: {components['market']['score']}
-Regulatory filings risk score: {components['filings']['score']}

Write a detailed explanation that:
1. Explains why the overall risk is classified as {risk['risk_level']}.
2. Connects cause → effect (why these factors increase or reduce risk).
3. Identifies reinforcing signals and contradictions.
4. Separates short-term risk from long-term risk.
5. Comments on reliability based on agreement between data sources.
6. Does NOT give investment advice or price predictions.

Write 2–3 structured paragraphs in a professional, analytical tone.
"""

#the safe fail system

def rule_based_explanation(company, risk, components):
    level = risk["risk_level"]
    explanation = (
        f"{company} is classified as **{level} risk** based on a structured, "
        f"multi-factor assessment that evaluates company fundamentals, news sentiment, "
        f"macroeconomic conditions, and regulatory disclosures.\n\n"
    )
    if components["financial"]["score"] > 0:
        explanation += (
            "From a fundamental perspective, valuation and balance-sheet indicators "
            "contribute to elevated risk. Higher valuation multiples increase sensitivity "
            "to earnings disappointments, while leverage can amplify downside exposure "
            "during unfavorable market conditions.\n\n"
        )
    else:
        explanation += (
            "Financial metrics do not currently indicate significant structural weakness, "
            "which helps stabilize the overall risk profile.\n\n"
        )
    #analyze news sentiment
    if components["news"]["score"] > 0:
        explanation += (
            "Recent news coverage introduces short-term uncertainty, as negative or "
            "cautionary headlines can influence market sentiment even when fundamentals "
            "remain stable.\n\n"
        )

    #analyze SEC
    if components["filings"]["score"] > 0:
        explanation += (
            "Recent SEC 8-K filings signal notable corporate events or disclosures. "
            "While not inherently negative, such filings are commonly associated with "
            "periods of heightened uncertainty and therefore raise near-term risk.\n\n"
        )

    #analyze interest rates and volatility
    if components["market"]["score"] > 0:
        explanation += (
            "Macroeconomic conditions, particularly elevated interest rates, add external "
            "pressure by increasing financing costs and compressing equity valuations.\n\n"
        )
    #conculion
    explanation += (
        "Overall, this assessment is considered **moderately reliable** because multiple "
        "independent data sources point in a similar direction. This tool is intended for "
        "**educational purposes only** and does not provide investment advice."
    )

    print('Used Rule-Based Response (Fallback), This Feedback Is Generic')

    return explanation
