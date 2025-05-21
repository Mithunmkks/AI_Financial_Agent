import os
from typing import Dict, Union, Optional, List

import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Load environment variables elsewhere in your app, typically in main entry

class TavilySearchInput(BaseModel):
    query: str = Field(..., description="The search query you want to execute with Tavily.")
    search_depth: Optional[str] = Field(default="basic", description="The depth of the search. 'basic' or 'advanced'.")
    topic: Optional[str] = Field(default="general", description="Category of search. 'general' or 'news'.")
    days: Optional[int] = Field(default=3, description="Number of days back for news topic.")
    max_results: Optional[int] = Field(default=5, description="Max number of search results.")
    include_images: Optional[bool] = Field(default=False, description="Include images in response.")
    include_image_descriptions: Optional[bool] = Field(default=False, description="Add descriptions for images.")
    include_answer: Optional[bool] = Field(default=False, description="Include a concise answer.")
    include_raw_content: Optional[bool] = Field(default=False, description="Include raw HTML content.")
    include_domains: Optional[List[str]] = Field(default_factory=list, description="Domains to include.")
    exclude_domains: Optional[List[str]] = Field(default_factory=list, description="Domains to exclude.")

@tool("search-web", args_schema=TavilySearchInput, return_direct=True)
def search_web(
    query: str,
    search_depth: str = "basic",
    topic: str = "general",
    days: int = 3,
    max_results: int = 3,
    include_images: bool = False,
    include_image_descriptions: bool = False,
    include_answer: bool = False,
    include_raw_content: bool = False,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None
) -> Union[Dict, str]:
    """
    Perform a web search using the Tavily API.

    This tool accesses real-time web data, news, and articles,
    providing up-to-date information from the internet.
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
        "include_image_descriptions": include_image_descriptions,
        "include_answer": include_answer,
        "include_raw_content": include_raw_content,
        "include_domains": include_domains or [],
        "exclude_domains": exclude_domains or []
    }

    try:
        response = requests.post(
            f"{TAVILY_BASE_URL}/search",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
