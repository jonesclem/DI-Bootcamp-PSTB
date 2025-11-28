"""
Simple configuration helper.

Reads settings from environment variables and exposes them as a Config
dataclass, used across the app (Streamlit UI, agent, MCP client, etc.).
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    """
    Central config object.

    llm_backend:
      - "ollama" (default) to use local Ollama
      - "groq" to use GroqCloud

    The rest are self-explanatory environment-driven settings.
    """

    # LLM backend choice
    llm_backend: str

    # Ollama settings
    ollama_base_url: str
    ollama_model: str

    # Groq settings (used only if llm_backend == "groq")
    groq_base_url: str | None
    groq_model: str | None
    groq_api_key: str | None

    # MCP server command lines (stdio) — names used by mcp_client.py
    fetch_cmd: str
    filesystem_cmd: str
    kb_metadata_cmd: str

    # Knowledge base paths
    kb_root_dir: str
    kb_metadata_path: str

    # Agent behavior
    max_tool_retries: int
    log_level: str


def get_config() -> Config:
    """
    Read environment variables and build a Config instance.

    This keeps the rest of the code decoupled from os.environ.
    """
    return Config(
        # LLM backend selection
        llm_backend=os.getenv("LLM_BACKEND", "ollama").lower(),

        # Ollama
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),

        # Groq
        groq_base_url=os.getenv("GROQ_BASE_URL"),
        groq_model=os.getenv("GROQ_MODEL"),
        groq_api_key=os.getenv("GROQ_API_KEY"),

        # MCP servers (stdio commands) — env var names stay as before
        fetch_cmd=os.getenv("MCP_FETCH_CMD", "uvx mcp-server-fetch"),
        filesystem_cmd=os.getenv(
            "MCP_FILESYSTEM_CMD",
            "npx -y @modelcontextprotocol/server-filesystem ./kb",
        ),
        kb_metadata_cmd=os.getenv(
            "MCP_KB_METADATA_CMD",
            "python -m src.kb_metadata_server.server",
        ),

        # KB paths
        kb_root_dir=os.getenv("KB_ROOT_DIR", "./kb"),
        kb_metadata_path=os.getenv("KB_METADATA_PATH", "./kb/metadata.jsonl"),

        # Agent knobs
        max_tool_retries=int(os.getenv("MAX_TOOL_RETRIES", "2")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )