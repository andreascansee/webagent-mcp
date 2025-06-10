from tools.search_urls import search_urls
from tools.fetch_page import fetch_page_text
from mcp.server.fastmcp import FastMCP

# Initilaize FastMCP server
mcp = FastMCP("web-scrapper")

mcp.tool()(search_urls)
mcp.tool()(fetch_page_text) 

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")