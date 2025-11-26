#!/usr/bin/env python
# coding: utf-8

# Imports & environment

# In[ ]:


import os
from typing import List, Dict, Any

from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_groq import ChatGroq

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents import initialize_agent, AgentType, Tool

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set. Please add it to your .env.")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY
if TAVILY_API_KEY:
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY


# LLM & basic RAG components

# In[ ]:


# Groq LLM (choose any supported model)
llm = ChatGroq(
    model_name="llama3-8b-8192",
    temperature=0.1,
)

# Simple in-memory corpus for demo;
# replace with loaders for your real docs
raw_docs = [
    Document(
        page_content="Agentic RAG combines retrieval-augmented generation with tool-using agents "
        "that can call web search, query vector stores, and iteratively reason.",
        metadata={"source": "internal_notes.md"},
    ),
    Document(
        page_content="Tavily is a search API optimized for LLM agents, providing curated web results "
        "with citations and metadata.",
        metadata={"source": "tavily_overview.md"},
    ),
]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

docs = text_splitter.split_documents(raw_docs)

# Embeddings + FAISS vectorstore
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})


# Plain RAG chain with source docs

# In[ ]:


rag_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert assistant. Use ONLY the provided context to answer. "
            "If the answer is not in the context, say you don't know.\n\n"
            "When possible, cite sources by name from the metadata.\n\n"
            "Context:\n{context}",
        ),
        ("human", "{question}"),
    ]
)

rag_chain = (
    {"context": retriever, "question": lambda x: x["question"]}
    | rag_prompt
    | llm
    | StrOutputParser()
)


def rag_answer(question: str) -> Dict[str, Any]:
    """
    Simple RAG pipeline: retrieve docs from the vector store and answer using them.
    Returns both the answer and the underlying source documents for the UI.
    """
    source_docs = retriever.get_relevant_documents(question)
    context_text = "\n\n".join([d.page_content for d in source_docs])

    answer = rag_chain.invoke({"question": question, "context": context_text})

    sources = []
    for d in source_docs:
        sources.append(
            {
                "title": d.metadata.get("source", "unknown"),
                "snippet": d.page_content[:400] + ("..." if len(d.page_content) > 400 else ""),
                "url": d.metadata.get("url"),
            }
        )

    return {"answer": answer, "sources": sources}


# Tools: Tavily search + RAG as a tool

# In[ ]:


# Tavily web search tool
if not TAVILY_API_KEY:
    print("Warning: TAVILY_API_KEY not set. Web search tool will still be created but may fail.")

tavily_tool = TavilySearchResults(
    max_results=4,
    # Use environment variable TAVILY_API_KEY automatically
)

def rag_tool_fn(query: str) -> str:
    """Thin wrapper around rag_answer for use as an agent Tool."""
    result = rag_answer(query)
    return result["answer"]

rag_tool = Tool(
    name="internal_rag_qa",
    description=(
        "Use this tool to answer questions about the internal knowledge base. "
        "It performs retrieval-augmented generation over embedded documents."
    ),
    func=rag_tool_fn,
)


# Tool-using agent (LangChain agent)

# In[ ]:


tools = [
    rag_tool,
    tavily_tool,
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)


# Unified API for Streamlit: run_agent()

# In[ ]:


def run_agent(
    query: str,
    prefer_agent: bool = True,
) -> Dict[str, Any]:
    """
    Unified entrypoint for the Streamlit app.

    - If prefer_agent=True, route through the tool-using agent (rag tool + Tavily search).
    - In all cases, we also independently run the RAG pipeline to surface concrete sources
      for the UI, so you always have some citations.
    """
    # Always gather RAG-based sources
    rag_result = rag_answer(query)

    if prefer_agent:
        try:
            agent_answer = agent.run(query)
        except Exception as e:
            agent_answer = (
                f"[Agent failed, falling back to pure RAG]: {e}\n\n"
                f"{rag_result['answer']}"
            )
    else:
        agent_answer = rag_result["answer"]

    return {
        "answer": agent_answer,
        "sources": rag_result["sources"],
    }

