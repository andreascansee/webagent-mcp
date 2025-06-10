

### Testing with MCP Inspector

The MCP Inspector is a powerful debugging and testing tool that allows you to interact with your MCP server in real-time. It provides a web-based interface to test your server's tools and resources before integrating them with Claude or other MCP clients.

#### 1. Install the MCP Inspector (if not already installed):
```bash
npm install -g @modelcontextprotocol/inspector
```

#### 2. Activate your virtual environment:
```bash
source venv/bin/activate
```

#### 3. Start the Inspector with your server:
```bash
npx @modelcontextprotocol/inspector python webagent_mcp_server.py
```