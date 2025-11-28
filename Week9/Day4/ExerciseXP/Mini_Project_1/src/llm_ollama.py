"""
Very small Ollama chat helper with graceful fallback.

Primary attempt: /api/chat
If that is not found (404), fallback to older /api/generate.
"""

from typing import List, Dict
import requests


def _messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    """
    Convert chat-style messages into a single prompt string.

    This is only used when falling back to /api/generate on older Ollama.
    """
    parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        parts.append(f"{role.upper()}:\n{content}\n")
    parts.append("ASSISTANT:\n")
    return "\n".join(parts)


def chat(base_url: str, model: str, messages: List[Dict[str, str]]) -> str:
    """
    Call Ollama and return assistant text.

    1) Try /api/chat (newer Ollama).
    2) If 404, fallback to /api/generate (older Ollama).
    """
    url_chat = f"{base_url.rstrip('/')}/api/chat"
    payload_chat = {"model": model, "messages": messages, "stream": False}

    # Generous timeout because model load can be slow on older machines.
    timeout_seconds = 600

    # First try /api/chat
    resp = requests.post(url_chat, json=payload_chat, timeout=timeout_seconds)

    if resp.status_code == 404:
        # Fallback to /api/generate for older Ollama versions.
        url_gen = f"{base_url.rstrip('/')}/api/generate"
        prompt = _messages_to_prompt(messages)
        payload_gen = {"model": model, "prompt": prompt, "stream": False}
        resp = requests.post(url_gen, json=payload_gen, timeout=timeout_seconds)
        resp.raise_for_status()
        data = resp.json()
        # Older generate API returns {"response": "..."}.
        return data.get("response", "")

    # For other errors, propagate normally so the app can surface them.
    resp.raise_for_status()
    data = resp.json()
    # Newer chat API returns {"message": {"content": "..."}}
    return data.get("message", {}).get("content", "")