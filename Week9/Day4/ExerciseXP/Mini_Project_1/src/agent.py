"""
Planning agent that uses Groq + MCP to build a small research pipeline.

Core responsibilities:
- Use Groq to decide which MCP tool to call next (planning).
- Call third-party MCP servers (fetch, filesystem) and a local one (kb_metadata).
- Handle errors and retries.
- Log each tool call so the UI can show a clear execution trace.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

from config import Config
from llm_groq import chat as groq_chat
from mcp_client import MCPClient, MCPToolCallResult, MCPToolInfo


@dataclass
class StepLog:
    """
    Per-step log used by Streamlit to visualize the agent's behavior.
    """
    step: int
    action: str
    server: str | None
    tool: str | None
    args: Dict[str, Any] | None
    success: bool
    error: str | None
    output_snippet: str


def _extract_first_json_object(text: str) -> Dict[str, Any] | None:
    """
    Try to extract the first {...} JSON object from a string.

    Some models wrap JSON in extra text; this lets us recover the object
    without forcing the model to be perfect.
    """
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except Exception:
                    return None
    return None


def _llm_chat(config: Config, messages: List[Dict[str, str]]) -> str:
    """
    Helper to call Groq using the given config.
    """
    return groq_chat(
        base_url=config.groq_base_url,
        model=config.groq_model,
        api_key=config.groq_api_key,
        messages=messages,
    )


class ResearchAgent:
    """
    Main orchestrator for the mini project.

    Flow:
    - Build a tool catalog by discovering tools from MCP servers.
    - Use the LLM to decide the next action in each step.
    - Apply a simple retry loop on tool failures.
    - At the end, summarize the findings into a markdown answer.

    Additional constraint for the mini-project:
    - The FIRST tool call must use the "fetch" server at least once,
      so that the integration of that third-party MCP server is always visible.
    """

    def __init__(self, config: Config, mcp_client: MCPClient, logger: logging.Logger | None = None):
        self.config = config
        self.mcp_client = mcp_client
        self.log = logger or logging.getLogger(__name__)

        # Logical server names we support in this project.
        self.server_names = ["fetch", "filesystem", "kb_metadata"]

        # Discover tools dynamically so we can show the model what exists.
        self.tool_catalog: List[MCPToolInfo] = self.mcp_client.discover_tools(self.server_names)

    def _tool_catalog_text(self) -> str:
        """
        Render the tool catalog into a short text snippet for the LLM.
        """
        if not self.tool_catalog:
            return "(no tools discovered)"
        lines: List[str] = []
        for t in self.tool_catalog:
            desc = t.description or ""
            lines.append(f"- server={t.server}, tool={t.name}: {desc}")
        return "\n".join(lines)

    def _ask_model_for_plan(
        self,
        user_goal: str,
        history_summary: str,
        must_call_tool: bool,
        must_use_fetch_first: bool,
    ) -> Dict[str, Any]:
        """
        Ask Groq what to do next.

        The model:
        - Sees the available tools (from discovery).
        - Sees a short summary of previous steps.
        - Must reply with ONE JSON object describing either:
          - a tool call, or
          - a final markdown answer ("finish").

        Extra constraints:
        - If must_call_tool is True, the model is not allowed to "finish".
        - If must_use_fetch_first is True, the model MUST choose server="fetch"
          for THIS step (e.g. for the first tool call in the workflow).
        """
        tools_text = self._tool_catalog_text()

        base_system_msg = f"""
You are an MCP planning agent.

You have access to multiple MCP servers and tools. These were discovered at runtime:

{tools_text}

Your job is to decide the NEXT ACTION in a multi-step workflow.

You MUST respond with EXACTLY ONE JSON object, and NOTHING else.
No natural language, no explanations, no code fences, no comments.

Valid response schemas:

1) To CALL A TOOL:

{{
  "action": "call_tool",
  "server": "<server_name>",
  "tool": "<tool_name>",
  "args": {{ ... }}
}}

2) To FINISH:

{{
  "action": "finish",
  "answer": "<final_markdown_answer>"
}}

Rules:
- "action" is "call_tool" or "finish".
- "server" must match one of the discovered servers.
- "tool" must match a tool exposed by that server.
- "args" should contain only arguments expected by that tool.
- "answer" is a short markdown string when finishing.

Workflow guidelines for this app:
- Typically:
  1) Use a fetch-like tool on server "fetch" to retrieve web content.
  2) Use a filesystem-like tool to write a markdown note file.
  3) Use a metadata-like tool to register that note in a KB.
  4) Then FINISH with a short summary.

Error handling:
- Use the history summary to see previous errors and avoid repeating
  the exact same failing call.
""".strip()

        if must_call_tool:
            # Enforce at least one tool call overall.
            base_system_msg += "\nFor THIS step you are NOT allowed to use action 'finish'. You MUST use 'call_tool'."

        if must_use_fetch_first:
            # Enforce that the first tool call uses the "fetch" server.
            base_system_msg += (
                "\nFor THIS step you MUST choose server='fetch' for the tool call, "
                "to retrieve some web content before writing files or metadata."
            )

        user_msg = f"""
User goal:
{user_goal}

Recent tool history:
{history_summary}

Respond ONLY with ONE JSON object following the schemas above.
""".strip()

        raw = _llm_chat(
            self.config,
            [
                {"role": "system", "content": base_system_msg},
                {"role": "user", "content": user_msg},
            ],
        ).strip()

        # Sometimes models wrap JSON in ```json fences; strip them defensively.
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()

        # Try direct JSON parse first; fall back to first-object extraction.
        try:
            plan = json.loads(raw)
        except Exception:
            plan = _extract_first_json_object(raw)

        if plan is None:
            self.log.warning("Failed to parse JSON; forcing finish.")
            return {"action": "finish", "answer": raw}

        if not isinstance(plan, dict) or "action" not in plan:
            self.log.warning("JSON without 'action'; forcing finish.")
            return {"action": "finish", "answer": json.dumps(plan, indent=2)}

        return plan

    def _summarize_logs(self, logs: List[StepLog]) -> str:
        """
        Create a compact summary of recent tool calls for the LLM.
        """
        if not logs:
            return "(no tool calls yet)"
        parts: List[str] = []
        for log in logs[-5:]:
            status = "ok" if log.success else f"error: {log.error}"
            snippet = (log.output_snippet or "").replace("\n", " ")
            if len(snippet) > 150:
                snippet = snippet[:150] + "..."
            parts.append(
                f"Step {log.step}: {log.server}.{log.tool}, status={status}, output={snippet}"
            )
        return "\n".join(parts)

    def _call_tool(self, server: str, tool: str, args: Dict[str, Any]) -> MCPToolCallResult:
        """
        Call an MCP tool with a small retry loop and logging.

        - Removes None-valued args.
        - Logs inputs and outputs.
        - Retries a few times based on config.max_tool_retries.
        """
        cleaned_args = {k: v for k, v in args.items() if v is not None}
        attempts = max(1, self.config.max_tool_retries)
        last: MCPToolCallResult | None = None

        for attempt in range(1, attempts + 1):
            self.log.info(
                f"MCP call -> server={server} tool={tool} attempt={attempt} args={cleaned_args!r}"
            )
            last = self.mcp_client.call_tool(server, tool, cleaned_args)
            if last.success:
                self.log.info(
                    f"MCP result <- server={server} tool={tool} success=True "
                    f"len(text)={len(last.text or '')}"
                )
                return last

            self.log.warning(
                f"MCP result <- server={server} tool={tool} success=False error={last.error!r}"
            )

        return last  # type: ignore[return-value]

    def _summarize_final_answer(self, user_goal: str, logs: List[StepLog]) -> str:
        """
        Fallback: if the planner never produced a 'finish' action, ask
        Groq to summarize the tool history into a markdown answer.
        """
        sys_msg = "You are a summarizer. Do NOT call tools. Only write a short markdown answer."
        user_msg = f"""
User goal:
{user_goal}

Tool history:
{self._summarize_logs(logs)}

Summarize the findings in markdown.
""".strip()

        return _llm_chat(
            self.config,
            [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg},
            ],
        ).strip()

    def run_research(self, user_goal: str, max_steps: int = 5) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Main entry point used by the Streamlit UI.

        Returns:
            final_answer_markdown, list_of_step_logs_as_dicts
        """
        logs: List[StepLog] = []
        used_tool = False
        used_fetch = False
        final_answer = "No answer produced."

        for step in range(1, max_steps + 1):
            history_summary = self._summarize_logs(logs)

            plan = self._ask_model_for_plan(
                user_goal=user_goal,
                history_summary=history_summary,
                must_call_tool=not used_tool,
                must_use_fetch_first=not used_fetch,
            )
            action = plan.get("action")

            # Finish branch
            if action == "finish":
                if not used_tool:
                    # Enforce "at least one tool call" requirement
                    self.log.warning("Model tried to finish before any tool call; ignoring this plan.")
                    continue
                final_answer = plan.get("answer", "").strip() or "(model returned empty answer)"
                break

            # Tool-call branch
            if action == "call_tool":
                server = plan.get("server")
                tool = plan.get("tool")
                args = plan.get("args") or {}

                if not server or not tool:
                    final_answer = f"Invalid tool call plan: {json.dumps(plan, indent=2)}"
                    break

                result = self._call_tool(server, tool, args)
                if result.success:
                    snippet = (result.text or "")[:300]
                    used_tool = True
                    if server == "fetch":
                        used_fetch = True
                else:
                    snippet = f"ERROR: {result.error}"

                logs.append(
                    StepLog(
                        step=step,
                        action="call_tool",
                        server=server,
                        tool=tool,
                        args=args,
                        success=result.success,
                        error=result.error,
                        output_snippet=snippet,
                    )
                )
                continue

            # Unknown action - bail and show debug info
            final_answer = f"Unknown action from model: {json.dumps(plan, indent=2)}"
            break

        # Fallback final summarization if we never got a proper "finish"
        if final_answer == "No answer produced.":
            final_answer = self._summarize_final_answer(user_goal, logs)

        return final_answer, [vars(l) for l in logs]