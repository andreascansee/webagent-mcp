import requests
from bs4 import BeautifulSoup

def fetch_page_text(url: str, char_limit: int = 2000, timeout: int = 10) -> str:
    """
    Fetches visible text from a webpage, optionally truncates to char_limit, and returns as string.
    
    Args:
        url: The URL to fetch
        char_limit: Maximum characters to return (0 for no limit)
        timeout: Request timeout in seconds
    
    Returns:
        Extracted text content as string
        
    Raises:
        RuntimeError: If URL cannot be fetched or parsed
        ValueError: If URL is invalid
    """
    # Basic URL validation
    if not url.strip():
        raise ValueError("URL cannot be empty")
    
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    
    try:
        # Add user agent to avoid some blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
        
        # Check if content is actually HTML
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            raise RuntimeError(f"URL does not return HTML content (got: {content_type})")
            
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching URL: {e}")
    
    try:
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted tags (scripts, styles, etc.)
        for tag in soup(["script", "style", "noscript", "meta", "link", "header", "footer", "nav", "aside"]):
            tag.decompose()

        # Extract text with better formatting
        main = soup.find("main") or soup.find("article") or soup.find("div", id="content")
        if main:
            text = main.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        return text[:char_limit] if char_limit > 0 else text
        
    except Exception as e:
        raise RuntimeError(f"Error parsing HTML content: {e}")