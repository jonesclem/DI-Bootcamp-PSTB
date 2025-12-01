# smart_data_scout/config.py
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dotenv import load_dotenv

# allow config via .env if present
load_dotenv()


@dataclass
class MCPServerConfig:
    name: str
    command: str
    args: List[str]
    env: Dict[str, str] = field(default_factory=dict)


@dataclass
class LLMConfig:
    backend: str  # "groq" or "ollama"
    model: str
    api_base: Optional[str] = None  # used for Ollama / OpenAI-compatible endpoints


@dataclass
class AppConfig:
    llm: LLMConfig
    mcp_servers: Dict[str, MCPServerConfig]
    max_agent_steps: int = 6


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.

    LLM config:
    - LLM_BACKEND: "groq" or "ollama" (default: groq)
    - GROQ_API_KEY: required if backend == "groq"
    - GROQ_MODEL: optional, default "llama-3.3-70b-versatile"
    - OLLAMA_MODEL: optional, default "llama3.1"
    - OLLAMA_API_BASE: optional, default "http://localhost:11434/v1"

    MCP servers:

    Web search: duckduckgo-mcp-server (nickclyde)
    - pip/uv install: `uv pip install duckduckgo-mcp-server` or `pip install duckduckgo-mcp-server`
      and then run `duckduckgo-mcp-server` as a stdio MCP server. :contentReference[oaicite:0]{index=0}

    CSV editor: csv-editor (santoshray02)
    - install via GitHub: `pip install git+https://github.com/santoshray02/csv-editor.git`
      which provides the `csv-editor` CLI MCP server. :contentReference[oaicite:1]{index=1}
    """

    backend = os.getenv("LLM_BACKEND", "groq").lower()
    if backend == "groq":
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        api_base = None
    elif backend == "ollama":
        model = os.getenv("OLLAMA_MODEL", "llama3.1")
        api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434/v1").rstrip("/")
    else:
        raise ValueError(f"Unsupported LLM_BACKEND: {backend}")

    # Web search server (duckduckgo-mcp-server)
    # After installing from PyPI, there is a console script `duckduckgo-mcp-server`. :contentReference[oaicite:2]{index=2}
    web_search_cmd = os.getenv("DDG_MCP_COMMAND", "duckduckgo-mcp-server")

    # CSV Editor server (csv-editor)
    csv_editor_cmd = os.getenv("CSV_EDITOR_COMMAND", "csv-editor")

    mcp_servers: Dict[str, MCPServerConfig] = {
        "web-search": MCPServerConfig(
            name="web-search",
            command=web_search_cmd,
            args=[],
            env={},  # no API key required
        ),
        "csv-editor": MCPServerConfig(
            name="csv-editor",
            command=csv_editor_cmd,
            args=[],
            env={
                # default limits; can be overridden via env :contentReference[oaicite:3]{index=3}
                "CSV_MAX_FILE_SIZE": os.getenv("CSV_MAX_FILE_SIZE", "1073741824"),  # 1 GB
                "CSV_SESSION_TIMEOUT": os.getenv("CSV_SESSION_TIMEOUT", "3600"),
                "CSV_CHUNK_SIZE": os.getenv("CSV_CHUNK_SIZE", "10000"),
            },
        ),
        "insights": MCPServerConfig(
            name="insights",
            command="python",
            args=["-m", "insights_server.server"],
            env={},
        ),
    }

    llm_cfg = LLMConfig(backend=backend, model=model, api_base=api_base)
    return AppConfig(llm=llm_cfg, mcp_servers=mcp_servers)