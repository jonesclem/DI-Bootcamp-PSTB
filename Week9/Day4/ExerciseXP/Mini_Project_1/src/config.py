"""
Configuration helpers for the MCP research agent.

This module:
- Reads environment variables.
- Produces a Config object used by the rest of the app.
- Validates that Groq-specific settings are present.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    """
    Central configuration for the application.

    All values are derived from environment variables so that:
    - LLM backend details can be swapped without code changes.
    - MCP server commands can be adjusted per machine.
    - KB paths can be customized.
    """

    groq_base_url: str
    groq_model: str
    groq_api_key: str

    fetch_cmd: str
    filesystem_cmd: str
    kb_metadata_cmd: str

    kb_root_dir: str
    kb_metadata_path: str

    max_tool_retries: int
    log_level: str

    def validate(self) -> None:
        """
        Basic validation to avoid silent misconfiguration.

        For this project we only support Groq, so the API key and model
        must be present.
        """
        if not self.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is required for Groq backend.")
        if not self.groq_model:
            raise RuntimeError("GROQ_MODEL is required for Groq backend.")


def get_config() -> Config:
    """
    Load configuration from environment variables and validate it.

    Example .env values:

        GROQ_API_KEY=sk_...
        GROQ_BASE_URL=https://api.groq.com/openai/v1
        GROQ_MODEL=openai/gpt-oss-20b

        MCP_FETCH_CMD=uvx mcp-server-fetch
        MCP_FILESYSTEM_CMD=npx -y @modelcontextprotocol/server-filesystem .
        MCP_KB_METADATA_CMD=python -m src.kb_metadata_server.server

        KB_ROOT_DIR=.
        KB_METADATA_PATH=./kb/metadata.jsonl
        MAX_TOOL_RETRIES=2
        LOG_LEVEL=INFO
    """
    cfg = Config(
        groq_base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),

        fetch_cmd=os.getenv("MCP_FETCH_CMD", "uvx mcp-server-fetch"),
        filesystem_cmd=os.getenv(
            "MCP_FILESYSTEM_CMD",
            "npx -y @modelcontextprotocol/server-filesystem .",
        ),
        kb_metadata_cmd=os.getenv(
            "MCP_KB_METADATA_CMD",
            "python -m src.kb_metadata_server.server",
        ),

        kb_root_dir=os.getenv("KB_ROOT_DIR", "."),
        kb_metadata_path=os.getenv("KB_METADATA_PATH", "./kb/metadata.jsonl"),

        max_tool_retries=int(os.getenv("MAX_TOOL_RETRIES", "2")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
    cfg.validate()
    return cfg