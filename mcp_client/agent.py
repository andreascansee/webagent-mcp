import subprocess
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp_client.llm.ollama_client import OllamaClient
from mcp_client.llm.prompts import SYSTEM_PROMPT
from mcp_client.llm.tool_helpers import (
    format_tool_result_as_user_message,
    extract_text_from_tool_result
)

class MCPAgent:
    """
    The main agent class for interacting with the MCP server and the local LLM.
    """

    MAX_LOOP_ITERATIONS = 5

    def __init__(self):
        self.mcp_session: ClientSession | None = None
        self.llm_client = OllamaClient()
        self.available_llm_tools: list = []  # All tools registered from the MCP server
        self.messages = []  # The message history sent to the LLM

    async def handle_tool_call(self, tool_name: str, tool_args: dict, tool_use_id: str) -> str:
        """
        Executes the given MCP tool and returns the result as a plain string.
        """
        print(f"Calling MCP tool '{tool_name}'...")
        tool_response = await self.mcp_session.call_tool(tool_name, arguments=tool_args)

        return extract_text_from_tool_result(tool_response.content)

    async def connect_to_mcp_server(self, server_command: str, server_args: list):
        """
        Starts the MCP server via subprocess and establishes a session.
        """
        print("\n--- Connecting to MCP Server ---")
        server_params = StdioServerParameters(
            command=server_command,
            args=server_args,
            env=None,
            stderr=subprocess.PIPE
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            print(f"Attempting to connect to MCP server: Command='{server_command}', Args={server_args}")
            print("Stdio client context established. Server process should be running.")

            async with ClientSession(read_stream, write_stream) as session:
                self.mcp_session = session
                print("MCP ClientSession created. Initializing connection...")
                await session.initialize()
                print("MCP connection initialized successfully!")

                # Get all available tools from the server
                response = await session.list_tools()
                mcp_tools = response.tools

                self.available_llm_tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in mcp_tools]

                print(f"Connected to MCP server with tools: {[tool.name for tool in mcp_tools]}")
                print(f"Prepared {len(self.available_llm_tools)} tools for LLM interaction.")

                # Add the system prompt to initialize the chat context
                self.messages.append({"role": "system", "content": SYSTEM_PROMPT})

                print("\n--- Agent initialized and ready for chat loop ---")
                await self.chat_loop()

            print("Exiting ClientSession context. Server will shut down.")

    async def process_query(self, query: str):
        """
        Handles a single user query by interacting with the LLM
        and executing any tool calls it may request.
        """
        print(f"\nProcessing query: {query}")
        self.messages.append({"role": "user", "content": query})

        loop_count = 0

        while loop_count < self.MAX_LOOP_ITERATIONS:
            loop_count += 1
            try:
                print(f"Calling LLM (Iteration {loop_count})...")
                ollama_response = await self.llm_client.chat(
                    messages=self.messages,
                    tools=self.available_llm_tools
                )

                if 'content' not in ollama_response or not ollama_response['content']:
                    print("\nLLM returned no content or an empty response.")
                    self.messages.append({"role": "assistant", "content": "[No reply]"})
                    break

                assistant_message_content = []
                tool_calls_made_this_turn = []

                for block in ollama_response['content']:
                    if block['type'] == 'text':
                        print("\nLLM says:")
                        print(block['text'])
                        assistant_message_content.append(block)
                    elif block['type'] == 'tool_use':
                        tool_name = block['name']
                        tool_args = block['input']
                        tool_use_id = block['id']
                        print(f"\nLLM requested tool: {tool_name} with arguments: {tool_args}")
                        assistant_message_content.append(block)
                        tool_calls_made_this_turn.append((tool_name, tool_args, tool_use_id))

                # Add assistant reply (text + tool_use metadata) to message history
                text_parts = [b['text'] for b in assistant_message_content if b['type'] == 'text']
                final_text = "\n".join(text_parts).strip() or "[No response]"
                self.messages.append({"role": "assistant", "content": final_text})

                if tool_calls_made_this_turn:
                    for tool_name, tool_args, tool_use_id in tool_calls_made_this_turn:
                        result = await self.handle_tool_call(tool_name, tool_args, tool_use_id)
                        print(f"Tool '{tool_name}' returned: {result[:200]}...")

                        self.messages.append(format_tool_result_as_user_message(tool_name, result))

                else:
                    break  # No tools requested, LLM has responded with final answer

            except Exception as e:
                print(f"\n[Error in process_query] An error occurred during LLM interaction or tool execution: {e}")
                break

        if loop_count >= self.MAX_LOOP_ITERATIONS:
            print("\n[Warning] Exceeded maximum LLM interaction iterations. Stopping to prevent infinite loop.")

    async def chat_loop(self):
        """
        Handles the interactive chat loop in the console.
        """
        print("Chat loop started. Type 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break
                await self.process_query(query)
            except Exception as e:
                print(f"\nError in chat loop: {e}")
        print("Chat loop finished.")