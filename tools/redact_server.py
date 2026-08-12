"""MCP server for masking sensitive tokens in text, wired to skills/redact_skill.md.
The privacy counterpart to the extract server: instead of collecting emails/urls/
numbers, this replaces them with placeholders before text is shared or logged.
"""
import re

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("redact")

_PATTERNS = {
    "emails": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "urls": re.compile(r"https?://\S+|www\.\S+"),
    "phones": re.compile(r"\+?\d[\d\s().-]{7,}\d"),
}


@mcp.tool()
def redact_text(text: str, kinds: str = "emails,phones") -> str:
    """Replace sensitive tokens with [REDACTED-<kind>] placeholders. kinds is a
    comma-separated list of any of: emails, urls, phones. Returns the redacted text
    plus a count of how many replacements were made per kind.
    """
    if not text.strip():
        return "No text to redact."

    requested = [k.strip().lower() for k in kinds.split(",") if k.strip()]
    unknown = [k for k in requested if k not in _PATTERNS]
    if unknown:
        return f"Error: unknown kind(s) {unknown}. Choose from: {', '.join(sorted(_PATTERNS))}."

    counts = {}
    for kind in requested:
        placeholder = f"[REDACTED-{kind[:-1].upper()}]"  # emails -> EMAIL
        text, n = _PATTERNS[kind].subn(placeholder, text)
        counts[kind] = n

    summary = ", ".join(f"{k}: {n}" for k, n in counts.items())
    return f"Redacted ({summary})\n\n{text}"


if __name__ == "__main__":
    mcp.run()
