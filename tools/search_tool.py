"""
Simple Tavily-powered web search tool (returns raw results)
"""
import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

load_dotenv()


@tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web using Tavily and return the raw Tavily response as JSON.

    Args:
        query: Search query
        max_results: Number of results to include (default 5)

    Returns:
        Raw Tavily results as a JSON string (LLM can format as needed)
    """
    if not os.environ.get("TAVILY_API_KEY"):
        return "Search not available. Please set TAVILY_API_KEY in the environment."

    try:
        tavily = TavilySearch(max_results=max_results)
        raw = tavily.invoke(query)
        return json.dumps(raw, ensure_ascii=False)
    except Exception as e:
        return f"Search error: {e}"