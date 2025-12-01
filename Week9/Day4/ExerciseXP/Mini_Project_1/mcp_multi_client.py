# Mini Project – MCP Agentic Application (Part 1 + Part 2)
# This module implements a unified MCP multi-server client:
# - Connects to external MCP servers from Part 1 (e.g. "files", "web")
# - Connects to the student's OWN MCP server from Part 2 ("local_insights")
#   which is implemented in my_mcp_server.py
# - Discovers all tools and exposes them to the LLM under names like:
#   "files__listDirectory", "web__search", "local_insights__clean_text", etc.
# It is used by orchestrator.py to actually execute tool calls chosen by the LLM.


# ### Async MCP multi-server client utilisant le me MCP officiel de Python SDK
#
# Ce client se connecte à :
# - des serveurs MCP externes (ex: 'files', 'web')
# - ton propre serveur MCP 'local_insights' (défini dans my_mcp_server.py)
#
# Il découvre tous les outils et les expose au LLM sous la forme :
#   <server_name>__<tool_name>
# ex : local_insights__clean_text, files__listDirectory, web__search, etc.

from __future__ import annotations

from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

from config import MCPServerConfig, load_mcp_server_configs


@dataclass
class ToolDescriptor:
    """Metadata for a tool, mapped to an LLM-exposed name."""
    llm_name: str          # ex: "local_insights__clean_text"
    server_name: str       # ex: "local_insights"
    tool_name: str         # ex: "clean_text"
    description: str
    input_schema: Dict[str, Any]


class MCPMultiClient:
    """
    Manage plusieurs sessions MCP en même temps :
    - démarre les serveurs via stdio (command + args)
    - initialise les sessions MCP
    - découvre tous les outils
    - fournit une API unifiée pour appeler un outil par son nom LLM (namespacé)
    """

    def __init__(
        self,
        server_configs: Optional[List[MCPServerConfig]] = None,
        debug: bool = False,
    ) -> None:
        # Si pas de config fournie, on charge depuis les variables d'env
        self.server_configs = server_configs or load_mcp_server_configs()
        self._exit_stack: Optional[AsyncExitStack] = None
        self.sessions: Dict[str, ClientSession] = {}
        self.tools: Dict[str, ToolDescriptor] = {}
        self.debug = debug

    async def __aenter__(self) -> "MCPMultiClient":
        self._exit_stack = AsyncExitStack()

        # Démarrage et initialisation de chaque serveur MCP
        for cfg in self.server_configs:
            if self.debug:
                print(f"[MCP] Starting server '{cfg.name}' → {cfg.command} {' '.join(cfg.args)}")

            server_params = StdioServerParameters(
                command=cfg.command,
                args=cfg.args,
                env=cfg.env,
            )

            read_stream, write_stream = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )

            session = ClientSession(read_stream, write_stream)
            await session.initialize()
            self.sessions[cfg.name] = session

        # Découverte des outils sur chaque serveur
        await self._discover_tools()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._exit_stack is not None:
            await self._exit_stack.aclose()
        self.sessions.clear()
        self.tools.clear()

    async def _discover_tools(self) -> None:
        """Discover tools on all MCP servers and build a registry."""
        for server_name, session in self.sessions.items():
            result: types.ListToolsResult = await session.list_tools()

            if self.debug:
                print(f"[MCP] Server '{server_name}' exposes {len(result.tools)} tools")

            for tool in result.tools:
                llm_name = f"{server_name}__{tool.name}"

                input_schema = tool.inputSchema or {
                    "type": "object",
                    "properties": {},
                    "required": [],
                }

                td = ToolDescriptor(
                    llm_name=llm_name,
                    server_name=server_name,
                    tool_name=tool.name,
                    description=tool.description or "",
                    input_schema=input_schema,
                )

                self.tools[llm_name] = td

                if self.debug:
                    print(
                        f"  → Registered tool '{llm_name}' "
                        f"(server={server_name}, original={tool.name})"
                    )

    def build_llm_tools_spec(self) -> List[Dict[str, Any]]:
        """
        Convertit les outils MCP en schéma de tools 'function calling' OpenAI-compatible.

        Ce résultat est passé à l'LLM dans `tools=...` pour permettre à l'LLM
        de planifier des tool_calls.
        """
        tools_for_llm: List[Dict[str, Any]] = []

        for td in self.tools.values():
            schema = td.input_schema or {
                "type": "object",
                "properties": {},
                "required": [],
            }
            tools_for_llm.append(
                {
                    "type": "function",
                    "function": {
                        "name": td.llm_name,
                        "description": td.description,
                        "parameters": schema,
                    },
                }
            )

        if self.debug:
            print(f"[MCP] Built LLM tools spec with {len(tools_for_llm)} tools")

        return tools_for_llm

    async def call_tool(self, llm_tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Appelle un outil via son nom LLM (namespacé).
        Exemple : "local_insights__generate_insights"
        """
        td = self.tools.get(llm_tool_name)
        if not td:
            raise ValueError(f"Unknown tool name from LLM: '{llm_tool_name}'")

        session = self.sessions.get(td.server_name)
        if not session:
            raise RuntimeError(
                f"No active MCP session for server '{td.server_name}' "
                f"(tool '{llm_tool_name}')."
            )

        if self.debug:
            print(f"[MCP] Calling '{llm_tool_name}' on server '{td.server_name}' with args={arguments}")

        result = await session.call_tool(td.tool_name, arguments=arguments)

        # Flatten text content from MCP result
        parts: List[str] = []
        for item in result.content:
            if hasattr(item, "text"):
                parts.append(item.text)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))

        output = "\n".join(parts)

        if self.debug:
            preview = output[:200].replace("\n", " ")
            print(f"[MCP] Result from '{llm_tool_name}': {preview}...")

        return output
