# Mini Project – MCP Agentic Application (Part 1 + Part 2)
# This file implements ONLY the Streamlit UI.
# The core logic (MCP servers, custom tools, LLM planning, orchestration) is
# implemented in:
# - my_mcp_server.py        → custom MCP server and tools (Part 2)
# - mcp_multi_client.py     → multi-server MCP client (external + custom)
# - llm_client.py           → LLM planning (Groq/Ollama)
# - orchestrator.py         → agentic orchestration using all tools.
# This UI calls run_agent_sync(...) from orchestrator.py.


from __future__ import annotations

import streamlit as st

from config import load_llm_config
from orchestrator import run_agent_sync


def main() -> None:
    if "init" not in st.session_state:
        st.session_state["init"] = True

    st.set_page_config(page_title="MCP Agentic App (Part 2)", layout="wide")

    st.title("🔧 MCP Agentic Application – Part 2")
    st.markdown(
        "This app composes **two external MCP servers** (filesystem + web) "
        "with **your custom `local_insights` server** using an LLM for planning."
    )

    llm_cfg = load_llm_config()
    st.markdown(
        f"""
        ### Runtime configuration
        - **LLM backend:** `{llm_cfg.backend}`
        - **Model:** `{llm_cfg.model}`
        """
    )

    st.markdown("### User goal")
    user_goal = st.text_area(
        "Describe what you want the agent to do:",
        height=150,
        placeholder=(
            "Example: Search the web for recent information about MCP, "
            "clean the relevant text, and generate structured insights."
        ),
    )

    if st.button("Run agent", type="primary"):
        if not user_goal.strip():
            st.error("Please provide a non-empty goal.")
        else:
            with st.spinner("Running agent with MCP tools..."):
                try:
                    result = run_agent_sync(user_goal)
                except Exception as e:  # noqa: BLE001
                    st.error("Agent crashed while running.")
                    st.exception(e)
                    return

            st.subheader("✅ Final answer")
            st.write(result.final_answer)

            st.subheader("🔍 Tool calls log")
            if not result.tool_logs:
                st.write("No tool calls were recorded.")
            else:
                for log in result.tool_logs:
                    with st.expander(
                        f"Step {log.step} – {log.tool_name} "
                        f"({'OK' if log.success else 'ERROR'})"
                    ):
                        st.markdown(f"**Server:** `{log.server_name}`")
                        st.markdown("**Arguments:**")
                        st.json(log.arguments)
                        st.markdown("**Result preview:**")
                        st.text(log.result_preview)
                        if log.error:
                            st.markdown("**Error:**")
                            st.code(log.error)


main()
