# Mini Project – MCP Agentic Application (Part 1 + Part 2)
# This module implements the LLM client:
# - Uses OpenAI-compatible API (GroqCloud or Ollama) with config from config.py
# - Provides planning for the agent (tool selection via function calling)
# - Is used directly by orchestrator.py to decide which MCP tools to call.
# The MCP server with custom tools is defined separately in my_mcp_server.py.


from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
import logging

from openai import OpenAI
from config import load_llm_config


logger = logging.getLogger("llm_client")
logger.setLevel(logging.INFO)


@dataclass
class LLMRuntimeConfig:
    backend: str
    model: str
    base_url: str
    api_key: str


class LLMClient:
    """
    Wrapper autour de l'API OpenAI-compatible (GroqCloud ou Ollama).
    - Validation stricte des inputs
    - Gestion d’erreur robuste
    - Logging propre
    """

    def __init__(self) -> None:
        cfg = load_llm_config()
        self.config = LLMRuntimeConfig(
            backend=cfg.backend,
            model=cfg.model,
            base_url=cfg.base_url,
            api_key=cfg.api_key,
        )

        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )

    @staticmethod
    def _validate_messages(messages: List[Dict[str, Any]]) -> None:
        if not isinstance(messages, list):
            raise ValueError("messages must be a list.")
        for m in messages:
            if not isinstance(m, dict):
                raise ValueError("Each message must be a dict.")
            if "role" not in m or "content" not in m:
                raise ValueError("Each message must contain 'role' and 'content'.")

    @staticmethod
    def _validate_tools(tools: List[Dict[str, Any]]) -> None:
        if not isinstance(tools, list):
            raise ValueError("tools must be a list.")
        for t in tools:
            if t.get("type") != "function":
                raise ValueError("All tools must have type 'function'.")
            fn = t.get("function") or {}
            if "name" not in fn or "parameters" not in fn:
                raise ValueError("Each tool must define 'name' and 'parameters'.")

    def plan(
        self,
        messages: List[Dict[str, Any]],
        tools_for_llm: List[Dict[str, Any]],
        temperature: float = 0.15,
        max_tokens: int = 800,
    ) -> Dict[str, Any]:
        """Retourne la réponse du LLM + éventuelles tool_calls."""

        self._validate_messages(messages)
        self._validate_tools(tools_for_llm)

        logger.info(
            f"LLM request: backend={self.config.backend}, model={self.config.model}, "
            f"messages={len(messages)}, tools={len(tools_for_llm)}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=tools_for_llm,
                tool_choice="auto",
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:  # noqa: BLE001
            logger.exception("LLM call failed.")
            raise RuntimeError(f"LLM call failed: {e}") from e

        msg = response.choices[0].message.to_dict()

        logger.info(
            f"LLM returned role={msg.get('role')}, "
            f"tool_calls={bool(msg.get('tool_calls'))}"
        )

        return msg


# Instance globale utilisée par l’orchestrateur
_global_llm = LLMClient()


def plan_with_llm(
    messages: List[Dict[str, Any]],
    tools_for_llm: List[Dict[str, Any]],
    temperature: float = 0.15,
    max_tokens: int = 800,
) -> Dict[str, Any]:
    return _global_llm.plan(
        messages=messages,
        tools_for_llm=tools_for_llm,
        temperature=temperature,
        max_tokens=max_tokens,
    )
