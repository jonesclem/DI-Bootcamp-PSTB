# server/main.py
from typing import List

from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import JSONResponse

from .config import MCP_HTTP_TOKEN, require_config
from . import serper_client
from .fetcher import fetch_readable
from .summarizer import summarize_with_citations
from .schemas import (
    ToolsListResponse,
    ToolInfo,
    SearchWebRequest,
    SearchWebResponse,
    FetchReadableRequest,
    FetchReadableResponse,
    SummarizeRequest,
    SummarizeResponse,
    SaveMarkdownRequest,
    SaveMarkdownResponse,
)

import os
from pathlib import Path


# Ensure required env vars are present at startup
require_config()

app = FastAPI(title="Tiny Tool API Server")


def verify_bearer_token(authorization: str = Header(...)):
    if not MCP_HTTP_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: MCP_HTTP_TOKEN is not set",
        )
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = authorization[len(prefix):].strip()
    if token != MCP_HTTP_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/tools", response_model=ToolsListResponse)
def list_tools(_: None = Depends(verify_bearer_token)):
    tools: List[ToolInfo] = [
        ToolInfo(
            name="search_web",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "k": {"type": "integer"},
                },
                "required": ["query"],
            },
        ),
        ToolInfo(
            name="fetch_readable",
            input_schema={
                "type": "object",
                "properties": {"url": {"type": "string", "format": "uri"}},
                "required": ["url"],
            },
        ),
        ToolInfo(
            name="summarize_with_citations",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "docs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string", "format": "uri"},
                                "text": {"type": "string"},
                            },
                            "required": ["title", "url", "text"],
                        },
                    },
                },
                "required": ["topic", "docs"],
            },
        ),
        ToolInfo(
            name="save_markdown",
            input_schema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["filename", "content"],
            },
        ),
    ]
    return ToolsListResponse(tools=tools)


@app.post("/tools/search_web", response_model=SearchWebResponse)
def search_web(
    payload: SearchWebRequest,
    _: None = Depends(verify_bearer_token),
):
    results = serper_client.search_web(payload.query, payload.k)
    return SearchWebResponse(results=results)


@app.post("/tools/fetch_readable", response_model=FetchReadableResponse)
def fetch_readable_endpoint(
    payload: FetchReadableRequest,
    _: None = Depends(verify_bearer_token),
):
    title, text = fetch_readable(str(payload.url))
    return FetchReadableResponse(url=str(payload.url), title=title, text=text)


@app.post("/tools/summarize_with_citations", response_model=SummarizeResponse)
def summarize_endpoint(
    payload: SummarizeRequest,
    _: None = Depends(verify_bearer_token),
):
    return summarize_with_citations(payload.topic, payload.docs)


@app.post("/tools/save_markdown", response_model=SaveMarkdownResponse)
def save_markdown(
    payload: SaveMarkdownRequest,
    _: None = Depends(verify_bearer_token),
):
    # Sanitize filename
    safe_name = os.path.basename(payload.filename)
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename")

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    path = output_dir / safe_name

    path.write_text(payload.content, encoding="utf-8")

    return SaveMarkdownResponse(path=str(path.resolve()))


@app.get("/")
def root():
    return JSONResponse({"status": "ok", "message": "Tool API server running"})