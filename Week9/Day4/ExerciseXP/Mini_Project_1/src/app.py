"""
Streamlit UI for the MCP research agent.

Responsibilities:
- Display config (Groq + MCP) in a read-only sidebar.
- Let the user specify a research goal.
- Run the agent and show:
  - final markdown answer,
  - per-step MCP tool call logs (for observability), formatted as pretty JSON.
"""

from __future__ import annotations

import logging

import streamlit as st

from config import get_config
from mcp_client import MCPClient
from agent import ResearchAgent


def _setup_logging(level: str) -> logging.Logger:
    """
    Configure a simple console logger for the app.
    """
    logger = logging.getLogger("mcp_research_app")
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            "%Y-%m-%d %H:%M:%S | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger


def main() -> None:
    """
    Entrypoint for the Streamlit UI.
    """
    cfg = get_config()
    logger = _setup_logging(cfg.log_level)

    st.set_page_config(page_title="MCP Research Agent", layout="wide")
    st.title("MCP Research Agent (Groq + MCP)")

    # Sidebar: show effective configuration so the reviewer sees how
    # Groq and MCP servers are wired in.
    st.sidebar.header("Configuration (read-only)")
    st.sidebar.text(f"Groq base URL: {cfg.groq_base_url}")
    st.sidebar.text(f"Groq model: {cfg.groq_model}")
    st.sidebar.text(f"KB root dir: {cfg.kb_root_dir}")
    st.sidebar.text(f"Metadata file: {cfg.kb_metadata_path}")

    max_steps = st.sidebar.slider("Max planning steps", min_value=2, max_value=10, value=5)

    st.markdown(
        "This app uses **Groq** for planning and three MCP servers:\n"
        "- `mcp-server-fetch` (third-party, web fetching)\n"
        "- `server-filesystem` (third-party, file writes)\n"
        "- `kb_metadata_server` (local, KB metadata)\n"
    )

    user_goal = st.text_area(
        "Enter your research goal",
        value="Create a short note summarizing the Model Context Protocol (MCP).",
        height=120,
    )

    if st.button("Run agent"):
        if not user_goal.strip():
            st.warning("Please enter a goal.")
            return

        st.info("Running agent...")

        # Construct MCP client and agent once per run.
        mcp_client = MCPClient(cfg, logger=logger)
        agent = ResearchAgent(cfg, mcp_client, logger=logger)

        final_answer, logs = agent.run_research(user_goal.strip(), max_steps=max_steps)

        # Render final answer as markdown so headings / bullets are visible.
        st.subheader("Final answer (markdown)")
        st.markdown(final_answer)

        # Pretty-print tool logs as expanders with formatted JSON.
        st.subheader("Tool call log (per step)")
        if not logs:
            st.write("(no tool calls)")
        else:
            for entry in logs:
                step = entry.get("step", "?")
                server = entry.get("server") or "?"
                tool = entry.get("tool") or "?"
                label = f"Step {step} — {server}.{tool}"
                with st.expander(label, expanded=False):
                    st.json(entry)


if __name__ == "__main__":
    main()