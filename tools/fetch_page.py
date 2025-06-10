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
        for tag in soup(["script", "style", "noscript", "meta", "link"]):
            tag.decompose()

        # Extract text with better formatting
        text = soup.get_text(separator="\n", strip=True)
        
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        return text[:char_limit] if char_limit > 0 else text
        
    except Exception as e:
        raise RuntimeError(f"Error parsing HTML content: {e}")

def fetch_page_with_metadata(url: str, char_limit: int = 2000) -> dict:
    """
    Fetches page text along with basic metadata (title, description).
    
    Args:
        url: The URL to fetch
        char_limit: Maximum characters for text content
        
    Returns:
        Dictionary with 'title', 'text', 'description' keys
    """
    if not url.strip():
        raise ValueError("URL cannot be empty")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching URL: {e}")
    
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else "No title"
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '').strip() if meta_desc else "No description"
        
        # Extract main text content
        for tag in soup(["script", "style", "noscript", "meta", "link"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        return {
            'title': title,
            'text': text[:char_limit] if char_limit > 0 else text,
            'description': description,
            'url': url
        }
        
    except Exception as e:
        raise RuntimeError(f"Error parsing HTML content: {e}")

# Optional test run
if __name__ == "__main__":
    url = input("Enter URL: ")
    try:
        # Test basic function
        text = fetch_page_text(url)
        print(f"\nText content (up to 2000 chars):\n{'-'*40}\n{text}")
        
        # Test metadata function
        print(f"\n{'='*40}")
        metadata = fetch_page_with_metadata(url, char_limit=500)
        print(f"Title: {metadata['title']}")
        print(f"Description: {metadata['description']}")
        print(f"Text preview: {metadata['text'][:200]}...")
        
    except Exception as e:
        print(f"\nError: {e}")