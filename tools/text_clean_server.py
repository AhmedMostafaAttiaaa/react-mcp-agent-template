"""MCP server for pre-ingestion text cleanup, wired to skills/text_clean_skill.md.

Scanned PDFs and scraped pages arrive with repeated headers/footers, hard-wrapped
lines, and stray URLs. Feeding that straight into chunking wastes tokens and
pollutes embeddings, so this runs before the chunker.
"""
import re

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("text_clean")

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_SPACES_RE = re.compile(r"[ \t]+")
_BLANK_LINES_RE = re.compile(r"\n{3,}")


@mcp.tool()
def clean_text(
    text: str,
    strip_urls: bool = False,
    strip_emails: bool = False,
    dedupe_lines: bool = False,
) -> str:
    """Normalize messy text before chunking: collapse runs of spaces and blank lines,
    trim trailing whitespace, and optionally remove URLs, remove email addresses, or
    drop repeated lines (useful for page headers/footers in extracted PDFs).
    Returns the cleaned text plus a short summary of what changed.
    """
    if not text.strip():
        return "No text to clean."

    original_chars = len(text)
    original_lines = len([ln for ln in text.splitlines() if ln.strip()])
    notes = []

    if strip_urls:
        text, n = _URL_RE.subn("", text)
        if n:
            notes.append(f"removed {n} URL(s)")
    if strip_emails:
        text, n = _EMAIL_RE.subn("", text)
        if n:
            notes.append(f"removed {n} email(s)")

    text = _SPACES_RE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.splitlines())

    if dedupe_lines:
        seen = set()
        kept = []
        removed = 0
        for line in text.splitlines():
            key = line.strip().lower()
            # Blank lines are structural (they delimit paragraphs), so they are
            # never deduped — only repeated content lines are.
            if not key:
                kept.append(line)
                continue
            if key in seen:
                removed += 1
                continue
            seen.add(key)
            kept.append(line)
        text = "\n".join(kept)
        if removed:
            notes.append(f"dropped {removed} duplicate line(s)")

    text = _BLANK_LINES_RE.sub("\n\n", text).strip()

    cleaned_lines = len([ln for ln in text.splitlines() if ln.strip()])
    saved = original_chars - len(text)
    summary = (
        f"Cleaned: {original_chars} -> {len(text)} chars ({saved} removed), "
        f"{original_lines} -> {cleaned_lines} non-empty lines"
    )
    if notes:
        summary += f" [{'; '.join(notes)}]"
    return f"{summary}\n\n--- Cleaned text ---\n{text}"


if __name__ == "__main__":
    mcp.run()
