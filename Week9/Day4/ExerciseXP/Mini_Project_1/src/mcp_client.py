"""
MCP client wrapper.

Responsibilities:
- Start MCP servers via stdio using commands from the Config.
- Call tools on those servers (with arguments).
- Discover tools at runtime so the agent can build a dynamic tool catalog.

This is a small wrapper over the official MCP Python client APIs.
"""

from __future__ import annotations

import asyncio
import logging
import shlex
from dataclasses import dataclass
from typing import Any, Dict, List

import mcp
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.types import CallToolResult

from config import Config


@dataclass
class MCPToolCallResult:
    """
    Normalized result of a tool call.

    The agent only needs:
    - whether it succeeded,
    - any text output, and
    - a human-readable error string if it failed.
    """
    success: bool
    text: str | None
    error: str | None


@dataclass
class MCPToolInfo:
    """
    Minimal view of an MCP tool.

    Used to build a tool catalog to show the LLM what is available,
    instead of hardcoding tool names in the prompt.
    """
    server: str
    name: str
    description: str | None


class MCPClient:
    """
    Thin wrapper around MCP stdio client.

    Each call spins up one MCP server process over stdio, interacts
    with it (initialize → list_tools / call_tool), then exits.
    """

    def __init__(self, config: Config, logger: logging.Logger | None = None):
        self.config = config
        self.log = logger or logging.getLogger(__name__)

    def _server_params_for(self, server: str) -> StdioServerParameters:
        """
        Build StdioServerParameters from a logical server name.

        Server names:
        - "fetch"       → third-party mcp-server-fetch
        - "filesystem"  → third-party server-filesystem
        - "kb_metadata" → local custom MCP server
        """
        if server == "fetch":
            cmdline = self.config.fetch_cmd
        elif server == "filesystem":
            cmdline = self.config.filesystem_cmd
        elif server == "kb_metadata":
            cmdline = self.config.kb_metadata_cmd
        else:
            raise ValueError(f"Unknown MCP server name: {server}")

        parts = shlex.split(cmdline)
        if not parts:
            raise ValueError(f"Empty command for server '{server}' (cmdline: {cmdline!r})")

        command = parts[0]
        args = parts[1:]
        print(f"[mcp_client] Starting MCP server '{server}' with command: {command} {args}")
        return StdioServerParameters(command=command, args=args)

    async def _async_call_tool(
        self,
        server: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> MCPToolCallResult:
        """
        Async implementation of calling a single tool on a given server.

        Steps:
        - Start server via stdio.
        - Initialize MCP session.
        - List tools and check that the requested one exists.
        - Call the tool with the given arguments.
        - Collect plain text output.
        """
        params = self._server_params_for(server)

        async with stdio_client(params) as (read, write):
            async with mcp.ClientSession(read, write) as session:
                print(f"[mcp_client] Initializing MCP session for server '{server}'")
                await session.initialize()
                print(f"[mcp_client] MCP session initialized for server '{server}'")

                tools = await session.list_tools()
                tool_names = [t.name for t in tools.tools]
                print(f"[mcp_client] Tools on server '{server}': {tool_names}")
                if tool_name not in tool_names:
                    return MCPToolCallResult(
                        success=False,
                        text=None,
                        error=f"Tool '{tool_name}' not found on '{server}'. Available: {tool_names}",
                    )

                print(f"[mcp_client] Calling tool '{tool_name}' on server '{server}' with args={arguments!r}")
                result: CallToolResult = await session.call_tool(tool_name, arguments)
                print(f"[mcp_client] Tool '{tool_name}' call completed on server '{server}'")

                text_chunks: list[str] = []
                for item in result.content or []:
                    val = getattr(item, "text", None)
                    if isinstance(val, str):
                        text_chunks.append(val)

                text = "\n".join(text_chunks) if text_chunks else None
                print(f"[mcp_client] Closing MCP session for server '{server}'")

        return MCPToolCallResult(success=True, text=text, error=None)

    async def _async_list_tools_for_server(self, server: str) -> List[MCPToolInfo]:
        """
        Async helper: list tools for one server and normalize them as MCPToolInfo.
        """
        params = self._server_params_for(server)
        results: List[MCPToolInfo] = []

        async with stdio_client(params) as (read, write):
            async with mcp.ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                for t in tools.tools:
                    results.append(
                        MCPToolInfo(
                            server=server,
                            name=t.name,
                            description=getattr(t, "description", None),
                        )
                    )
        return results

    def call_tool(self, server: str, tool_name: str, arguments: Dict[str, Any]) -> MCPToolCallResult:
        """
        Synchronous wrapper used by the agent.

        It runs the async tool call and converts any unexpected exceptions
        into a failed MCPToolCallResult, so the agent can display them.
        """
        try:
            return asyncio.run(self._async_call_tool(server, tool_name, arguments))
        except Exception as exc:
            if self.log:
                self.log.error(
                    f"Error calling MCP tool {server}.{tool_name} with args={arguments!r}",
                    exc_info=True,
                )
            return MCPToolCallResult(
                success=False,
                text=None,
                error=str(exc),
            )

    def discover_tools(self, servers: List[str]) -> List[MCPToolInfo]:
        """
        Discover tools across a list of servers.

        This supports the "planning" requirement: rather than hard-coding
        tool names, we show the LLM a catalog of what is actually available.
        """
        collected: List[MCPToolInfo] = []
        for s in servers:
            try:
                tools = asyncio.run(self._async_list_tools_for_server(s))
                collected.extend(tools)
            except Exception as exc:
                if self.log:
                    self.log.warning(f"Failed to list tools for server '{s}': {exc}")
        return collected