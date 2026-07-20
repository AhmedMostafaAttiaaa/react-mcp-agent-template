"""MCP server for quick text profiling, wired to skills/text_stats_skill.md.

Complements the chunking/RAG pipeline: `analyze_text` describes the shape of a
document, and `estimate_chunks` predicts how many chunks a given chunk_size
would produce before you pay for an actual ingest.
"""
import re
from collections import Counter

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("text_stats")

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"[a-z0-9']+")

# Deliberately small — enough to stop the top-keywords list from being all
# "the/and/of", without pretending to be a real NLP stopword corpus.
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by", "can", "for",
    "from", "had", "has", "have", "he", "her", "his", "i", "if", "in", "into",
    "is", "it", "its", "of", "on", "or", "she", "that", "the", "their", "them",
    "then", "there", "these", "they", "this", "to", "was", "we", "were", "what",
    "when", "which", "who", "will", "with", "would", "you", "your",
}

_WORDS_PER_MINUTE = 200


@mcp.tool()
def analyze_text(text: str, top_keywords: int = 5) -> str:
    """Profile a piece of text: character/word/sentence/paragraph counts, average
    sentence length, estimated reading time, and the most frequent non-stopword
    terms. Use this to understand the shape of a document before chunking it.
    """
    words = text.split()
    if not words:
        return "No text to analyze."

    sentences = [s for s in _SENTENCE_RE.split(text) if s.strip()]
    paragraphs = [p for p in text.split("\n\n") if p.strip()]

    tokens = [w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS and len(w) > 2]
    keywords = Counter(tokens).most_common(max(top_keywords, 0))

    avg_sentence = len(words) / len(sentences) if sentences else len(words)
    reading_minutes = len(words) / _WORDS_PER_MINUTE

    lines = [
        f"Characters:      {len(text)}",
        f"Words:           {len(words)}",
        f"Sentences:       {len(sentences)}",
        f"Paragraphs:      {len(paragraphs)}",
        f"Avg sentence:    {avg_sentence:.1f} words",
        f"Reading time:    ~{reading_minutes:.1f} min (at {_WORDS_PER_MINUTE} wpm)",
    ]
    if keywords:
        formatted = ", ".join(f"{term} ({count})" for term, count in keywords)
        lines.append(f"Top keywords:    {formatted}")
    return "\n".join(lines)


@mcp.tool()
def estimate_chunks(text: str, chunk_size: int = 300, chunk_overlap: int = 55) -> str:
    """Estimate how many chunks a fixed-size sliding window would produce for this
    text, without actually chunking or embedding it. Defaults match the rag.chunk_size
    and rag.chunk_overlap settings in config.yaml.
    """
    total_words = len(text.split())
    if total_words == 0:
        return "No text to estimate."
    if chunk_size <= 0:
        return "Error: chunk_size must be greater than 0."
    if chunk_overlap >= chunk_size:
        return f"Error: chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})."

    step = chunk_size - chunk_overlap
    if total_words <= chunk_size:
        n_chunks = 1
    else:
        n_chunks = 1 + -(-(total_words - chunk_size) // step)  # ceiling division

    return (
        f"Words: {total_words} | chunk_size={chunk_size} overlap={chunk_overlap} (step={step})\n"
        f"Estimated chunks: {n_chunks}\n"
        f"Each chunk carries {chunk_overlap} words of context from the previous one."
    )


if __name__ == "__main__":
    mcp.run()
