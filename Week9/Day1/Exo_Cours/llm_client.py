"""
Minimal Gemini-backed MCP client for the stock price server.

Usage:
  GEMINI_API_KEY=... python llm_client.py
Optional flags:
  --model gemini-1.5-flash
  --server-path path/to/mcp_server.py
Type 'exit' or Ctrl+C to quit.
"""

from __future__ import annotations

import argparse
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import anyio
import google.generativeai as genai
from mcp.client.session import ClientSession
from mcp.shared.message import SessionMessage
import mcp.types as types
import subprocess

ROOT = Path(__file__).resolve().parent

# JSON Schema keys that Gemini's Schema proto does not support.
UNSUPPORTED_SCHEMA_KEYS = {
    "title",
    "$schema",
    "examples",
    "default",
    "deprecated",
    "readOnly",
    "writeOnly",
}


def _clean_schema(obj: Any) -> Any:
    """
    Recursively remove JSON Schema fields that Gemini's Schema proto
    does not support (e.g. 'title').
    """
    if isinstance(obj, dict):
        return {
            k: _clean_schema(v)
            for k, v in obj.items()
            if k not in UNSUPPORTED_SCHEMA_KEYS
        }
    if isinstance(obj, list):
        return [_clean_schema(v) for v in obj]
    return obj


def _as_gemini_tools(tools: list[Any]) -> list[dict[str, Any]]:
    """Convert MCP tools to Gemini function declarations."""
    declarations: list[dict[str, Any]] = []
    for tool in tools:
        params = tool.inputSchema or {"type": "object", "properties": {}}
        if hasattr(params, "model_dump"):
            params = params.model_dump()

        params = _clean_schema(params)

        declarations.append(
            {
                "name": tool.name,
                "description": tool.description or getattr(tool, "title", "") or "",
                "parameters": params,
            }
        )

    # google.generativeai expects a list of tools with function_declarations
    return [{"function_declarations": declarations}]


def _format_tool_result(result) -> str:
    """Flatten CallToolResult content into text."""
    parts: list[str] = []
    for block in result.content:
        block_type = getattr(block, "type", None)
        if block_type == "text":
            parts.append(block.text)
        elif block_type == "resource_link":
            title = f" ({block.title})" if block.title else ""
            parts.append(f"[resource link] {block.uri}{title}")
        elif block_type == "resource":
            resource = block.resource
            if hasattr(resource, "text") and resource.text is not None:
                parts.append(resource.text)
            elif hasattr(resource, "blob") and resource.blob is not None:
                parts.append(f"[binary resource {resource.mimeType or 'unknown'}]")
            else:
                parts.append(str(resource))
        else:
            parts.append(str(block))
    return "\n".join(parts)


@asynccontextmanager
async def connect_to_server(server_path: Path):
    """Spawn the MCP server over stdio (blocking pipes) and yield a ready session."""
    env = os.environ.copy()
    env.update(
        {
            "PYTHONUNBUFFERED": "1",
            "FASTMCP_DEBUG": "true",
            "FASTMCP_LOG_LEVEL": "DEBUG",
        }
    )

    proc = subprocess.Popen(
        [sys.executable, str(server_path)],
        cwd=str(server_path.parent),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        text=True,
        env=env,
    )

    # Two in-memory channels:
    #   server_stdout -> client: server_to_client_send/server_to_client_recv
    #   client -> server_stdin: client_to_server_send/client_to_server_recv
    server_to_client_send, server_to_client_recv = anyio.create_memory_object_stream(0)
    client_to_server_send, client_to_server_recv = anyio.create_memory_object_stream(0)

    async def forward_stdout():
        try:
            while True:
                line = await anyio.to_thread.run_sync(proc.stdout.readline)  # type: ignore[arg-type]
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = types.JSONRPCMessage.model_validate_json(line)
                    await server_to_client_send.send(SessionMessage(msg))
                except Exception as exc:  # noqa: BLE001
                    await server_to_client_send.send(exc)
        finally:
            await server_to_client_send.aclose()

    async def forward_stdin():
        try:
            async with client_to_server_recv:
                async for session_message in client_to_server_recv:
                    data = (
                        session_message.message.model_dump_json(
                            by_alias=True, exclude_none=True
                        )
                        + "\n"
                    )
                    await anyio.to_thread.run_sync(proc.stdin.write, data)  # type: ignore[arg-type]
                    await anyio.to_thread.run_sync(proc.stdin.flush)  # type: ignore[arg-type]
        finally:
            if proc.stdin:
                proc.stdin.close()

    async with anyio.create_task_group() as tg:
        tg.start_soon(forward_stdout)
        tg.start_soon(forward_stdin)

        # ClientSession reads from server_to_client_recv and writes to client_to_server_send
        session = ClientSession(server_to_client_recv, client_to_server_send)
        await session.__aenter__()
        await session.initialize()
        try:
            yield session
        finally:
            await session.__aexit__(None, None, None)
            tg.cancel_scope.cancel()
            if proc.poll() is None:
                proc.terminate()


