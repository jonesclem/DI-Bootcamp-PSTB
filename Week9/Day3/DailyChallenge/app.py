import os
import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# ---------- Environment & LangSmith setup ---------- #

# Load .env file if present
load_dotenv()

# Core keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# LangSmith / LangChain tracing flags (optional but recommended)
# Only enable tracing if an API key is present
if LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
    os.environ["LANGCHAIN_ENDPOINT"] = os.getenv(
        "LANGCHAIN_ENDPOINT",
        "https://api.smith.langchain.com",
    )

# Let downstream libraries see these too
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
if TAVILY_API_KEY:
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# ---------- Optional: import the agent API ---------- #

AGENT_AVAILABLE = False
agent_run_fn = None

try:
    # This assumes you will have a function `run_agent(query: str) -> dict`
    # defined in agentic_rag (e.g., via nbconvert to .py or separate module).
    from agentic_rag import run_agent  # type: ignore

    agent_run_fn = run_agent
    AGENT_AVAILABLE = True
except Exception:
    AGENT_AVAILABLE = False


# ---------- Utility: load agentic_rag.ipynb as text/JSON ---------- #

def load_notebook_preview(nb_path: str = "agentic_rag.ipynb", max_chars: int = 5000):
    """
    Try to load the notebook as JSON text for display in Streamlit.

    Returns (preview_text, error_message).
    """
    path = Path(nb_path)
    if not path.exists():
        return None, f"Notebook file not found at: {path.resolve()}"

    try:
        raw = path.read_text(encoding="utf-8")
        # Validate JSON; pretty-print a truncated version
        nb_json = json.loads(raw)
        pretty = json.dumps(nb_json, indent=2)
        if len(pretty) > max_chars:
            pretty = pretty[:max_chars] + "\n... (truncated)"
        return pretty, None
    except Exception as e:
        return None, f"Failed to read notebook as JSON: {e}"


# ---------- Streamlit UI ---------- #

st.set_page_config(page_title="Agentic RAG Demo", page_icon="🧠", layout="wide")

st.title("🧠 Agentic RAG + Tool-Using Agent")
st.write(
    "Ask a question and the app will route it through your agent (if available), "
    "or return a simulated response as a fallback."
)

with st.sidebar:
    st.header("Environment Status")

    st.markdown("**Keys loaded:**")
    st.write(f"GROQ_API_KEY: {'✅' if GROQ_API_KEY else '❌'}")
    st.write(f"TAVILY_API_KEY: {'✅' if TAVILY_API_KEY else '❌'}")
    st.write(f"GOOGLE_API_KEY: {'✅' if GOOGLE_API_KEY else '❌'}")
    st.write(f"LANGCHAIN_API_KEY: {'✅' if LANGCHAIN_API_KEY else '❌'}")

    st.markdown("---")
    st.markdown("**Agent module**")
    if AGENT_AVAILABLE:
        st.success("agentic_rag.run_agent is available ✅")
    else:
        st.warning("agentic_rag.run_agent not found – using simulated responses.")

    st.markdown("---")
    st.markdown("**Notebook Preview**")

    nb_preview, nb_error = load_notebook_preview()
    if nb_preview:
        with st.expander("Show agentic_rag.ipynb (JSON preview)", expanded=False):
            st.code(nb_preview, language="json")
    else:
        st.info(nb_error or "No notebook preview available.")


# ---------- Main interaction ---------- #

user_query = st.text_area(
    "Your question",
    placeholder="e.g. 'Summarize our internal RAG design doc with citations.'",
    height=150,
)

submit = st.button("Submit")

if submit:
    if not user_query.strip():
        st.error("Please enter a question before submitting.")
    else:
        with st.spinner("Thinking..."):
            try:
                if AGENT_AVAILABLE and agent_run_fn is not None:
                    # Expecting a dict like {"answer": str, "sources": list}
                    result = agent_run_fn(user_query)
                    if isinstance(result, dict):
                        answer = result.get("answer", "")
                        sources = result.get("sources", [])
                    else:
                        # If user returns a plain string for now
                        answer = str(result)
                        sources = []
                else:
                    # Fallback: simulated response
                    answer = (
                        "Simulated agent response (implement `run_agent` in "
                        "`agentic_rag.ipynb` to replace this).\n\n"
                        f"Echoing your question: {user_query}"
                    )
                    sources = []

            except Exception as e:
                st.error(f"Error while running the agent: {e}")
                answer = ""
                sources = []

        if answer:
            st.subheader("Answer")
            st.write(answer)

        if sources:
            st.subheader("Sources")
            for i, src in enumerate(sources, start=1):
                # Expecting each source to be a dict with 'title' and/or 'url' and/or 'snippet'
                title = src.get("title") or f"Source {i}"
                url = src.get("url")
                snippet = src.get("snippet") or src.get("text") or ""

                st.markdown(f"**{i}. {title}**")
                if url:
                    st.markdown(f"[Open source]({url})")
                if snippet:
                    st.write(snippet)
                st.markdown("---")