import os
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()

# Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")

# Set Ollama's expected host environment variable
os.environ["OLLAMA_HOST"] = OLLAMA_HOST