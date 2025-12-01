# smart_data_scout/agent.py
import asyncio
import json
from typing import List, Tuple

from .llm_backends import LLMBackend, Message
from .mcp_client import MCPClientManager
from .planner import plan_next_action
from .logging_utils import log_tool_call
from .types import ToolCallLog, ToolDescriptor


async def run_agent_once(
    user_goal: str,
    llm: LLMBackend,
    mcp_manager: MCPClientManager,
    max_steps: int = 6,
) -> Tuple[str, List[ToolCallLog]]:
    """
    Run the agent for a single top-level goal.
    Returns (final_answer, tool_call_logs).
    """
    logs: List[ToolCallLog] = []
    history_summary = ""

    tools: List[ToolDescriptor] = await mcp_manager.list_tools()

    for step in range(1, max_steps + 1):
        action = plan_next_action(llm, user_goal, history_summary, tools)

        if action.action == "finish":
            system = (
                "You are Smart Data Scout. Use the history of tool calls to provide "
                "a clear final answer to the user's goal. If tools failed or were "
                "insufficient, explain the limitations."
            )
            messages: List[Message] = [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Goal: {user_goal}\n\nHistory:\n{history_summary}"},
            ]
            final_answer = llm.chat(messages)
            return final_answer, logs

        server_name = action.server_name
        tool_name = action.tool_name
        arguments = action.arguments or {}

        if not server_name or not tool_name:
            final_answer = (
                "Planner produced an invalid tool action (missing server_name/tool_name). "
                f"I will stop. Planner reasoning: {action.reasoning}"
            )
            return final_answer, logs

        try:
            contents = await mcp_manager.call_tool(server_name, tool_name, arguments)
            joined_text = "\n".join(c.text for c in contents)
            summary = joined_text[:500] + ("..." if len(joined_text) > 500 else "")

            log = ToolCallLog(
                step=step,
                server_name=server_name,
                tool_name=tool_name,
                arguments=arguments,
                success=True,
                summary=summary,
            )
            logs.append(log)
            log_tool_call(log)

            history_summary += (
                f"\n\nSTEP {step}: Called {server_name}.{tool_name} with args "
                f"{json.dumps(arguments)}.\nRESULT SNIPPET:\n{summary}\n"
            )

        except Exception as exc:  # noqa: BLE001
            err_msg = str(exc)
            log = ToolCallLog(
                step=step,
                server_name=server_name,
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                summary="Tool call failed",
                error=err_msg,
            )
            logs.append(log)
            log_tool_call(log)

            history_summary += (
                f"\n\nSTEP {step}: Tool {server_name}.{tool_name} failed with error: {err_msg}\n"
            )

            # Let the planner see the error on the next step and adapt.
            continue

    # max_steps exhausted: summarize what we have
    system = (
        "You are Smart Data Scout. The tool loop reached its maximum number of steps. "
        "Summarize what was learned and what remains uncertain."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Goal: {user_goal}\n\nHistory:\n{history_summary}"},
    ]
    final_answer = llm.chat(messages)
    return final_answer, logs


def run_agent_sync(
    user_goal: str,
    llm: LLMBackend,
    mcp_manager: MCPClientManager,
    max_steps: int = 6,
) -> Tuple[str, List[ToolCallLog]]:
    return asyncio.run(run_agent_once(user_goal, llm, mcp_manager, max_steps=max_steps))