import os
import requests
from typing import Dict, Union
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class GetPricesInput(BaseModel):
    """
    Pydantic model defining input parameters for the get_prices function.
    This model validates the inputs and provides descriptive metadata.
    """
    ticker: str = Field(..., description="The ticker of the stock.")
    start_date: str = Field(
        ..., 
        description="The start of the price time window. Format: YYYY-MM-DD or millisecond timestamp."
    )
    end_date: str = Field(
        ..., 
        description="The end of the price time window. Format: YYYY-MM-DD or millisecond timestamp."
    )
    interval: str = Field(
        default="day",
        description=(
            "The time interval for prices. Valid values: 'second', 'minute', 'day', 'week', "
            "'month', 'quarter', 'year'."
        ),
    )
    interval_multiplier: int = Field(
        default=1,
        description=(
            "Multiplier for the interval. E.g., interval='day' and interval_multiplier=1 means daily prices; "
            "interval='minute' and interval_multiplier=5 means prices every 5 minutes."
        ),
    )
    limit: int = Field(
        default=5000,
        description="Max number of prices to return. Default is 5000, max is 50000.",
    )


def get_prices(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str,
    interval_multiplier: int = 1,
    limit: int = 5000
) -> Union[Dict, str]:
    """
    Fetch historical price data for a specified stock ticker over a given date range and interval.

    Parameters:
        ticker (str): The stock symbol (e.g., "AAPL").
        start_date (str): Start date or timestamp for the price data.
        end_date (str): End date or timestamp for the price data.
        interval (str): Time interval for the price data (e.g., 'day', 'minute').
        interval_multiplier (int): Multiplier for the interval to aggregate data.
        limit (int): Maximum number of data points to return.

    Returns:
        Dict or str: JSON response containing price data or error information.
    """
    
    # Retrieve API key from environment variable
    api_key = os.environ.get("FINANCIAL_DATASETS_API_KEY")
    if not api_key:
        raise ValueError("Missing FINANCIAL_DATASETS_API_KEY.")

    # Construct the request URL with query parameters
    url = (
        f"https://api.financialdatasets.ai/prices"
        f"?ticker={ticker}"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
        f"&interval={interval}"
        f"&interval_multiplier={interval_multiplier}"
        f"&limit={limit}"
    )

    try:
        # Send GET request with API key in headers
        response = requests.get(url, headers={'X-API-Key': api_key})
        response.raise_for_status()  # Raises error for HTTP status >= 400

        # Parse and return JSON data
        data = response.json()
        return data

    except Exception as e:
        # Return a dict with error details instead of raising
        return {"ticker": ticker, "prices": [], "error": str(e)}


if __name__ == "__main__":
    # Example usage for testing the function
    result = get_prices(
        ticker="AAPL",
        start_date="2023-01-01",
        end_date="2023-01-10",
        interval="day",
        interval_multiplier=1,
        limit=10
    )
    print(result)
