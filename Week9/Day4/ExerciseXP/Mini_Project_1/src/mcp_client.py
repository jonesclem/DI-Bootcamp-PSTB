"""
Thin MCP client wrapper.

- Starts each MCP server over stdio using commands from Config.
- Calls a given tool with arguments.
- Uses the official MCP client pattern (async with ClientSession).
"""

from __future__ import annotations

import asyncio
import logging
import shlex
from dataclasses import dataclass
from typing import Any, Dict

import mcp
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.types import CallToolResult

from config import Config


@dataclass
class MCPToolCallResult:
    """
    Normalized result of a tool call, used by the agent and UI.
    """
    success: bool
    text: str | None
    error: str | None


class MCPClient:
    """
    Small helper around the MCP stdio client.

    It knows how to:
    - Map logical server names ("fetch", "filesystem", "kb_metadata")
      to command lines from Config.
    - Start the server via stdio.
    - Call a tool with JSON arguments.
    """

    def __init__(self, config: Config, logger: logging.Logger | None = None):
        self.config = config
        self.log = logger or logging.getLogger(__name__)

    def _server_params_for(self, server: str) -> StdioServerParameters:
        """
        Build StdioServerParameters for the requested server.

        We take the shell command line from Config (e.g. "uvx mcp-server-fetch"),
        split it into:
          - command: first token ("uvx")
          - args: remaining tokens (["mcp-server-fetch"])
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

        # Helpful debug when servers start
        print(f"[mcp_client] Starting MCP server '{server}' with command: {command} {args}")

        return StdioServerParameters(command=command, args=args)

    async def _async_call_tool(
        self,
        server: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> MCPToolCallResult:
        """
        Async part: start server, call tool, capture output.

        Follows the official MCP stdio client pattern:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    ...
        """
        params = self._server_params_for(server)

        async with stdio_client(params) as (read, write):
            # Official pattern: use ClientSession as an async context manager
            async with mcp.ClientSession(read, write) as session:
                print(f"[mcp_client] Initializing MCP session for server '{server}'")
                await session.initialize()
                print(f"[mcp_client] MCP session initialized for server '{server}'")

                # List tools and ensure the requested tool exists
                tools = await session.list_tools()
                tool_names = [t.name for t in tools.tools]
                print(f"[mcp_client] Tools on server '{server}': {tool_names}")

                if tool_name not in tool_names:
                    return MCPToolCallResult(
                        success=False,
                        text=None,
                        error=f"Tool '{tool_name}' not found on server '{server}'. Available: {tool_names}",
                    )

                print(f"[mcp_client] Calling tool '{tool_name}' on server '{server}' with args={arguments!r}")
                result: CallToolResult = await session.call_tool(tool_name, arguments)
                print(f"[mcp_client] Tool '{tool_name}' call completed on server '{server}'")

                # Extract plain text from the result content
                text_chunks: list[str] = []
                for item in result.content or []:
                    val = getattr(item, "text", None)
                    if isinstance(val, str):
                        text_chunks.append(val)

                print(f"[mcp_client] Closing MCP session for server '{server}'")

        # async with blocks handle closing session and transport
        text = "\n".join(text_chunks) if text_chunks else None
        return MCPToolCallResult(success=True, text=text, error=None)

    def call_tool(self, server: str, tool_name: str, arguments: Dict[str, Any]) -> MCPToolCallResult:
        """
        Synchronous wrapper used by the agent.

        It runs the async call and catches any unexpected exceptions so that
        the agent can log them instead of crashing.
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