import ollama
from mcp_client.llm.config import OLLAMA_HOST, OLLAMA_MODEL

class OllamaClient:
    """
    A minimal async client wrapper for Ollama models.

    This class provides a unified chat interface and handles optional tool-calling
    logic compatible with the Ollama API format.
    """

    def __init__(self, model: str = OLLAMA_MODEL):
        """
        Initialize the client with the given model and Ollama host.

        Args:
            model: The model name to use (e.g., "qwen2.5:14b")
        """
        self.model = model
        self.client = ollama.AsyncClient(host=OLLAMA_HOST)
        print(f"OllamaClient initialized with model: '{self.model}' and host: '{OLLAMA_HOST}'")

    async def chat(self, messages: list, tools: list = None) -> dict:
        """
        Send a prompt and return a structured response from the model.

        Args:
            messages: List of chat-style messages (dicts with 'role' and 'content')
            tools: Optional list of tools in structured format (name, description, input_schema)

        Returns:
            A dict with a 'content' key, containing a list of blocks:
            - {"type": "text", "text": "..."}
            - {"type": "tool_use", "id": ..., "name": ..., "input": ...}

        Raises:
            RuntimeError on unexpected issues
        """
        try:
            # Prepare tools in Ollama format
            ollama_tools = []
            if tools:
                for tool in tools:
                    ollama_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool["input_schema"]  # Ollama uses 'parameters'
                        }
                    })

            # Debug output of request payload
            print("\n--- Sending to Ollama ---")
            print(f"Model: {self.model}")
            print(f"Messages: {messages}")
            print(f"Tools (Ollama format): {ollama_tools}")
            print("-------------------------\n")

            # Send the chat request (non-streaming)
            response = await self.client.chat(
                model=self.model,
                messages=messages,
                tools=ollama_tools,
                stream=False
            )

            response_message = response.get("message", {})
            content_blocks = []

            # Add text content, if any
            msg_content = response_message.get("content")
            if msg_content:
                content_blocks.append({
                    "type": "text",
                    "text": msg_content
                })

            # Add tool calls, if any (guard against malformed responses)
            tool_calls = response_message.get("tool_calls")
            if tool_calls:
                for tool_call in tool_calls:
                    fn = tool_call.get("function", {})
                    if "name" in fn and "arguments" in fn:
                        content_blocks.append({
                            "type": "tool_use",
                            "id": fn["name"],
                            "name": fn["name"],
                            "input": fn["arguments"]
                        })

            return {"content": content_blocks}

        except ollama.ResponseError as e:
            print(f"[Ollama Error] Response Error: {e.status_code} - {e.response}")
            raise
        except Exception as e:
            print(f"[Ollama Error] An unexpected error occurred: {e}")
            raise
