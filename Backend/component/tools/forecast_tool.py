from typing import Dict, Union
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field

from component.stock_prediction import predict_stock_prices

load_dotenv()


class ForecastInput(BaseModel):
    ticker: str = Field(..., description="The stock ticker to forecast prices for (e.g., AAPL).")
    days: int = Field(default=7, description="Number of future days to predict (default: 7).")


@tool("forecast_prices", args_schema=ForecastInput, return_direct=True)
def forecast_prices(ticker: str, days: int = 7) -> Union[Dict, str]:
    """
    Predict the next N days of stock prices using the Prophet model and historical data from Financial Datasets API.
    """
    try:
        result = predict_stock_prices(ticker, days)

        if not result.forecast or result.forecast[0]["ds"] is None:
            return {
                "ticker": result.ticker,
                "forecast": [],
                "error": result.forecast[0].get("error", "Unknown error during forecasting")
            }

        return {
            "ticker": result.ticker,
            "forecast": result.forecast
        }

    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "forecast": [],
            "error": str(e)
        }
