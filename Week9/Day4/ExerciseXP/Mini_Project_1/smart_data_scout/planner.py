# smart_data_scout/planner.py
import json
from textwrap import dedent
from typing import List

from .llm_backends import LLMBackend, Message
from .types import PlannedAction, ToolDescriptor


def _tools_block(tools: List[ToolDescriptor]) -> str:
    lines: List[str] = []
    for t in tools:
        props = t.input_schema.get("properties", {})
        lines.append(
            f"- server: {t.server_name}\n"
            f"  tool: {t.tool_name}\n"
            f"  description: {t.description}\n"
            f"  input_properties: {json.dumps(props)}"
        )
    return "\n".join(lines)


def plan_next_action(
    llm: LLMBackend,
    user_goal: str,
    history_summary: str,
    tools: List[ToolDescriptor],
) -> PlannedAction:
    """
    Ask the LLM to pick the next tool call (or finish).
    """

    system_prompt = dedent(
        """
        You are the orchestration brain of the Smart Data Scout agent.

        You have multiple MCP servers:

        - web-search: duckduckgo-mcp-server
          Provides DuckDuckGo web search and content fetching in an LLM-friendly format. :contentReference[oaicite:5]{index=5}

        - csv-editor: CSV Editor by santoshray02
          Provides 40+ CSV tools for loading, cleaning, transforming, analyzing, and validating CSV data
          (load_csv_from_url, remove_duplicates, fill_missing_values, get_statistics, get_correlation_matrix, etc.). :contentReference[oaicite:6]{index=6}

        - insights: custom
          Converts structured CSV/analysis results into stakeholder-ready insights.

        Your job:
        - choose which tool to call next and with what arguments, OR
        - decide we are done and return a final answer.

        ALWAYS respond with a single JSON object:

        {
          "action": "tool" | "finish",
          "server_name": "web-search" | "csv-editor" | "insights",
          "tool_name": "name-of-tool",
          "arguments": { ... },
          "reasoning": "short explanation"
        }

        Rules:
        - Use web-search when you need to discover public data sources or CSV URLs.
        - Use csv-editor for loading, cleaning, transforming, and analyzing CSV data.
        - Use insights to generate high-level insights and summaries from CSV snippets or stats.
        - Prefer multiple small steps over one huge step.
        - Arguments must be valid JSON matching the tools' input schemas.
        """
    ).strip()

    tools_text = _tools_block(tools)
    user_content = dedent(
        f"""
        USER GOAL:
        {user_goal}

        HISTORY SUMMARY:
        {history_summary or "(no previous steps)"}

        AVAILABLE TOOLS:
        {tools_text}

        Decide the next step and output ONLY a JSON object, with no extra text.
        """
    ).strip()

    messages: List[Message] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]
    raw = llm.chat(messages)
    text = raw.strip()

    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return PlannedAction(
            action="finish",
            reasoning=f"Planner JSON parse failed. Raw reply: {raw}",
        )

    action = data.get("action", "finish")
    if action not in ("tool", "finish"):
        action = "finish"

    return PlannedAction(
        action=action,  # type: ignore[arg-type]
        server_name=data.get("server_name"),
        tool_name=data.get("tool_name"),
        arguments=data.get("arguments") or {},
        reasoning=data.get("reasoning"),
    )