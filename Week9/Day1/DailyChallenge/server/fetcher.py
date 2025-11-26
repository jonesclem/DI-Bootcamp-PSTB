# server/fetcher.py
from typing import Tuple
import requests
from fastapi import HTTPException
from bs4 import BeautifulSoup


def fetch_readable(url: str) -> Tuple[str, str]:
    """
    Fetches a URL and returns (title, text) using a very simple
    'main content' heuristic: concatenate all <p> tags.
    """
    try:
        resp = requests.get(url, timeout=10)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error fetching URL: {e}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Non-200 response fetching URL: {resp.status_code}",
        )

    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else url

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = "\n\n".join(p for p in paragraphs if p)

    # Truncate to avoid overloading the LLM
    max_chars = 8000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Truncated]"

    return title, text