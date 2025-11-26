# server/serper_client.py
from typing import List
import requests
from fastapi import HTTPException

from .config import SERPER_API_KEY
from .schemas import SearchResult


SERPER_SEARCH_URL = "https://google.serper.dev/search"


def search_web(query: str, k: int) -> List[SearchResult]:
    if not SERPER_API_KEY:
        raise HTTPException(status_code=500, detail="SERPER_API_KEY not configured")

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"q": query}

    try:
        resp = requests.post(SERPER_SEARCH_URL, json=payload, headers=headers, timeout=10)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error calling Serper.dev: {e}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Serper.dev error: {resp.text}",
        )

    data = resp.json()
    organic = data.get("organic", []) or []

    results: List[SearchResult] = []
    for item in organic[:k]:
        title = item.get("title") or ""
        url = item.get("link") or ""
        snippet = item.get("snippet") or ""
        if not url:
            continue
        results.append(
            SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                source="serper.dev",
            )
        )

    return results