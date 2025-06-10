from duckduckgo_search import DDGS
from typing import List, Optional, Dict, Any

def search_urls(query: str, max_results: int = 3, region: str = "wt-wt") -> List[str]:
    """
    Search for URLs using DuckDuckGo search API.
    
    Args:
        query: Search term/query string
        max_results: Maximum number of URLs to return (default: 3)
        region: Search region code (default: "wt-wt" for worldwide)
    
    Returns:
        List of URLs as strings
    
    Raises:
        RuntimeError: If search fails or no results found
    """
    if not query.strip():
        raise ValueError("Query cannot be empty")
    
    urls = []
    
    try:
        with DDGS() as ddgs:
            # Use text search with proper error handling
            results = ddgs.text(
                query, 
                region=region, 
                safesearch="moderate", 
                max_results=max_results
            )
            
            # Convert generator to list and extract URLs
            for result in results:
                if isinstance(result, dict) and "href" in result:
                    urls.append(result["href"])
                    # Stop when we have enough results
                    if len(urls) >= max_results:
                        break
            
            if not urls:
                raise RuntimeError(f"No search results found for query: {query}")
                
    except Exception as e:
        raise RuntimeError(f"Search failed: {str(e)}")
    
    return urls
