# src/llm_groq.py
from typing import List, Dict
import time
import requests


def chat(base_url: str, model: str, api_key: str, messages: List[Dict[str, str]]) -> str:
    """
    Call Groq's OpenAI-compatible chat API and return the assistant text.

    - Logs before and after the HTTP call.
    - Uses a finite timeout.
    - Prints any HTTP error body for debugging.
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
        # Show the error body so we know *why* it's 400
        print("[llm_groq] Error response body:", resp.text[:1000])
        resp.raise_for_status()

    data = resp.json()

    if "choices" not in data or not data["choices"]:
        print("[llm_groq] Unexpected response JSON:", data)
        raise RuntimeError("Groq response missing 'choices'")

    content = data["choices"][0]["message"]["content"]
    print(f"[llm_groq] Response text length={len(content)}")
    return content