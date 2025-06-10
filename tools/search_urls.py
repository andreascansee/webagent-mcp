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

def search_urls_with_metadata(query: str, max_results: int = 3, region: str = "wt-wt") -> List[Dict[str, Any]]:
    """
    Search and return full metadata (title, snippet, URL) instead of just URLs.
    
    Args:
        query: Search term/query string
        max_results: Maximum number of results to return
        region: Search region code
    
    Returns:
        List of dictionaries containing 'title', 'href', 'body' keys
    """
    if not query.strip():
        raise ValueError("Query cannot be empty")
    
    results = []
    
    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query, 
                region=region, 
                safesearch="moderate", 
                max_results=max_results
            )
            
            for result in search_results:
                if isinstance(result, dict):
                    # Keep the full result with title, snippet, and URL
                    results.append({
                        'title': result.get('title', 'No title'),
                        'href': result.get('href', ''),
                        'body': result.get('body', 'No description')
                    })
                    
                    if len(results) >= max_results:
                        break
            
            if not results:
                raise RuntimeError(f"No search results found for query: {query}")
                
    except Exception as e:
        raise RuntimeError(f"Search failed: {str(e)}")
    
    return results

# Example usage and testing
if __name__ == "__main__":
    try:
        search_term = input("Search term: ")
        
        # Test URL-only search
        print("\n=== URLs only ===")
        urls = search_urls(search_term, max_results=5)
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
        
        # Test full metadata search
        print("\n=== Full results ===")
        results = search_urls_with_metadata(search_term, max_results=3)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['href']}")
            print(f"   Preview: {result['body'][:100]}...")
            print()
            
    except Exception as e:
        print(f"Error: {e}")