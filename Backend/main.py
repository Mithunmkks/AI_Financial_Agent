from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from component.stock_analysis import ask_agent
from component.sentiment_analysis import analyze_stock_news
from component.recommendation import ask_portfolio_agent
from pydantic import BaseModel

app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}


# Request Models
class ChatRequest(BaseModel):
    message: str

class SentimentRequest(BaseModel):
    ticker: str


class Stock(BaseModel):
    ticker: str
    buy_price: float
    quantity: int

class PortfolioRequest(BaseModel):
    portfolio: list[Stock]


# Routes
@app.post("/chat")
def chat_with_agent(req: ChatRequest):
    try:
        response = ask_agent(req.message)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

@app.post("/sentiment")
def get_sentiment(req: SentimentRequest):
    try:
        results = analyze_stock_news(req.ticker)
        return results
    except Exception as e:
        return {"error": str(e)}


@app.post("/portfolio/recommendation")
def portfolio_recommendation(req: PortfolioRequest):
    try:
        result = ask_portfolio_agent(req.dict())
        return {"recommendation": result}
    except Exception as e:
        return {"error": str(e)}






