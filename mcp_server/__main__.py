"""
Web Scraper MCP Server

This MCP server provides web scraping capabilities through two main tools:
- search_urls: Search for URLs based on queries
- fetch_page_text: Extract text content from web pages

The server uses FastMCP for easy setup and integration with MCP-compatible clients.
"""

from mcp_server.tools.search_urls import search_urls
from mcp_server.tools.fetch_page import fetch_page_text
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("web-scraper")

# Register the search tool for finding URLs
mcp.tool()(search_urls)

# Register the fetch tool for extracting page content
mcp.tool()(fetch_page_text) 

if __name__ == "__main__":
    mcp.run(transport='stdio')