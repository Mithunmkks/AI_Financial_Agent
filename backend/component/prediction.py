from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, openai_api_key=OPENAI_API_KEY)

# Prompt template
template = """
You are a financial analyst AI. Your task is to predict a stock's price 7 days from now using current sentiment data.

Stock: {stock_name}
Current Price: ${current_price}

Sentiment Info:
- Sentiment: {sentiment}
- Sentiment Score: {sentiment_score}
- Impact Score: {impact_score}
- Reasoning: {reasoning}

Based on this, output a JSON object like:
{{
  "predicted_price": float,
  "confidence_level": "low | medium | high",
  "reasoning": "your explanation here"
}}
"""

prompt = ChatPromptTemplate.from_template(template)

def predict_stock_price(stock_name, current_price, sentiment_data):
    formatted_prompt = prompt.format_messages(
        stock_name=stock_name,
        current_price=current_price,
        sentiment=sentiment_data["sentiment"],
        sentiment_score=sentiment_data["sentiment_score"],
        impact_score=sentiment_data["impact_score"],
        reasoning=sentiment_data["reasoning"]
    )
    
    response = llm.invoke(formatted_prompt)
    
    try:
        result = json.loads(response.content)
        return result
    except json.JSONDecodeError:
        raise ValueError("LLM response was not valid JSON:\n" + response.content)

# Example usage
if __name__ == "__main__":
    sentiment_data = {
        "sentiment": "Positive",
        "sentiment_score": 0.85,
        "impact_score": 0.7,
        "reasoning": "The company released a strong earnings report with better-than-expected revenue."
    }
    stock_name = "Apple Inc"
    current_price = 185.32

    prediction = predict_stock_price(stock_name, current_price, sentiment_data)
    print(json.dumps(prediction, indent=2))
