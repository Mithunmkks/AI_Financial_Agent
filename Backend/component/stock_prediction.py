import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv
from prophet import Prophet
from pydantic import BaseModel

# Load API key
load_dotenv()
API_KEY = os.getenv("FINANCIAL_DATASETS_API_KEY")

# Base API settings
BASE_URL = "https://api.financialdatasets.ai/prices"
INTERVAL = "day"
INTERVAL_MULTIPLIER = 1
DEFAULT_PERIOD = "3mo"  # Used to calculate start_date

# Output schema
class ForecastResult(BaseModel):
    ticker: str
    forecast: list[dict]  # Each dict = {ds, yhat, yhat_lower, yhat_upper}


def fetch_stock_history(ticker: str, start_date: str, end_date: str):
    headers = {"X-API-KEY": API_KEY}
    params = {
        "ticker": ticker,
        "interval": INTERVAL,
        "interval_multiplier": INTERVAL_MULTIPLIER,
        "start_date": start_date,
        "end_date": end_date,
        "limit": 5000
    }

    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code != 200:
        raise ValueError(f"API error: {response.status_code} - {response.text}")
    
    data = response.json().get("prices", [])
    if not data:
        raise ValueError("No data returned from Financial Datasets API")

    df = pd.DataFrame(data)
    df["ds"] = pd.to_datetime(df["time"]).dt.tz_localize(None)  # ✅ remove timezone
    df["y"] = df["close"]
    return df[["ds", "y"]]


def generate_forecast(df: pd.DataFrame, periods: int = 7):
    model = Prophet(daily_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)


def predict_stock_prices(ticker: str, days: int = 7) -> ForecastResult:
    try:
        # Compute date range
        end_date = pd.Timestamp.today().date().strftime("%Y-%m-%d")
        start_date = (pd.Timestamp.today() - pd.Timedelta("180D")).date().strftime("%Y-%m-%d")

        df = fetch_stock_history(ticker, start_date, end_date)
        forecast_df = generate_forecast(df, periods=days)
        forecast_df["ds"] = forecast_df["ds"].dt.strftime("%Y-%m-%d")


        # ✅ Convert 'ds' column from Timestamp to string for JSON safety
        forecast_df["ds"] = forecast_df["ds"].astype(str)
        forecast_json = forecast_df.to_dict(orient="records")

        return ForecastResult(ticker=ticker.upper(), forecast=forecast_json)

    except Exception as e:
        return ForecastResult(ticker=ticker.upper(), forecast=[
            {
                "ds": None,
                "yhat": None,
                "yhat_lower": None,
                "yhat_upper": None,
                "error": str(e)
            }
        ])


# For direct testing
if __name__ == "__main__":
    result = predict_stock_prices("AAPL", 7)  # Fixed 7-day forecast
    print(json.dumps(result.model_dump(), indent=2))  # ✅ Pydantic v2 compatible
