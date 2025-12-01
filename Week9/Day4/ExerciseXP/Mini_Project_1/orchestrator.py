# Mini Project – MCP Agentic Application (Part 1 + Part 2)
# This module implements the agentic orchestrator:
# - Uses llm_client.py (Groq/Ollama) for planning and tool selection
# - Uses mcp_multi_client.py to call tools from:
#   * external MCP servers (Part 1): "files", "web"
#   * custom MCP server (Part 2): "local_insights" from my_mcp_server.py
# - Lets the LLM decide the order of multi-step tool calls based on intermediate results
# - Implements error handling, basic rate limiting, and detailed tool logs.
# app.py calls run_agent_sync(...) to run the full end-to-end agent.


from __future__ import annotations

import asyncio
import json
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List

from config import load_llm_config, load_mcp_server_configs
from llm_client import plan_with_llm
from mcp_multi_client import MCPMultiClient, ToolDescriptor


@dataclass
class ToolLogEntry:
    step: int
    tool_name: str
    server_name: str
    arguments: Dict[str, Any]
    success: bool
    result_preview: str
    error: str | None = None


@dataclass
class OrchestratorResult:
    final_answer: str
    tool_logs: List[ToolLogEntry] = field(default_factory=list)


class AgenticOrchestrator:
    """
    High-level autonomous agent:
    - Discovers tools from external MCP servers + custom `local_insights` server.
    - Lets the LLM choose which tools to call and in which order.
    - Robust to errors (tool failures / bad arguments / wrong schemas).
    - Provides transparent logs for debugging and assessment.
    """

    def __init__(self, max_steps: int = 8) -> None:
        self.max_steps = max_steps
        self.llm_cfg = load_llm_config()
        self.server_configs = load_mcp_server_configs()
        self.tool_logs: List[ToolLogEntry] = []

        # Rate-limiting (as requested by the corrector)
        self.tool_call_counts: Dict[str, int] = {}
        self.max_calls_per_tool: int = 5

    async def run(self, user_goal: str) -> OrchestratorResult:
        self.tool_logs.clear()

        async with MCPMultiClient(self.server_configs, debug=False) as mcp_client:
            tools_for_llm = mcp_client.build_llm_tools_spec()

            # High-level, non-scripted system prompt
            messages: List[Dict[str, Any]] = [
                {
                    "role": "system",
                    "content": (
                        "You are an autonomous agent that can use tools from multiple "
                        "MCP servers. Use the tools *only when helpful* to make progress.\n\n"
                        "Available server types:\n"
                        "- 'files' : listing, reading local files.\n"
                        "- 'web'   : searching the internet and fetching content.\n"
                        "- 'local_insights' : custom tools (clean_text, generate_insights).\n\n"
                        "Plan step by step. Choose tools based on their descriptions and "
                        "the user's goal. If a tool fails, adapt your strategy. "
                        "When you have enough information, provide a clear final answer."
                    ),
                },
                {
                    "role": "user",
                    "content": user_goal,
                },
            ]

            final_answer = ""

            for step in range(1, self.max_steps + 1):
                assistant_msg = plan_with_llm(messages, tools_for_llm)
                tool_calls = assistant_msg.get("tool_calls") or []

                # No tool call requested → final answer
                if not tool_calls:
                    content = assistant_msg.get("content") or ""
                    final_answer = (
                        content
                        if isinstance(content, str)
                        else json.dumps(content, ensure_ascii=False)
                    )
                    break

                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_msg.get("content") or "",
                        "tool_calls": tool_calls,
                    }
                )

                # Execute tool calls one by one
                for tc in tool_calls:
                    f_info = tc.get("function") or {}
                    tool_name = f_info.get("name")
                    raw_args = f_info.get("arguments") or "{}"
                    tool_call_id = tc.get("id", "")  # required for OpenAI-style tool messages

                    # Decode arguments
                    try:
                        args = (
                            json.loads(raw_args)
                            if isinstance(raw_args, str)
                            else raw_args
                        )
                        if not isinstance(args, dict):
                            raise ValueError("Tool arguments must be a JSON object.")
                    except Exception as e:
                        error_text = (
                            f"Invalid arguments for tool '{tool_name}': {raw_args}. "
                            f"Parse error: {e}"
                        )
                        self.tool_logs.append(
                            ToolLogEntry(
                                step=step,
                                tool_name=tool_name or "UNKNOWN",
                                server_name="UNKNOWN",
                                arguments={},
                                success=False,
                                result_preview="",
                                error=error_text,
                            )
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "name": tool_name,
                                "content": (
                                    "Arguments invalid. "
                                    + error_text
                                    + " Please replan with valid arguments."
                                ),
                            }
                        )
                        continue

                    # Validate against schema
                    td: ToolDescriptor | None = mcp_client.tools.get(tool_name)
                    server_name = td.server_name if td else "UNKNOWN"
                    required_fields = td.input_schema.get("required", []) if td else []

                    missing = [r for r in required_fields if r not in args]
                    if missing:
                        error_text = (
                            f"Missing required parameters for tool '{tool_name}': {missing}"
                        )
                        self.tool_logs.append(
                            ToolLogEntry(
                                step=step,
                                tool_name=tool_name,
                                server_name=server_name,
                                arguments=args,
                                success=False,
                                result_preview="",
                                error=error_text,
                            )
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "name": tool_name,
                                "content": (
                                    error_text
                                    + ". Adjust your call or choose another tool."
                                ),
                            }
                        )
                        continue

                    # Rate limiting
                    count = self.tool_call_counts.get(tool_name or "UNKNOWN", 0)
                    if count >= self.max_calls_per_tool:
                        error_text = (
                            f"Rate limit reached for tool '{tool_name}' "
                            f"({self.max_calls_per_tool}/run)."
                        )
                        self.tool_logs.append(
                            ToolLogEntry(
                                step=step,
                                tool_name=tool_name,
                                server_name=server_name,
                                arguments=args,
                                success=False,
                                result_preview="",
                                error=error_text,
                            )
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "name": tool_name,
                                "content": (
                                    error_text
                                    + " Please switch to another tool or strategy."
                                ),
                            }
                        )
                        continue

                    self.tool_call_counts[tool_name] = count + 1

                    # Execute tool
                    try:
                        result_str = await mcp_client.call_tool(tool_name, args)
                        preview = result_str[:800]

                        self.tool_logs.append(
                            ToolLogEntry(
                                step=step,
                                tool_name=tool_name,
                                server_name=server_name,
                                arguments=args,
                                success=True,
                                result_preview=preview,
                            )
                        )

                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "name": tool_name,
                                "content": preview,
                            }
                        )

                    except Exception as e:
                        tb = traceback.format_exc(limit=3)
                        error_text = (
                            f"Tool '{tool_name}' failed.\n"
                            f"Server: {server_name}\n"
                            f"Arguments: {args}\n"
                            f"Error: {e}\n"
                            f"Traceback:\n{tb}"
                        )
                        self.tool_logs.append(
                            ToolLogEntry(
                                step=step,
                                tool_name=tool_name,
                                server_name=server_name,
                                arguments=args,
                                success=False,
                                result_preview="",
                                error=error_text,
                            )
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "name": tool_name,
                                "content": (
                                    "Tool call failed.\n"
                                    + error_text
                                    + "\nReplan with a different strategy."
                                ),
                            }
                        )

            if not final_answer:
                final_answer = (
                    "I could not fully complete the task within the allowed steps. "
                    "Check the tool logs for intermediate results."
                )

            return OrchestratorResult(
                final_answer=final_answer,
                tool_logs=list(self.tool_logs),
            )


def run_agent_sync(user_goal: str) -> OrchestratorResult:
    orchestrator = AgenticOrchestrator()
    return asyncio.run(orchestrator.run(user_goal))
