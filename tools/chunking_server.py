"""MCP server demonstrating different text chunking strategies, wired to
skills/chunking_skill.md. Useful for showing/comparing how fixed-size,
sentence-based, and paragraph-based chunking split the same text differently.
"""
import re

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("chunking")

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _chunk_fixed(words: list, chunk_size: int, chunk_overlap: int) -> list:
    if chunk_overlap >= chunk_size:
        chunk_overlap = max(chunk_size - 1, 0)
    chunks = []
    step = chunk_size - chunk_overlap
    for start in range(0, len(words), step):
        window = words[start : start + chunk_size]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + chunk_size >= len(words):
            break
    return chunks


def _pack_by_words(units: list, chunk_size: int) -> list:
    """Greedily packs whole units (sentences/paragraphs) into chunks up to
    ~chunk_size words each, never splitting a unit across chunks."""
    chunks = []
    current: list = []
    current_words = 0
    for unit in units:
        unit_words = len(unit.split())
        if current and current_words + unit_words > chunk_size:
            chunks.append(" ".join(current))
            current = []
            current_words = 0
        current.append(unit)
        current_words += unit_words
    if current:
        chunks.append(" ".join(current))
    return chunks


@mcp.tool()
def chunk_text_demo(text: str, method: str = "fixed", chunk_size: int = 50, chunk_overlap: int = 10) -> str:
    """Chunk a piece of text using one of three strategies and return the resulting
    chunks for comparison. method: "fixed" (sliding word window with overlap, may
    split mid-sentence), "sentence" (packs whole sentences up to ~chunk_size words,
    no overlap), or "paragraph" (packs whole paragraphs up to ~chunk_size words,
    no overlap).
    """
    method = method.lower().strip()

    if method == "fixed":
        chunks = _chunk_fixed(text.split(), chunk_size, chunk_overlap)
    elif method == "sentence":
        sentences = [s.strip() for s in _SENTENCE_RE.split(text) if s.strip()]
        chunks = _pack_by_words(sentences, chunk_size)
    elif method == "paragraph":
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = _pack_by_words(paragraphs, chunk_size)
    else:
        return f"Error: unknown method '{method}'. Choose from: fixed, sentence, paragraph."

    if not chunks:
        return "No text to chunk."

    header = f"Method: {method} | chunk_size={chunk_size}"
    if method == "fixed":
        header += f" overlap={chunk_overlap}"
    lines = [header, f"Produced {len(chunks)} chunk(s):"]
    for i, chunk in enumerate(chunks):
        lines.append(f"\n--- Chunk {i} ({len(chunk.split())} words) ---\n{chunk}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
