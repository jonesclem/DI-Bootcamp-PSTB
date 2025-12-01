# Mini Project – MCP Agentic Application (Part 2)
# This file defines the student's OWN MCP server required by Part 2:
# - Server name: "local_insights"
# - Custom tools:
#   * clean_text(text, lowercase)          → text normalization / cleaning
#   * generate_insights(text)              → deterministic JSON insights extractor
# These tools are discovered and called via mcp_multi_client.py and orchestrator.py
# together with external servers from Part 1 (filesystem + web).


from __future__ import annotations

import json
import logging
import re

from mcp.server import Server
from mcp.types import Tool

# Basic logging to stderr (MCP-friendly)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_mcp_server")

server = Server("local_insights")


@server.tool(
    Tool(
        name="clean_text",
        description=(
            "Clean and normalize raw text. "
            "Removes HTML, excessive whitespace, and common artifacts. "
            "Useful before running LLM analysis or saving notes."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Raw text that may contain HTML, new lines or weird spacing.",
                },
                "lowercase": {
                    "type": "boolean",
                    "description": "If true, convert text to lowercase.",
                    "default": False,
                },
            },
            "required": ["text"],
        },
    )
)
async def clean_text_tool(text: str, lowercase: bool = False) -> str:
    """
    Basic text preprocessing: strip HTML, collapse whitespace, normalize encoding.
    Limitations:
    - purely heuristic and deterministic
    - does not handle complex markup (e.g. nested tags) perfectly
    """
    logger.info("clean_text called (lowercase=%s)", lowercase)

    if not isinstance(text, str):
        raise ValueError("Parameter 'text' must be a string.")
    if not text.strip():
        raise ValueError("Input text is empty. Provide non-empty text for cleaning.")

    # Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Normalize encoding
    cleaned = cleaned.encode("utf-8", "ignore").decode()

    if lowercase:
        cleaned = cleaned.lower()

    return cleaned


@server.tool(
    Tool(
        name="generate_insights",
        description=(
            "Generate structured insights from a cleaned text. "
            "Returns JSON with key_points, risks, and recommended_steps. "
            "Deterministic, no LLM inside this tool.\n"
            "Limitations: relies on simple keyword detection and sentence length; "
            "does not understand deep semantics."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Clean input text in natural language.",
                },
            },
            "required": ["text"],
        },
    )
)
async def generate_insights(text: str) -> str:
    """
    Extract simple structured 'insights' heuristically.
    This tool is deterministic and safe: it never calls an LLM by itself.

    Limitations:
    - Uses keyword-based heuristics to detect 'risks'
    - Sentences are split with a simple regex, which may be imperfect
    """
    logger.info("generate_insights called")

    if not isinstance(text, str):
        raise ValueError("Parameter 'text' must be a string.")
    if not text.strip():
        raise ValueError("Input text is empty. Provide non-empty text for analysis.")

    # More robust sentence splitting
    raw_sentences = re.split(r"[.!?;\n]", text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]

    key_points = [s for s in sentences if len(s.split()) > 6][:10]
    risks = [
        s
        for s in sentences
        if any(trigger in s.lower() for trigger in ["risk", "issue", "problem", "concern"])
    ]
    steps = [
        "Review the main context and assumptions.",
        "Validate critical points with additional data.",
        "Define concrete next steps and responsibilities.",
    ]

    insights = {
        "key_points": key_points,
        "risks": risks[:10],
        "recommended_steps": steps,
        "meta": {
            "num_sentences": len(sentences),
            "num_key_points": len(key_points),
            "num_risks": len(risks),
        },
    }

    return json.dumps(insights, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    server.run()
