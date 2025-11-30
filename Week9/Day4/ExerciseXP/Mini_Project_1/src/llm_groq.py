"""
Groq LLM client helper.

This module implements a minimal wrapper around Groq's
OpenAI-compatible /chat/completions endpoint.
"""

from __future__ import annotations

from typing import List, Dict
import time
import requests


def chat(base_url: str, model: str, api_key: str, messages: List[Dict[str, str]]) -> str:
    """
    Call Groq's chat API and return the assistant's reply text.

    Args:
        base_url: Groq API base URL, e.g. https://api.groq.com/openai/v1
        model: model name, e.g. openai/gpt-oss-20b
        api_key: Groq API key
        messages: OpenAI-style message list (role/content)

    Raises:
        requests.HTTPError if Groq returns a non-2xx status.
        RuntimeError if the JSON lacks "choices".
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    print(f"[llm_groq] POST {url} model={model!r}")
    print(f"[llm_groq] messages count={len(messages)}")

    start = time.time()
    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": messages,
                "stream": False,
            },
            timeout=40,
        )
    except Exception as e:
        elapsed = time.time() - start
        print(f"[llm_groq] HTTP exception after {elapsed:.2f}s: {repr(e)}")
        raise

    elapsed = time.time() - start
    print(f"[llm_groq] Got HTTP {resp.status_code} after {elapsed:.2f}s")

    if not resp.ok:
        # Print the error body for easier debugging during development.
        print("[llm_groq] Error response body:", resp.text[:1000])
        resp.raise_for_status()

    data = resp.json()
    if "choices" not in data or not data["choices"]:
        raise RuntimeError(f"Groq response missing 'choices': {data}")

    content = data["choices"][0]["message"]["content"]
    print(f"[llm_groq] Response text length={len(content)}")
    return content