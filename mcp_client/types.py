
from typing import TypedDict

class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict