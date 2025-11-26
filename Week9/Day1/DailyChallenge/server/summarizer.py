# server/summarizer.py
from typing import List
import requests
from fastapi import HTTPException

from .config import OLLAMA_BASE_URL, OLLAMA_MODEL
from .schemas import Doc, SourceEntry, SummarizeResponse


def summarize_with_citations(topic: str, docs: List[Doc]) -> SummarizeResponse:
    if not docs:
        raise HTTPException(status_code=400, detail="No documents provided")

    # Build sources list (1-based indices)
    sources: List[SourceEntry] = []
    for idx, d in enumerate(docs, start=1):
        sources.append(SourceEntry(i=idx, title=d.title, url=str(d.url)))

    # Build prompt for the LLM
    sources_text_lines = []
    for s, d in zip(sources, docs):
        snippet = d.text[:1200]  # short snippet per source
        sources_text_lines.append(
            f"[{s.i}] {d.title} ({d.url})\n{snippet}\n"
        )
    sources_text = "\n\n".join(sources_text_lines)

    system_prompt = (
        "You are a helpful assistant that writes concise research briefings.\n"
        "You will be given a TOPIC and several SOURCES with indices [1], [2], etc.\n"
        "Write exactly 5 bullet points about the topic.\n"
        "Each bullet must:\n"
        "- Be at most 200 characters.\n"
        "- Include at least one citation marker like [1] or [2] that refers to a source.\n"
        "Output format:\n"
        "- Exactly 5 lines.\n"
        "- Each line starts with '- ' followed by the text.\n"
        "- Do not add any extra text before or after the bullets."
    )

    user_prompt = f"TOPIC: {topic}\n\nSOURCES:\n{sources_text}"

    body = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat", json=body, timeout=60
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error calling Ollama: {e}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Ollama error: {resp.text}",
        )

    data = resp.json()
    message = data.get("message", {})
    content = message.get("content", "")

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    bullets: List[str] = []
    for line in lines:
        if line.startswith("- "):
            bullets.append(line[2:].strip())

    # Fallback: if the model didn't follow the format, just take first 5 lines
    if not bullets:
        bullets = lines

    bullets = bullets[:5]
    # If fewer than 5, pad with empty / generic bullets
    while len(bullets) < 5:
        bullets.append("[No additional information][1]")

    # Enforce max length 200 chars
    bullets = [b[:200] for b in bullets]

    return SummarizeResponse(bullets=bullets, sources=sources)