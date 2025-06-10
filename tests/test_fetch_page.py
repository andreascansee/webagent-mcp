from mcp_server.tools.fetch_page import fetch_page_text

if __name__ == "__main__":
    # Prompt the user to enter a URL
    url = input("Enter URL to fetch: ").strip()

    try:
        print("\n--- Page Content ---")
        text = fetch_page_text(url, char_limit=2000, timeout=15)
        print(text)

    except Exception as e:
        print(f"\nError: {e}")
