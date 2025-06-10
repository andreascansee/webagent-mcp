def format_tool_result_as_user_message(tool_name: str, result: str) -> dict:
    """
    Injects the result of a tool call into the conversation as a synthetic 'user' message,
    so that the LLM can reason based on the tool output.

    ⚠️ This is a compatibility workaround for models/backends that do not support
    OpenAI-style function-calling with structured tool return values.

    OpenAI standard (not used here):
        The assistant returns {"tool_calls": [...]}, and the caller responds with
        {"tool_outputs": [...]} — all typed and separated.

    What we do instead:
        We simulate tool results by adding a plain user message like:
        {
            "role": "user",
            "content": "[Tool 'fetch_page_text' result]:\n<raw result string>"
        }

    Why:
        Some models (e.g. Mistral, Qwen, GPT via text-based APIs) only support flat message lists.
        This hack ensures that the LLM sees and reasons over tool results, even without native support.

    Args:
        tool_name: The tool that was called.
        result: The plain string result returned by the tool.

    Returns:
        A conversation message dictionary, as if the user had posted the tool result manually.
    """
    return {
        "role": "user",
        "content": f"[Tool '{tool_name}' result]:\n{result}"
    }


def extract_text_from_tool_result(content: object) -> str:
    """
    Extracts plain text from the result content of a tool call.

    This function normalizes different content formats (e.g., list of objects, object with `.text`, or raw string)
    into a single plain string for use in the conversation.

    Args:
        content: The raw content object returned from a tool call.

    Returns:
        A plain string representing the tool result.
    """
    if isinstance(content, list):
        return "\n".join(tc.text for tc in content if hasattr(tc, "text"))
    if hasattr(content, "text"):
        return content.text
    return str(content)
