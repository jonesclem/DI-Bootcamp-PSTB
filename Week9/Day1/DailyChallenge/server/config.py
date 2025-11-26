# server/config.py
import os


MCP_HTTP_TOKEN = os.environ.get("MCP_HTTP_TOKEN")
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

# Ollama config
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")  # or llama3, gemma3 etc.


def require_config():
    missing = []
    if not MCP_HTTP_TOKEN:
        missing.append("MCP_HTTP_TOKEN")
    if not SERPER_API_KEY:
        missing.append("SERPER_API_KEY")
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )