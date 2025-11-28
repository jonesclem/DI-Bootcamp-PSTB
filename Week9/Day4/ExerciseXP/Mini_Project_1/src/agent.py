"""
Agent orchestrating MCP tool calls using an LLM (Groq or Ollama).

- Takes a user goal.
- Iteratively asks the LLM what to do next.
- The LLM either calls an MCP tool or finishes with a final markdown answer.
- Logs each tool call for observability.

Robustness:
- LLM cannot finish before at least one tool call.
- JSON parsing is tolerant (tries raw and "first JSON object").
- None-valued args are stripped before calling tools.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

from config import Config
from llm_ollama import chat as ollama_chat
from llm_groq import chat as groq_chat
from mcp_client import MCPClient, MCPToolCallResult


@dataclass
class StepLog:
    """Simple record of what happened at each tool call step."""

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
    Try to extract and parse the first JSON object in a string.

    Some models output text around JSON. We:
      - find the first '{'
      - track brace depth until matching '}'
      - attempt json.loads on that substring
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
                candidate = text[start : i + 1]
                try:
                    return json.loads(candidate)
                except Exception:
                    return None
    return None


def llm_chat(config: Config, messages: List[Dict[str, str]]) -> str:
    """
    Dispatch LLM calls to either Groq or Ollama based on config.llm_backend.
    """
    if config.llm_backend == "groq":
        if not (config.groq_base_url and config.groq_model and config.groq_api_key):
            raise RuntimeError("Groq backend selected but GROQ_* env vars are not fully set.")
        return groq_chat(
            base_url=config.groq_base_url,
            model=config.groq_model,
            api_key=config.groq_api_key,
            messages=messages,
        )

    # Default: Ollama
    return ollama_chat(
        base_url=config.ollama_base_url,
        model=config.ollama_model,
        messages=messages,
    )


class ResearchAgent:
    """
    Agent that uses the LLM to decide which MCP tool to call next.

    The model MUST return JSON with one of these shapes:

    Tool call:
      {
        "action": "call_tool",
        "server": "fetch" | "filesystem" | "kb_metadata",
        "tool": "<tool_name>",
        "args": { ... }
      }

    Finish:
      {
        "action": "finish",
        "answer": "<final_markdown_answer>"
      }
    """

    def __init__(self, config: Config, mcp_client: MCPClient, logger: logging.Logger | None = None):
        self.config = config
        self.mcp_client = mcp_client
        self.log = logger or logging.getLogger(__name__)

    def _ask_model_for_plan(
        self,
        user_goal: str,
        history_summary: str,
        must_call_tool: bool,
    ) -> Dict[str, Any]:
        """
        Ask the LLM what to do next and parse its JSON response.

        If must_call_tool=True, we explicitly forbid action="finish"
        in the instructions (used before the first tool call).
        """
        base_system_msg = """
You are an MCP planning agent.

Your ONLY job is to decide the NEXT ACTION in a multi-step tool workflow.
You do NOT execute tools yourself. You only emit JSON instructions that my code will follow exactly.

You MUST always respond with EXACTLY ONE JSON object, and NOTHING else.
No natural language, no explanations, no code fences, no comments.

------------------------------------------------------------
VALID RESPONSE SCHEMAS
------------------------------------------------------------

1) To CALL A TOOL, respond with:

{
  "action": "call_tool",
  "server": "<server_name>",
  "tool": "<tool_name>",
  "args": { ... }
}

2) To FINISH, respond with:

{
  "action": "finish",
  "answer": "<final_markdown_answer>"
}

Where:
- action is either "call_tool" or "finish".
- server is one of: "fetch", "filesystem", "kb_metadata".
- tool is:
    - "fetch"         (on server "fetch")
    - "write_file"    (on server "filesystem")
    - "add_metadata"  (on server "kb_metadata")
- args is an object containing ONLY the arguments expected by that tool.
- answer is a short markdown string.

NO other top-level keys are allowed.
DO NOT wrap the JSON in code fences.
DO NOT output more than one JSON object.

------------------------------------------------------------
AVAILABLE TOOLS
------------------------------------------------------------

You have access to exactly three MCP servers:

1) Server "fetch"
   Tool: "fetch"
   Purpose: Fetch a URL and return its page content as markdown.
   Args:
     - "url": string, required. Example: "https://en.wikipedia.org/wiki/Model_Context_Protocol"
     - "max_length": integer, optional. Maximum characters to return.
     - "start_index": integer, optional.
     - "raw": boolean, optional. If true, return raw content instead of markdown.

2) Server "filesystem"
   Tool: "write_file"
   Purpose: Write a markdown note file under the knowledge base root directory.
   Args:
     - "path": string, required. A path RELATIVE to the KB root, e.g. "notes/mcp_overview.md".
       Do NOT start paths with "./" or "/". Use relative paths like "notes/filename.md".
     - "content": string, required. The markdown content to write.

3) Server "kb_metadata"
   Tool: "add_metadata"
   Purpose: Register a metadata entry for an existing note file.
   Args:
     - "topic": string, required. Short title/topic, e.g. "Overview of MCP".
     - "file_path": string, required. The SAME relative path you used in write_file,
       e.g. "notes/mcp_overview.md".
     - "summary": string, required. 2–3 sentences summarizing the note.

------------------------------------------------------------
WORKFLOW YOU MUST FOLLOW
------------------------------------------------------------

Your high-level workflow MUST be:

1) Use "fetch.fetch" one or two times to gather information from the web.
2) Then use "filesystem.write_file" EXACTLY ONCE to save a markdown note under the KB root.
3) Then use "kb_metadata.add_metadata" EXACTLY ONCE to register metadata for that note.
4) Then use "finish" with a short markdown answer for the user.

In other words, the ideal sequence of actions is:

  call_tool(fetch.fetch)
  -> call_tool(filesystem.write_file)
  -> call_tool(kb_metadata.add_metadata)
  -> finish

You MUST NOT skip steps 2 or 3.
You MUST NOT call kb_metadata.add_metadata before you have successfully written the note file.

------------------------------------------------------------
ARGUMENT RULES
------------------------------------------------------------

- For optional arguments (like max_length, start_index, raw):
  - If you do not want to set them, simply OMIT the field.
  - DO NOT set them to null, None, or an empty string.
- For filesystem.write_file:
  - "path" MUST be relative to the KB root, for example:
      "notes/Model_Context_Protocol.md"
    NOT "./notes/...", NOT "/notes/...".
- For kb_metadata.add_metadata:
  - "file_path" MUST match the "path" you used for filesystem.write_file.
  - "summary" should be a short human-readable summary (2–3 sentences).

------------------------------------------------------------
PLANNING RULES
------------------------------------------------------------

- Never repeat the exact same tool call with the exact same arguments more than once.
- Prefer at most 1–2 fetch calls before moving to write_file.
- Once the note has been written successfully, immediately follow with add_metadata.
- Only use "finish" AFTER at least one successful tool call.
- If earlier tool calls failed, use that error information from history to choose better arguments in the next tool call.

------------------------------------------------------------
YOUR TASK IN EACH STEP
------------------------------------------------------------

You are given:
- The user goal.
- A summary of previous tool calls and their outputs (which may include errors).

At EACH step you must:
1. Decide whether to:
   - call the next appropriate tool in the workflow, or
   - finish with a final markdown answer (ONLY if the workflow is already completed).
2. Output a SINGLE JSON object following the schemas above.

Remember:
- Respond with ONE JSON object only.
- Do NOT add any explanation, comments, or extra text outside the JSON.
"""
        system_msg = base_system_msg
        if must_call_tool:
            system_msg += "\n\nFor THIS step you are NOT allowed to use action 'finish'. You MUST use action 'call_tool'."

        user_msg = f"""
User goal:
{user_goal}

Recent tool history:
{history_summary}

Respond ONLY with ONE JSON object following the schema above.
""".strip()

        raw = llm_chat(
            self.config,
            [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        ).strip()

        # Remove markdown fences if present
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()

        # Try direct JSON parsing first
        try:
            plan = json.loads(raw)
        except Exception:
            # If that fails, try to extract first {...}
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
        Create a compact summary of the last few tool calls for the LLM.
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
        Call an MCP tool with a small retry loop.

        - Removes None-valued args.
        - Logs before and after the call for observability.
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
        If the planning loop never produced a 'finish' action, we still want to
        return a useful answer. This method does one extra LLM call that only
        summarizes existing tool history.
        """
        sys_msg = "You are a summarizer. Do NOT call tools. Only write a short markdown answer."
        user_msg = f"""
User goal:
{user_goal}

Tool history:
{self._summarize_logs(logs)}

Summarize the findings in markdown.
""".strip()

        return llm_chat(
            self.config,
            [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg},
            ],
        ).strip()

    def run_research(self, user_goal: str, max_steps: int = 5) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Main entry point used by Streamlit.

        Returns:
            final_answer_markdown, list_of_logs_as_dicts
        """
        logs: List[StepLog] = []
        used_tool = False
        final_answer = "No answer produced."

        for step in range(1, max_steps + 1):
            history_summary = self._summarize_logs(logs)

            plan = self._ask_model_for_plan(
                user_goal=user_goal,
                history_summary=history_summary,
                must_call_tool=not used_tool,  # before first tool, forbid finish
            )

            action = plan.get("action")

            # Handle finish
            if action == "finish":
                if not used_tool:
                    # We do not accept an early finish; ask again next loop.
                    self.log.warning("Model tried to finish before any tool call; ignoring this plan.")
                    continue
                final_answer = plan.get("answer", "").strip() or "(model returned empty answer)"
                break

            # Handle tool call
            if action == "call_tool":
                server = plan.get("server")
                tool = plan.get("tool")
                args = plan.get("args") or {}

                if not server or not tool:
                    final_answer = f"Invalid tool call plan: {json.dumps(plan, indent=2)}"
                    break

                result = self._call_tool(server, tool, args)
                snippet = (result.text or "")[:300]

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

                if result.success:
                    used_tool = True

                continue  # next planning step

            # Unknown action → bail with debug info
            final_answer = f"Unknown action from model: {json.dumps(plan, indent=2)}"
            break

        # If we never saw a valid 'finish', run one summarization pass.
        if final_answer == "No answer produced.":
            final_answer = self._summarize_final_answer(user_goal, logs)

        return final_answer, [vars(l) for l in logs]