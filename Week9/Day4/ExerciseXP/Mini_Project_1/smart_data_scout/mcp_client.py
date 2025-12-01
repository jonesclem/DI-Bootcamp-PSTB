# smart_data_scout/mcp_client.py
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List

from mcp import ClientSession, types
from mcp.client.stdio import stdio_client, StdioServerParameters

from .config import MCPServerConfig
from .types import ToolDescriptor


@dataclass
class MCPClientManager:
    """
    Simple manager that can:
    - list tools across all configured MCP servers
    - call a specific tool on a specific server

    Each call creates a fresh stdio MCP session (simple and robust for a course project).
    """

    server_configs: Dict[str, MCPServerConfig]

    async def _with_session(self, server_name: str, coro_fn):
        cfg = self.server_configs[server_name]
        params = StdioServerParameters(
            command=cfg.command,
            args=cfg.args,
            env=cfg.env or None,
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await coro_fn(session)

    async def list_tools(self) -> List[ToolDescriptor]:
        """
        List tools from all configured MCP servers.

        Some servers return proper `types.Tool` objects.
        Others may return tuples like:
          - (Tool, extra_meta)
          - ("tool_id", {schema_dict})
          - ("tool_id", "description", {schema_dict})

        This function normalizes all of those into ToolDescriptor.
        """
        tools: List[ToolDescriptor] = []

        for name in self.server_configs.keys():

            async def _list(session: ClientSession):
                return await session.list_tools()

            server_tools = await self._with_session(name, _list)

            for t in server_tools:
                tool_name = ""
                description = ""
                input_schema: Dict[str, Any] = {}

                # Case 1: standard MCP Tool object
                if hasattr(t, "name"):
                    tool_name = t.name  # type: ignore[attr-defined]
                    description = getattr(t, "description", "") or ""
                    input_schema = getattr(t, "inputSchema", {}) or {}

                # Case 2: tuple shapes
                elif isinstance(t, tuple):
                    # e.g. (Tool, meta)
                    if len(t) >= 1 and hasattr(t[0], "name"):
                        tool = t[0]
                        tool_name = tool.name  # type: ignore[attr-defined]
                        description = getattr(tool, "description", "") or ""
                        input_schema = getattr(tool, "inputSchema", {}) or {}

                    # e.g. ("tool_id", {schema_dict})
                    elif len(t) >= 2 and isinstance(t[0], str) and isinstance(t[1], dict):
                        tool_name = t[0]
                        schema = t[1]
                        description = schema.get("description", "")
                        input_schema = schema

                    # e.g. ("tool_id", "description", {schema_dict})
                    elif (
                        len(t) >= 3
                        and isinstance(t[0], str)
                        and isinstance(t[1], str)
                        and isinstance(t[2], dict)
                    ):
                        tool_name = t[0]
                        description = t[1]
                        input_schema = t[2]
                    else:
                        # unknown tuple format; fall back to string representation
                        tool_name = str(t)

                # Fallback: unknown type
                else:
                    tool_name = str(t)

                tools.append(
                    ToolDescriptor(
                        server_name=name,
                        tool_name=tool_name,
                        description=description,
                        input_schema=input_schema,
                    )
                )

        return tools

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> List[types.TextContent]:
        """
        Call a single tool on a given server and return only TextContent items.
        """
        async def _call(session: ClientSession):
            return await session.call_tool(tool_name, arguments=arguments)

        result = await self._with_session(server_name, _call)
        contents: List[types.TextContent] = []
        for c in result.content:
            if isinstance(c, types.TextContent):
                contents.append(c)
        return contents


def get_mcp_manager_sync(server_configs: Dict[str, MCPServerConfig]) -> MCPClientManager:
    return MCPClientManager(server_configs)