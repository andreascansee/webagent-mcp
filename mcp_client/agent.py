from contextlib import AsyncExitStack
from typing import List, Dict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp_client.types import ToolDefinition
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

    MAX_LOOP_ITERATIONS = 5  # Prevent infinite loops if the LLM repeatedly calls tools

    def __init__(self):
        self.sessions: List[ClientSession] = []  # All active tool server sessions
        self.exit_stack = AsyncExitStack()       # Ensures clean async resource teardown
        self.llm_client = OllamaClient()         # Handles interaction with the local LLM
        self.available_llm_tools: List[ToolDefinition] = []  # Tool metadata passed to the LLM
        self.tool_to_session: Dict[str, ClientSession] = {}  # Maps tool names to MCP sessions
        self.messages = []  # Complete message history sent to the LLM

    async def handle_tool_call(self, tool_name: str, tool_args: dict, tool_use_id: str) -> str:
        """
        Executes a single MCP tool and returns its output as plain string.
        """
        print(f"Calling MCP tool '{tool_name}'...")
        session = self.tool_to_session.get(tool_name)
        if not session:
            raise ValueError(f"No session found for tool: {tool_name}")

        tool_response = await session.call_tool(tool_name, arguments=tool_args)
        return extract_text_from_tool_result(tool_response.content)

    async def connect_to_server(self, server_name: str, server_config: dict) -> None:
        """
        Launches and connects to an MCP server via stdio transport.
        Registers all available tools for that session.
        """
        try:
            server_params = StdioServerParameters(**server_config)

            # Automatically close connections when the agent shuts down
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport

            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.sessions.append(session)

            # Fetch and register all tools from this server
            response = await session.list_tools()
            tools = response.tools
            print(f"\nConnected to {server_name} with tools:", [t.name for t in tools])

            for tool in tools:
                self.tool_to_session[tool.name] = session
                self.available_llm_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })

        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")

    async def process_query(self, query: str):
        """
        Sends a user query to the LLM and handles any resulting tool calls.
        """
        if not self.messages:
            self.messages.append({"role": "system", "content": SYSTEM_PROMPT})  # Inject initial system prompt

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

                # Handle malformed responses
                if 'content' not in ollama_response or not ollama_response['content']:
                    print("\nLLM returned no content or an empty response.")
                    self.messages.append({"role": "assistant", "content": "[No reply]"})
                    break

                assistant_message_content = []
                tool_calls_made_this_turn = []

                # Process each returned block: text or tool call
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

                # Add assistant response to message history (text + tool metadata)
                text_parts = [b['text'] for b in assistant_message_content if b['type'] == 'text']
                final_text = "\n".join(text_parts).strip() or "[No response]"
                self.messages.append({"role": "assistant", "content": final_text})

                # Execute any requested tools and inject their result as synthetic user messages
                if tool_calls_made_this_turn:
                    for tool_name, tool_args, tool_use_id in tool_calls_made_this_turn:
                        result = await self.handle_tool_call(tool_name, tool_args, tool_use_id)
                        print(f"Tool '{tool_name}' returned: {result[:200]}...")
                        self.messages.append(format_tool_result_as_user_message(tool_name, result))
                else:
                    break  # No tool calls → final answer received

            except Exception as e:
                print(f"\n[Error in process_query] An error occurred during LLM interaction or tool execution: {e}")
                break

        if loop_count >= self.MAX_LOOP_ITERATIONS:
            print("\n[Warning] Exceeded maximum LLM interaction iterations. Stopping to prevent infinite loop.")

    async def chat_loop(self):
        """
        Simple interactive console chat loop.
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

    async def cleanup(self):
        """
        Cleanly shut down all sessions using the exit stack.
        """
        await self.exit_stack.aclose()
