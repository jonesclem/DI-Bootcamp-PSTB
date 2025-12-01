# app.py
import asyncio

import streamlit as st

from smart_data_scout.agent import run_agent_once
from smart_data_scout.config import load_config
from smart_data_scout.llm_backends import create_llm_backend
from smart_data_scout.mcp_client import MCPClientManager
from smart_data_scout.types import ToolCallLog


@st.cache_resource(show_spinner=False)
def get_app_objects():
    cfg = load_config()
    llm = create_llm_backend(cfg.llm)
    mcp_manager = MCPClientManager(cfg.mcp_servers)
    return cfg, llm, mcp_manager


def main():
    st.set_page_config(page_title="Smart Data Scout", layout="wide")
    st.title("🔍 Smart Data Scout")

    cfg, llm, mcp_manager = get_app_objects()

    with st.sidebar:
        st.header("Config")
        st.write(f"LLM backend: `{cfg.llm.backend}`")
        st.write(f"Model: `{cfg.llm.model}`")
        st.write(f"Max steps: {cfg.max_agent_steps}")
        st.markdown("---")
        st.caption("MCP servers:")
        for name, srv in cfg.mcp_servers.items():
            st.write(f"- **{name}** → `{srv.command} {' '.join(srv.args)}`")

    st.markdown(
        "Describe a **data scouting task**. Examples:\n"
        "- *\"Find a public CSV of EU EV sales since 2020, clean it and summarize key trends.\"*\n"
        "- *\"Analyze a sales.csv from a URL I’ll provide and highlight anomalies by region.\"*"
    )

    user_goal = st.text_area("Goal", height=140)

    if st.button("Run Smart Data Scout", type="primary") and user_goal.strip():
        with st.spinner("Agent thinking, searching, and analyzing..."):
            final_answer, logs = asyncio.run(
                run_agent_once(
                    user_goal.strip(),
                    llm,
                    mcp_manager,
                    max_steps=cfg.max_agent_steps,
                )
            )

        st.subheader("🧠 Final Answer")
        st.write(final_answer)

        st.subheader("🔎 Tool Call Log")
        if not logs:
            st.write("No tool calls were made.")
        else:
            for log in logs:
                _render_log(log)


def _render_log(log: ToolCallLog):
    with st.expander(f"Step {log.step}: {log.server_name}.{log.tool_name}"):
        st.write(f"**Success:** {log.success}")
        st.write("**Arguments (redacted):**")
        st.json({k: v for k, v in log.arguments.items() if "key" not in k.lower()})
        st.write("**Summary:**")
        st.write(log.summary)
        if log.error:
            st.error(f"Error: {log.error}")


if __name__ == "__main__":
    main()