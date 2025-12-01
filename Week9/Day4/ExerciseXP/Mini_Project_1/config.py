# Mini Project – MCP Agentic Application (Part 1 + Part 2)
# This module centralizes configuration:
# - LLM backend selection (GroqCloud or Ollama) for llm_client.py
# - MCP servers configuration for:
#   * external servers from Part 1 (e.g. "files", "web")
#   * custom server from Part 2 ("local_insights" implemented in my_mcp_server.py)
# load_mcp_server_configs() is used by mcp_multi_client.py and orchestrator.py.


from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load .env file at import time
load_dotenv()


# ### LLM configuration dataclass
@dataclass
class LLMConfig:
    backend: str          # "groq" or "ollama"
    model: str
    base_url: str
    api_key: str


# ### MCP server configuration dataclass
@dataclass
class MCPServerConfig:
    name: str             # logical name, used for namespacing tools
    command: str          # e.g. "npx" or "python"
    args: List[str]       # command arguments for the server
    env: Optional[Dict[str, str]] = None


# ### Load LLM configuration from environment variables
def load_llm_config() -> LLMConfig:
    backend = os.getenv("LLM_BACKEND", "groq").lower()

    if backend == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is required when LLM_BACKEND='groq'.")

        return LLMConfig(
            backend="groq",
            model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
            api_key=api_key,
        )

    if backend == "ollama":
        return LLMConfig(
            backend="ollama",
            model=os.getenv("LLM_MODEL", "llama3.1"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            # Ollama does not really use the key, but the client requires one
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
        )

    raise ValueError(f"Unsupported LLM_BACKEND: {backend}")


# ### Load MCP servers configuration from env (Part 2)
def load_mcp_server_configs() -> List[MCPServerConfig]:
    """
    For Part 2:
    - REQUIRE at least 2 external MCP servers (e.g. files + web)
    - REQUIRE your own local MCP server (my_mcp_server.py), exposed as 'local_insights'
    """

    servers: List[MCPServerConfig] = []
    external_count = 0

    # External server 1: filesystem
    files_args = os.getenv("MCP_FILES_ARGS")
    if files_args:
        servers.append(
            MCPServerConfig(
                name="files",
                command=os.getenv("MCP_FILES_CMD", "npx"),
                args=files_args.split(),
            )
        )
        external_count += 1

    # External server 2: web/search
    web_args = os.getenv("MCP_WEB_ARGS")
    if web_args:
        servers.append(
            MCPServerConfig(
                name="web",
                command=os.getenv("MCP_WEB_CMD", "npx"),
                args=web_args.split(),
            )
        )
        external_count += 1

    # Your own MCP server (MANDATORY for Part 2)
    local_args = os.getenv("MCP_LOCAL_ARGS")
    if not local_args:
        raise RuntimeError(
            "MCP_LOCAL_ARGS must be set for Part 2 and must point to your my_mcp_server.py.\n"
            "Example: MCP_LOCAL_CMD=python, MCP_LOCAL_ARGS=my_mcp_server.py"
        )

    servers.append(
        MCPServerConfig(
            name="local_insights",
            command=os.getenv("MCP_LOCAL_CMD", "python"),
            args=local_args.split(),
        )
    )

    # Enforce the '≥ 2 external + 1 local' rule
    if external_count < 2:
        raise RuntimeError(
            "You must configure at least 2 external MCP servers (e.g. files + web) "
            "in addition to your local_insights server."
        )

    return servers
