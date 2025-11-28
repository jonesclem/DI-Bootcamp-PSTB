"""
Streamlit UI for the MCP research agent.

- Shows read-only configuration in the sidebar.
- Lets the user enter a research goal.
- Runs the agent and displays the final answer + tool call log.
"""

from __future__ import annotations

import json
import logging
import os

import streamlit as st

from config import get_config
from mcp_client import MCPClient
from agent import ResearchAgent


def _setup_logging(level: str) -> logging.Logger:
    """
    Configure a root logger for the app.
    """
    logger = logging.getLogger("mcp_research_app")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level.upper())
    return logger


def main() -> None:
    cfg = get_config()
    logger = _setup_logging(cfg.log_level)

    # MCP client + agent
    mcp_client = MCPClient(cfg, logger=logger)
    agent = ResearchAgent(cfg, mcp_client, logger=logger)

    st.title("MCP Research Agent (Mini Project)")

    # Sidebar: config summary
    st.sidebar.header("Configuration (read-only)")
    st.sidebar.text(f"LLM backend: {cfg.llm_backend}")

    if cfg.llm_backend == "ollama":
        st.sidebar.text(f"Ollama base URL: {cfg.ollama_base_url}")
        st.sidebar.text(f"Ollama model: {cfg.ollama_model}")
    elif cfg.llm_backend == "groq":
        st.sidebar.text(f"Groq base URL: {cfg.groq_base_url}")
        st.sidebar.text(f"Groq model: {cfg.groq_model}")

    st.sidebar.text(f"KB root dir: {os.path.abspath(cfg.kb_root_dir)}")
    st.sidebar.text(f"Metadata file: {os.path.abspath(cfg.kb_metadata_path)}")

    # Main controls
    max_steps = st.sidebar.slider(
        "Max planning steps", min_value=1, max_value=10, value=5, step=1
    )

    user_goal = st.text_area(
        "Research goal / query",
        value="Using the URL https://en.wikipedia.org/wiki/Model_Context_Protocol, "
              "fetch information about the Model Context Protocol, write a note to the KB, "
              "register metadata for that note, and then summarize the result.",
        height=150,
    )

    if st.button("Run agent"):
        if not user_goal.strip():
            st.warning("Please enter a research goal.")
            return

        with st.spinner("Running agent..."):
            final_answer, logs = agent.run_research(user_goal.strip(), max_steps=max_steps)

        st.subheader("Final answer (markdown)")
        st.markdown(final_answer)

        st.subheader("Tool call log (per step)")
        if not logs:
            st.write("No tools were called.")
        else:
            for entry in logs:
                st.code(json.dumps(entry, indent=2), language="json")


if __name__ == "__main__":
    main()