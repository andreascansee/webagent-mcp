# MCP Client & Server Demo

This project demonstrates a minimal but functional implementation of an **MCP (Model Context Protocol)** system, combining:

- ✅ a **local MCP server** exposing tools (like web search & page fetching)
- 🤖 a **client agent** powered by a local LLM (e.g. via Ollama)
- 🌐 optional **debug UI** using the [MCP Inspector](https://www.npmjs.com/package/@modelcontextprotocol/inspector)

---

## 🔍 What does it do?

The client uses a local LLM to respond to user queries.  
It can **automatically invoke tools** like:

- `search_urls`: Uses DuckDuckGo to search for relevant links
- `fetch_page_text`: Downloads and extracts the text from a web page

The system prompt guides the LLM to use these tools **autonomously** to research and summarize information from the web.

Example:  
You ask **"What's the latest news on AI chips?"**  
→ The LLM will:
1. Use `search_urls` to find links  
2. Pick one  
3. Use `fetch_page_text` to extract the content  
4. Summarize it for you – all in one response.

---

## 📂 Project Structure

```
.
├── img
│   ├── mcp-inspector-tools.png
│   └── mcp-inspector.png
├── mcp_client
│   ├── __init__.py
│   ├── agent.py
│   ├── llm
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── ollama_client.py
│   │   ├── prompts.py
│   │   └── tool_helpers.py
│   └── session.py
├── mcp_server
│   ├── __main__.py
│   └── tools
│       ├── fetch_page.py
│       └── search_urls.py
├── README.md
├── requirements.txt
└── tests
    ├── __init__.py
    ├── test_fetch_page.py
    ├── test_ollama_client.py
    └── test_search_urls.py
```


## 🚀 Start the Client

To launch the interactive MCP agent:

```bash
python -m mcp_client.session
```

This starts a local session that connects to your MCP server and interacts with it via a local LLM (e.g. Ollama).


### Testing with MCP Inspector

The MCP Inspector is a web-based tool for debugging and testing your MCP server in real-time. It allows you to inspect available tools, simulate tool calls, and verify responses before integrating with a client like this one.

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
npx @modelcontextprotocol/inspector python -m mcp_server
```

You should see a UI like this:


![image](./img/mcp-inspector.png)

![image](./img/mcp-inspector-tools.png)


## ✅ Running Tests
To run a test module directly:

```bash
python -m tests.test_fetch_page
```

## ℹ️ Ollama Response Notes
The response from `ollama.chat()` (non-streaming) has the following structure:

```python
{
  "model": "llama3",
  "created_at": "...",
  "message": {
    "role": "assistant",
    "content": "..."
  },
  "done": True
}
```

If the LLM triggers a tool call, it will appear under:

```python
response["message"]["tool_calls"]
```