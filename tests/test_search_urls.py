from mcp_server.tools.search_urls import search_urls

if __name__ == "__main__":
    # Prompt the user to enter a search query
    query = input("Enter search query: ").strip()

    try:
        # Print a heading for the output
        print("\n--- Search results ---")

        # Perform the search using DuckDuckGo
        urls = search_urls(query, max_results=5)

        # Print the resulting URLs
        for i, url in enumerate(urls, start=1):
            print(f"{i}. {url}")

    except Exception as e:
        # Print any error that occurs
        print(f"\nError: {e}")
