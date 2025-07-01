from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from typing import Dict, Union
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()
import os   

class TavilySearchInput(BaseModel):
    query: str = Field(..., description="The search query you want to execute with Tavily.")
    search_depth: Optional[str] = Field(
        default="basic",
        description="The depth of the search. It can be 'basic' or 'advanced'."
    )
    topic: Optional[str] = Field(
        default="general",
        description="The category of the search. Currently supports 'general' and 'news'."
    )
    days: Optional[int] = Field(
        default=3,
        description="The number of days back from the current date to include in the search results. Only available for 'news' topic."
    )
    max_results: Optional[int] = Field(
        default=5,
        description="The maximum number of search results to return."
    )
    include_images: Optional[bool] = Field(
        default=False,
        description="Include a list of query-related images in the response."
    )
    include_image_descriptions: Optional[bool] = Field(
        default=False,
        description="When include_images is True, adds descriptive text for each image."
    )
    include_answer: Optional[bool] = Field(
        default=False,
        description="Include a short answer to original query."
    )
    include_raw_content: Optional[bool] = Field(
        default=False,
        description="Include the cleaned and parsed HTML content of each search result."
    )
    include_domains: Optional[List[str]] = Field(
        default=[],
        description="A list of domains to specifically include in the search results."
    )
    exclude_domains: Optional[List[str]] = Field(
        default=[],
        description="A list of domains to specifically exclude from the search results."
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "Latest advancements in AI",
                "api_key": "your-api-key-here",
                "search_depth": "advanced",
                "topic": "news",
                "days": 7,
                "max_results": 10,
                "include_images": True,
                "include_image_descriptions": True,
                "include_answer": True,
                "include_raw_content": False,
                "include_domains": ["techcrunch.com", "wired.com"],
                "exclude_domains": ["example.com"]
            }
        }



@tool("search-web", args_schema=TavilySearchInput, return_direct=True)
def search_web(
    query: str,
    search_depth: str = "basic",
    topic: str = "general",
    days: int = 3,
    max_results: int = 3,
    include_images: bool = False,
    include_answer: bool = False,
    include_raw_content: bool = False,
    include_domains: list = None,
    exclude_domains: list = None
) -> Union[Dict, str]:
    """
    Perform a web search using the Tavily API.

    This tool accesses real-time web data, news, articles and should be used when up-to-date information from the internet is required.
    """
    TAVILY_BASE_URL = "https://api.tavily.com"

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("Missing TAVILY_API_KEY in environment variables.")

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": search_depth,
        "topic": topic,
        "days": days if topic == "news" else None,
        "max_results": max_results,
        "include_images": include_images,
        "include_answer": include_answer,
        "include_raw_content": include_raw_content
    }

    if include_domains:
        payload["include_domains"] = include_domains
    if exclude_domains:
        payload["exclude_domains"] = exclude_domains

    try:
        response = requests.post(
            f"{TAVILY_BASE_URL}/search",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Example usage of the tool
    search_web("Latest advancements in AI")