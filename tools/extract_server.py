"""MCP server for pulling structured tokens out of free text, wired to
skills/extract_skill.md. The counterpart to text_clean: instead of removing
URLs/emails, this collects them — useful for building metadata from a document.
"""
import re

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("extract")

_PATTERNS = {
    "emails": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "urls": re.compile(r"https?://\S+|www\.\S+"),
    "numbers": re.compile(r"-?\d+(?:\.\d+)?"),
    "hashtags": re.compile(r"#\w+"),
    "mentions": re.compile(r"@\w+"),
}


@mcp.tool()
def extract(text: str, kind: str = "emails", unique: bool = True) -> str:
    """Extract all matches of a given kind from text. kind: "emails", "urls",
    "numbers", "hashtags", or "mentions". If unique is true (default), duplicates
    are collapsed while preserving first-seen order. Returns a count and the matches.
    """
    kind = kind.lower().strip()
    pattern = _PATTERNS.get(kind)
    if pattern is None:
        return f"Error: unknown kind '{kind}'. Choose from: {', '.join(sorted(_PATTERNS))}."

    matches = pattern.findall(text)
    if unique:
        seen = set()
        deduped = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                deduped.append(m)
        matches = deduped

    if not matches:
        return f"No {kind} found."
    return f"Found {len(matches)} {kind}:\n" + "\n".join(matches)


if __name__ == "__main__":
    mcp.run()
