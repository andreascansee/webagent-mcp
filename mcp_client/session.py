import asyncio
import json
from mcp_client.agent import MCPAgent

# Path to the server configuration file
CONFIG_FILE = "server_config.json"

async def main():
    # Instantiate the agent that manages LLM interaction and MCP tool sessions
    agent = MCPAgent()
    
    try:
        # Load the server configuration from JSON file
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        # Extract the dictionary of servers to connect to
        servers = config.get("mcpServers", {})
        if not servers:
            raise ValueError("No servers defined in config.")

        # Iterate through each server entry and connect
        for name, cfg in servers.items():
            await agent.connect_to_server(name, cfg)

        # Start the interactive chat loop after connecting all servers
        await agent.chat_loop()

    except Exception as e:
        # Print full error traceback if anything goes wrong during setup
        import traceback
        print(f"[ERROR] Failed during server startup: {e}")
        traceback.print_exc()
    
    finally:
        # Ensure all resources (server connections etc.) are closed properly
        await agent.cleanup()

# Entry point of the program – runs the main async function
if __name__ == "__main__":
    asyncio.run(main())
