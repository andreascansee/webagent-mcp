# Import the asynchronous Ollama client implementation
from mcp_client.llm.ollama_client import OllamaClient
import asyncio

# --- Tool definition used for testing tool call behavior ---
DUMMY_TOOL_SCHEMA = {
    "name": "get_current_weather",
    "description": "Get the current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "The city and state, e.g., San Francisco, CA"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
        },
        "required": ["location"]
    }
}

# --- Message used to prompt a tool call ---
TOOL_CALL_MESSAGES = [{
    'role': 'user',
    'content': 'What is the weather like in Paris, France? Please use the weather tool if you have one.'
}]


# Define an async test function to interact with the Ollama model
async def test_ollama_client():
    print("--- Starting Ollama Client Test ---")

    # Initialize the Ollama client with default model and host
    client = OllamaClient()

    # --- Test 1: Simple text-only interaction ---
    print("Testing simple text query...")
    text_messages = [{'role': 'user', 'content': 'What is the capital of France?'}]
    try:
        # Send message to the model and await response
        response = await client.chat(text_messages)
        print("\n--- Ollama Text Response ---")

        # Extract and print textual response
        for content_block in response.get('content', []):
            if content_block['type'] == 'text':
                print(content_block['text'])

        print("----------------------------\n")
    except Exception as e:
        print(f"Failed to get text response: {e}")

    # --- Test 2: Simulated tool use scenario ---
    print("Testing tool call simulation (Ollama might not actually use it without specific prompt)...")

    try:

        # Send message with dummy tool included
        response = await client.chat(
            messages=TOOL_CALL_MESSAGES,
            tools=[DUMMY_TOOL_SCHEMA]
        )

        print("\n--- Ollama Tool Response (if any) ---")

        # Print tool or text output depending on response content
        for content_block in response.get('content', []):
            print(f"Type: {content_block['type']}")
            if content_block['type'] == 'text':
                print(f"Text: {content_block['text']}")
            elif content_block['type'] == 'tool_use':
                print(f"Tool Name: {content_block['name']}")
                print(f"Tool Input: {content_block['input']}")

        print("------------------------------------\n")

    except Exception as e:
        print(f"Failed to get tool response: {e}")

    print("--- Ollama Client Test Finished ---")

# Entry point for running this test script
if __name__ == "__main__":
    asyncio.run(test_ollama_client())
