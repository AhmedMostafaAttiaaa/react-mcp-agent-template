"""MCP server exposing query_documents (vector mode) and query_graph (graph mode)
over whatever the Streamlit UI has ingested into data/. Reads the same config.yaml
as the rest of the project so store paths and the embedding model stay in sync.
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.fastmcp import FastMCP

from agent.config import load_config
from ui.ingestion import make_ollama_embedder
from ui.rag_store import GraphStore, VectorStore

config = load_config(str(PROJECT_ROOT / "config.yaml"))
rag_config = config["rag"]
embedding_config = config["embedding"]

mcp = FastMCP("rag")

_embedder = None


def _get_embedder():
    global _embedder
    if _embedder is None:
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        _embedder = make_ollama_embedder(embedding_config["model"], host)
    return _embedder


@mcp.tool()
def query_documents(query: str, top_k: int = 5) -> str:
    """Search ingested documents in the vector index and return the most relevant chunks."""
    store = VectorStore(str(PROJECT_ROOT / rag_config["vector_store_dir"]))
    if store.is_empty():
        return "No documents have been ingested into the vector index yet. Upload and ingest a file in vector mode in the UI first."
    query_embedding = _get_embedder()(query)
    hits = store.query(query_embedding, n_results=top_k)
    if not hits:
        return "No relevant chunks found."
    lines = [f"[{hit['metadata'].get('source', 'unknown')}] {hit['text']}" for hit in hits]
    return "\n\n".join(lines)


@mcp.tool()
def query_graph(entity: str, hops: int = 1) -> str:
    """Search the ingested graph index for facts connected to an entity, up to N hops away."""
    store = GraphStore(str(PROJECT_ROOT / rag_config["graph_store_path"]))
    if store.is_empty():
        return "No graph index has been built yet. Upload and ingest a file in graph mode in the UI first."
    facts = store.query(entity, hops=hops)
    if not facts:
        return f"No facts found for '{entity}' in the graph index."
    lines = [f"{f['subject']} --{f['relation']}--> {f['object']} (source: {f['source']})" for f in facts]
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
