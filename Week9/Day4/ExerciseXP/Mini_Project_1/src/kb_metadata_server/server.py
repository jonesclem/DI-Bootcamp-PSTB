"""
Custom MCP server: kb_metadata_server.

This server exposes a single tool:
- add_metadata(topic, file_path, summary)

It appends JSONL records to a metadata file so we can track which
notes exist in the KB and what they contain at a high level.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP


@dataclass
class MetadataConfig:
    """
    Configuration for the KB metadata server.

    Uses environment variables so the same code works on different machines.
    """
    root_dir: str
    metadata_path: str

    @classmethod
    def from_env(cls) -> "MetadataConfig":
        root = os.getenv("KB_ROOT_DIR", ".")
        meta = os.getenv("KB_METADATA_PATH", "./kb/metadata.jsonl")
        return cls(root_dir=root, metadata_path=meta)


# Create the MCP server instance and load config once.
mcp = FastMCP("kb_metadata")
cfg = MetadataConfig.from_env()


@mcp.tool()
def add_metadata(topic: str, file_path: str, summary: str) -> str:
    """
    Register a metadata entry for an existing note file.

    Args:
        topic: short title/topic for the note.
        file_path: path relative to KB_ROOT_DIR (e.g. "notes/mcp_overview.md").
        summary: 2–3 sentence description of the note.

    Returns:
        A short confirmation or error message as plain text.
    """
    # Compute absolute path and ensure it stays within KB root for safety.
    abs_path = os.path.abspath(os.path.join(cfg.root_dir, file_path))
    if not abs_path.startswith(os.path.abspath(cfg.root_dir) + os.sep):
        return f"Refused: path outside KB root: {abs_path}"

    # Ensure the directory for the metadata file exists.
    os.makedirs(os.path.dirname(cfg.metadata_path), exist_ok=True)

    record: Dict[str, Any] = {
        "topic": topic,
        "file_path": file_path,
        "summary": summary,
    }

    # Append one JSON object per line for simple, reproducible parsing.
    with open(cfg.metadata_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return f"Metadata added for {file_path} with topic '{topic}'"


if __name__ == "__main__":
    # Run the MCP server over stdio.
    mcp.run()