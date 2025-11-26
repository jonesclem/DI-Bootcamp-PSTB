# server/schemas.py
from typing import List, Dict
from pydantic import BaseModel, HttpUrl


class ToolInfo(BaseModel):
    name: str
    input_schema: Dict


class ToolsListResponse(BaseModel):
    tools: List[ToolInfo]


class SearchWebRequest(BaseModel):
    query: str
    k: int = 5


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str


class SearchWebResponse(BaseModel):
    results: List[SearchResult]


class FetchReadableRequest(BaseModel):
    url: HttpUrl


class FetchReadableResponse(BaseModel):
    url: str
    title: str
    text: str


class Doc(BaseModel):
    title: str
    url: HttpUrl
    text: str


class SummarizeRequest(BaseModel):
    topic: str
    docs: List[Doc]


class SourceEntry(BaseModel):
    i: int
    title: str
    url: str


class SummarizeResponse(BaseModel):
    bullets: List[str]
    sources: List[SourceEntry]


class SaveMarkdownRequest(BaseModel):
    filename: str
    content: str


class SaveMarkdownResponse(BaseModel):
    path: str