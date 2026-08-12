"""MCP server for turning text into URL/file-safe slugs, wired to skills/slugify_skill.md.
Useful for deriving stable filenames or anchor IDs from titles.
"""
import re
import unicodedata

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("slugify")


@mcp.tool()
def slugify(text: str, separator: str = "-", max_length: int = 0) -> str:
    """Convert text to a lowercase slug: strip accents, drop punctuation, and join
    words with separator (default "-"). If max_length > 0, the slug is trimmed to
    that length without cutting a word in half. Returns the slug.
    """
    if not text.strip():
        return "No text to slugify."

    # Decompose accented characters and drop the combining marks (café -> cafe).
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")

    words = re.findall(r"[A-Za-z0-9]+", ascii_text.lower())
    if not words:
        return "No sluggable characters found."

    slug = separator.join(words)

    if max_length and len(slug) > max_length:
        # Only back off to the previous separator if the cut lands mid-word; if the
        # character just past the limit is already a separator, the trim ended on a
        # clean word boundary and no word needs to be dropped.
        trimmed = slug[:max_length]
        if separator in trimmed and slug[max_length] != separator:
            trimmed = trimmed.rsplit(separator, 1)[0]
        slug = trimmed.rstrip(separator)

    return slug


if __name__ == "__main__":
    mcp.run()
