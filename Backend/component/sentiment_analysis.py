import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

# Load environment variables from .env
load_dotenv()

# API keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI model via LangChain
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.2,
    api_key=OPENAI_API_KEY
)

# Fetch cleaned news
def fetch_clean_news(query, max_results=3, min_score=0.85):
    client = TavilyClient(TAVILY_API_KEY)
    response = client.search(
        query=query,
        topic="finance",
        search_depth="advanced",
        max_results=max_results,
        time_range="month",
        include_answer="advanced",
        include_raw_content=False
    )

    results = response.get("results", [])
    output = []

    for item in results:
        if item.get("score", 0) >= min_score:
            output.append({
                "url": item.get("url", ""),
                "title": item.get("title", "").strip(),
                "content": item.get("content", "").strip()
            })

    return output

# Analyze a single article
def get_sentiment_and_impact(news_item):
    prompt = f"""
Analyze the following financial news article and provide:
1. Sentiment: positive, negative, or neutral
2. Sentiment score (0.0 to 1.0)
3. Impact score (0.0 to 1.0)
4. A brief reasoning

News:
Title: {news_item['title']}
Content: {news_item['content']}

Respond in this JSON format:
{{
  "sentiment": "...",
  "sentiment_score": ...,
  "impact_score": ...,
  "reasoning": "..."
}}
"""
    try:
        response = llm.invoke([
            SystemMessage(content="You are a financial news sentiment and impact analysis model."),
            HumanMessage(content=prompt)
        ])
        result = json.loads(response.content)
        result["url"] = news_item["url"]
        return result

    except Exception as e:
        return {
            "url": news_item.get("url", ""),
            "sentiment": "unknown",
            "sentiment_score": 0.0,
            "impact_score": 0.0,
            "reasoning": f"Error during analysis: {str(e)}"
        }

# Summarize multiple reasoning strings
def summarize_reasonings(reasonings: list[str]) -> str:
    prompt = f"""
You are a financial analyst. Summarize the following reasoning statements into a single concise explanation of the overall sentiment and market impact:

{chr(10).join(f"- {r}" for r in reasonings)}

Respond in 2–3 sentences.
"""
    try:
        response = llm.invoke([
            SystemMessage(content="You are a financial news summarizer."),
            HumanMessage(content=prompt)
        ])
        return response.content.strip()
    except Exception as e:
        return "Summary unavailable due to an error."

# Final function
def analyze_stock_news(stock_name: str, max_results=3):
    query = f"{stock_name} stock news"
    news_items = fetch_clean_news(query=query, max_results=max_results)

    results = []
    for news in news_items:
        result = get_sentiment_and_impact(news)
        results.append(result)

    if not results:
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "impact_score": 0.0,
            "reasoning": "No valid articles found."
        }

    # Weighted average of sentiment_score and impact_score
    total_weight = sum(r["impact_score"] for r in results) or 1.0
    weighted_sentiment_score = sum(r["sentiment_score"] * r["impact_score"] for r in results) / total_weight
    average_impact_score = sum(r["impact_score"] for r in results) / len(results)

    # Determine dominant sentiment
    sentiments = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    for r in results:
        sentiments[r["sentiment"]] += r["impact_score"]

    final_sentiment = max(sentiments, key=sentiments.get)

    # Summarize all reasonings
    reasoning_summary = summarize_reasonings([r["reasoning"] for r in results])

    return {
        "sentiment": final_sentiment,
        "sentiment_score": round(weighted_sentiment_score, 3),
        "impact_score": round(average_impact_score, 3),
        "reasoning": reasoning_summary
    }

# For standalone test
if __name__ == "__main__":
    output = analyze_stock_news("Apple")
    print(json.dumps(output, indent=2))