async def call_mcp_tool(session: ClientSession, name: str, arguments: dict[str, Any]) -> str:
    result = await session.call_tool(name=name, arguments=arguments)
    text = _format_tool_result(result)
    if result.isError:
        return f"[tool error]\n{text}"
    return text


async def send_user_and_maybe_call_tool(chat, user_text: str, session: ClientSession) -> str:
    """
    Send a user message to Gemini, handle at most one round of tool calls, and return the final text reply.
    """
    # Gemini client is synchronous; run it off-thread.
    response = await anyio.to_thread.run_sync(chat.send_message, user_text)

    # Prefer response.function_calls if available (newer SDKs).
    function_calls = list(getattr(response, "function_calls", []) or [])

    # Fallback: scan parts for function_call entries with a non-empty name.
    if not function_calls:
        parts = getattr(response, "parts", None)
        if not parts and getattr(response, "candidates", None):
            try:
                parts = response.candidates[0].content.parts
            except Exception:
                parts = None
        parts = parts or []
        for p in parts:
            fc = getattr(p, "function_call", None)
            name = getattr(fc, "name", None) if fc is not None else None
            if fc is not None and name:
                function_calls.append(fc)

    # If there are no valid function calls, just return the model's text.
    if not function_calls:
        return getattr(response, "text", "") or ""

    # Handle each function call once.
    for fc in function_calls:
        name = getattr(fc, "name", None)
        if not name:
            # Skip invalid/empty names to avoid 400 errors and MCP warnings.
            continue

        args = dict(getattr(fc, "args", {}) or {})
        tool_output = await call_mcp_tool(session, name, args)

        # Send the function result back to Gemini for a final answer.
        response = await anyio.to_thread.run_sync(
            chat.send_message,
            {
                "function_response": {
                    "name": name,
                    "response": {"result": tool_output},
                }
            },
        )

    return getattr(response, "text", "") or ""


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gemini-backed MCP client for the stock server."
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        help="Gemini model to use.",
    )
    parser.add_argument(
        "--server-path",
        type=Path,
        default=ROOT / "mcp_server.py",
        help="Path to the MCP server file to run.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Please set GEMINI_API_KEY in your environment.")
        sys.exit(1)

    genai.configure(api_key=api_key)

    print("Connecting to MCP server...")
    async with connect_to_server(args.server_path) as session:
        tools_response = await session.list_tools()
        gemini_tools = _as_gemini_tools(tools_response.tools)
        print("Connected. Available tools:", ", ".join(tool.name for tool in tools_response.tools))

        model = genai.GenerativeModel(
            args.model,
            tools=gemini_tools,
            system_instruction="You are an assistant that uses MCP tools to answer stock questions.",
        )
        chat = model.start_chat(history=[])

        while True:
            try:
                user_text = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if user_text.lower() in {"exit", "quit"}:
                break

            try:
                reply = await send_user_and_maybe_call_tool(chat, user_text, session)
            except Exception as exc:
                reply = f"Error: {exc}"
            print(f"Assistant: {reply}")


if __name__ == "__main__":
    anyio.run(main)
