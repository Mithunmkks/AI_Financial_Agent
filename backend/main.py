from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.component.stock_analysis import ask_agent
from backend.component.sentiment_analysis import analyze_stock_news
from pydantic import BaseModel

app = FastAPI()
# Allow frontend to connect (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Root route (health check)
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

# Request models
class ChatRequest(BaseModel):
    message: str

class SentimentRequest(BaseModel):
    query: str

class PredictRequest(BaseModel):
    ticker: str

@app.post("/chat")
def chat_with_agent(req: ChatRequest):
    try:
        response = ask_agent(req.message)  # ✅ Call real agent here
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

# --- 2. Market Sentiment ---
@app.post("/sentiment")
def get_sentiment(req: SentimentRequest):
    try:
        results = analyze_stock_news(req.query)
        return {"sentiment_analysis": results}
    except Exception as e:
        return {"error": str(e)}

# --- 3. Prediction ---
@app.post("/predict")
def get_prediction(req: PredictRequest):
    # Dummy prediction logic
    prediction = "📈 Buy" if req.ticker.upper() in ["AAPL", "TSLA"] else "📉 Hold"
    return {"ticker": req.ticker.upper(), "prediction": prediction}
