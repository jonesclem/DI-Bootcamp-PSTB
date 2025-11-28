"""
Custom MCP server: "kb_metadata".

This server exposes *two* very simple tools:

1) add_metadata(topic: str, file_path: str, summary: str) -> str
   - Appends a JSON line to KB_METADATA_PATH.
   - Intended to be called after writing a note file.

2) list_metadata(topic: Optional[str]) -> str
   - Returns a small markdown list of entries for the given topic (or all topics).

Implementation uses the FastMCP helper from the official MCP Python SDK.
It runs over STDIO by default when executed as `python -m src.kb_metadata_server.server`.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from mcp.server.fastmcp import FastMCP


# Create the MCP server instance
mcp = FastMCP("kb_metadata")


def _metadata_path() -> str:
    """Resolve the metadata file path from env or fall back to ./kb/metadata.jsonl."""
    return os.environ.get("KB_METADATA_PATH", "./kb/metadata.jsonl")


def _ensure_dir_exists(path: str) -> None:
    """Create parent directory for a file if it does not exist."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)


@mcp.tool()
def add_metadata(topic: str, file_path: str, summary: str) -> str:
    """
    Append a metadata entry as JSONL.

    Args:
        topic: Short topic label (e.g. "LLMs and MCP").
        file_path: Path to the note file (relative or absolute).
        summary: 2-3 sentence summary of the note.

    Returns:
        Human-readable confirmation string.
    """
    path = _metadata_path()
    _ensure_dir_exists(path)

    entry: Dict[str, Any] = {
        "topic": topic,
        "file_path": file_path,
        "summary": summary,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return f"Recorded metadata for topic='{topic}' and file='{file_path}'."

@mcp.tool()
def list_metadata(topic: Optional[str] = None) -> str:
    """
    List metadata entries, optionally filtered by topic.

    Args:
        topic: If given, only entries with this topic will be returned.

    Returns:
        A markdown-formatted list of entries.
    """
    path = _metadata_path()
    if not os.path.exists(path):
        return "No metadata entries found yet."

    entries: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                entries.append(obj)
            except json.JSONDecodeError:
                continue

    if topic is not None:
        entries = [e for e in entries if e.get("topic") == topic]

    if not entries:
        return f"No metadata entries found for topic '{topic}'." if topic else "No metadata entries found."

    lines = ["# Metadata entries"]
    if topic:
        lines.append(f"Filtered by topic: **{topic}**")

    for e in entries:
        lines.append(
            f"- **Topic**: {e.get('topic')} | "
            f"**File**: `{e.get('file_path')}` | "
            f"**Created**: {e.get('created_at')}  \n"
            f"  Summary: {e.get('summary')}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    # Default transport is STDIO, which is what the MCP client expects.
    mcp.run()