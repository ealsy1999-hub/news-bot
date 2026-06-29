import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_news(title, description, source):
    content = description.strip() if description and len(description.strip()) > 50 else ""

    if content:
        prompt = f"""Summarize this news article in 4-5 sentences in English.
Include: what happened, why it matters, key numbers or facts if any, and potential impact.
Be informative and analytical. Do NOT ask for more information - just summarize what you have.

Source: {source}
Title: {title}
Content: {content[:800]}

Summary:"""
    else:
        prompt = f"""Write a 3-4 sentence analytical commentary in English about this news headline.
Explain what this likely means, why it matters economically or politically, and potential impact.
Do NOT say you need more information - just analyze the headline as given.

Headline: {title}

Analysis:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "⚠️ Summary unavailable."

def categorize(title):
    t = title.lower()
    if any(w in t for w in ["oil","gas","opec","energy","lng","brent","crude","barrel","nuclear","solar","wind"]):
        return "⚡ Energy"
    elif any(w in t for w in ["market","stock","fed","rate","inflation","gdp","economy","dollar","euro","trade","productivity","labor","jobless","claims"]):
        return "📈 Markets"
    elif any(w in t for w in ["war","sanction","nato","china","russia","iran","deal","treaty","geopolit","military","conflict"]):
        return "🌍 Geopolitics"
    elif any(w in t for w in ["real estate","property","housing","mortgage","realt"]):
        return "🏠 Real Estate"
    else:
        return "📰 General"
