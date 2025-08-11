"""
Search Tool for general web search
"""
import os
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

class SearchTool:
    def __init__(self):
        self.search = None
        self.tavily_search = None
        self._setup_search()
    
    def _setup_search(self):
        """Setup search tools if API key is available"""
        try:
            if os.environ.get("TAVILY_API_KEY"):
                self.search = TavilySearchResults()
                self.tavily_search = TavilySearch(max_results=5)
                print("✅ Tavily search initialized")
            else:
                print("⚠️  Tavily API key not found, search tools will not work")
        except Exception as e:
            print(f"⚠️  Could not initialize search tools: {e}")
    
    def search_web(self, query: str) -> str:
        """
        Search the web for information
        
        Args:
            query: The search query
            
        Returns:
            Search results as a formatted string
        """
        if not self.search:
            return "Search tool not available. Please set TAVILY_API_KEY environment variable."
        
        try:
            results = self.search.run(query)
            if isinstance(results, list):
                formatted_results = []
                for i, result in enumerate(results[:5], 1):  # Limit to 5 results
                    title = result.get('title', 'No title')
                    content = result.get('content', 'No content')
                    url = result.get('url', 'No URL')
                    formatted_results.append(f"{i}. {title}\n   {content}\n   URL: {url}\n")
                return "\n".join(formatted_results)
            else:
                return str(results)
        except Exception as e:
            return f"Search error: {e}"


# Create global instance
search_tool = SearchTool()


@tool
def search_web(query: str, formatted: bool = True) -> str:
    """
    Search the web for information using Tavily.
    Use this tool when asked to search for current information, news, or general knowledge.
    
    Args:
        query: The search query to look up on the web
        formatted: If True, returns nicely formatted results. If False, returns raw Tavily output.
        
    Returns:
        Search results from the web
    """
    if not search_tool.search:
        return "Search tool not available. Please set TAVILY_API_KEY environment variable."
    
    try:
        if formatted:
            return search_tool.search_web(query)
        else:
            return search_tool.tavily_search.invoke(query)
    except Exception as e:
        return f"Search error: {e}" 