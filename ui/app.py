"""Local Streamlit app: upload files, configure provider/RAG settings, trigger
ingestion, and chat with the agent while watching its live Thought/Action/
Observation trace. No auth, no multi-user state — single local session.
"""
import asyncio
import os
import sys
import uuid
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import ollama

from agent.config import load_config
from agent.core import Agent
from agent.providers.groq_provider import GroqProvider
from agent.providers.ollama_provider import _DEFAULT_TIMEOUT, OllamaProvider
from ui.ingestion import build_graph_index, build_vector_index, chunk_text, extract_text, make_ollama_embedder
from ui.rag_store import GraphStore, VectorStore

st.set_page_config(page_title="ReAct MCP Agent", layout="wide")

CONFIG = load_config(str(PROJECT_ROOT / "config.yaml"))
RAG_CONFIG = CONFIG["rag"]
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def get_ollama_models() -> list:
    try:
        client = ollama.Client(host=OLLAMA_HOST, timeout=_DEFAULT_TIMEOUT)
        return [m["model"] for m in client.list()["models"]]
    except Exception:
        return []


def build_provider(provider_name: str, model: str):
    temperature = CONFIG.get("temperature", 0.2)
    if provider_name == "ollama":
        return OllamaProvider({"model": model, "temperature": temperature})
    return GroqProvider({"model": model, "temperature": temperature})


st.title("ReAct MCP Agent — local test UI")

ollama_models = get_ollama_models()

with st.sidebar:
    st.header("Settings")

    provider_name = st.selectbox(
        "Generation provider", ["ollama", "groq"], index=0 if CONFIG["provider"] == "ollama" else 1
    )

    if provider_name == "ollama":
        if not ollama_models:
            st.warning(f"No models found on {OLLAMA_HOST}. Is Ollama running?")
        gen_model = st.selectbox("Generation model", ollama_models or ["(none found)"])
    else:
        gen_model = st.text_input("Groq model", value=CONFIG["groq"].get("model", "llama-3.1-8b-instant"))
        st.caption(
            "Groq is optional and only used for generation. It requires GROQ_API_KEY in .env. "
            "Leave the provider on 'ollama' to stay fully offline with zero API keys."
        )

    embedding_model = st.selectbox(
        "Embedding model (ollama)",
        ollama_models or ["(none found — try `ollama pull nomic-embed-text`)"],
    )

    rag_mode = st.radio("RAG mode", ["vector", "graph"], index=0 if RAG_CONFIG["mode"] == "vector" else 1)

    st.divider()
    st.header("Upload & ingest")

    uploaded_files = st.file_uploader(
        "Upload files",
        type=["csv", "xlsx", "pdf", "txt", "doc", "docx", "md"],
        accept_multiple_files=True,
    )

    max_size_bytes = RAG_CONFIG["max_file_size_mb"] * 1024 * 1024
    chunk_size = st.number_input("Chunk size (words)", min_value=50, max_value=2000, value=RAG_CONFIG["chunk_size"])
    chunk_overlap = st.number_input(
        "Chunk overlap (words)", min_value=0, max_value=chunk_size - 1,
        value=min(RAG_CONFIG["chunk_overlap"], chunk_size - 1),
    )

    if st.button("1. Parse & chunk"):
        all_chunks = []
        for f in uploaded_files or []:
            data = f.getvalue()
            if len(data) > max_size_bytes:
                st.error(f"{f.name} is larger than the {RAG_CONFIG['max_file_size_mb']}MB limit — skipped.")
                continue
            try:
                text = extract_text(f.name, data)
            except Exception as exc:
                st.error(f"Failed to parse {f.name}: {exc}")
                continue
            all_chunks.extend(chunk_text(text, source=f.name, chunk_size=chunk_size, chunk_overlap=chunk_overlap))
        st.session_state["pending_chunks"] = all_chunks
        st.session_state["pending_file_count"] = len(uploaded_files or [])

    pending_chunks = st.session_state.get("pending_chunks")
    if pending_chunks is not None:
        st.info(f"{len(pending_chunks)} chunks ready from {st.session_state.get('pending_file_count', 0)} file(s).")

        if rag_mode == "graph":
            cap = RAG_CONFIG["graph_chunk_cap"]
            st.warning(
                f"Graph mode will make {len(pending_chunks)} LLM call(s), one per chunk, to extract "
                f"entities/relationships. Safety cap: {cap} chunks."
            )
            if len(pending_chunks) > cap:
                st.error(
                    f"Chunk count ({len(pending_chunks)}) exceeds the safety cap ({cap}). "
                    "Raise `rag.graph_chunk_cap` in config.yaml if you really want to proceed."
                )
            else:
                confirmed = st.checkbox(f"I confirm I want to run {len(pending_chunks)} LLM extraction call(s).")
                if confirmed and st.button("2. Build graph index") and pending_chunks:
                    provider = build_provider(provider_name, gen_model)
                    store = GraphStore(str(PROJECT_ROOT / RAG_CONFIG["graph_store_path"]))
                    with st.spinner("Extracting entities and relationships..."):
                        triple_count = build_graph_index(pending_chunks, provider, store)
                    st.success(f"Graph index built: {triple_count} facts added.")
                    del st.session_state["pending_chunks"]
        else:
            if st.button("2. Build vector index") and pending_chunks:
                embed_fn = make_ollama_embedder(embedding_model, OLLAMA_HOST)
                store = VectorStore(str(PROJECT_ROOT / RAG_CONFIG["vector_store_dir"]))
                with st.spinner("Embedding and indexing chunks..."):
                    count = build_vector_index(pending_chunks, embed_fn, store)
                st.success(f"Vector index built: {count} chunks indexed.")
                del st.session_state["pending_chunks"]

st.divider()
st.header("Chat")

if "history" not in st.session_state:
    st.session_state["history"] = []

for turn in st.session_state["history"]:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

user_input = st.chat_input("Ask the agent something...")

if user_input:
    st.session_state["history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        trace_box = st.container()

        def on_step(step_record):
            with trace_box:
                with st.expander(f"Step {step_record['step']}", expanded=True):
                    st.markdown(f"**Thought:** {step_record.get('thought', '')}")
                    if step_record.get("action"):
                        st.markdown(f"**Action:** `{step_record['action']}`")
                        st.code(str(step_record.get("action_input")), language="json")
                    if step_record.get("observation"):
                        st.markdown(f"**Observation:** {step_record['observation']}")
                    if step_record.get("final_answer"):
                        st.markdown(f"**Final Answer:** {step_record['final_answer']}")
                    if step_record.get("error"):
                        st.markdown(f":red[Parser note: {step_record['error']}]")

        provider = build_provider(provider_name, gen_model)
        agent = Agent(CONFIG, provider)

        with st.spinner("Thinking..."):
            answer = asyncio.run(agent.run(user_input, on_step=on_step))

        st.markdown(answer)
        st.session_state["history"].append({"role": "assistant", "content": answer})
