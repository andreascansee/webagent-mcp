import asyncio
from mcp_client.agent import MCPAgent

async def main():
    agent = MCPAgent()
    try:
        await agent.connect_to_mcp_server("python", ["-m", "mcp_server"])
        print("\nMCP Agent test finished.")
    except Exception as e:
        import traceback
        print(f"\n[CRITICAL ERROR] Agent startup failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())