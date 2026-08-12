"""MCP server for sorting the lines of a text block, wired to skills/sort_skill.md.
A small utility for tidying lists, keywords, or config lines.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sort_lines")


@mcp.tool()
def sort_lines(text: str, order: str = "asc", unique: bool = False, case_sensitive: bool = False) -> str:
    """Sort the non-empty lines of text. order: "asc" (A→Z) or "desc" (Z→A). If
    unique is true, duplicate lines are removed. If case_sensitive is false
    (default), sorting ignores case. Returns the sorted lines.
    """
    order = order.lower().strip()
    if order not in ("asc", "desc"):
        return f"Error: unknown order '{order}'. Choose from: asc, desc."

    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return "No lines to sort."

    if unique:
        seen = set()
        deduped = []
        for ln in lines:
            key = ln if case_sensitive else ln.lower()
            if key not in seen:
                seen.add(key)
                deduped.append(ln)
        lines = deduped

    key_fn = None if case_sensitive else str.lower
    lines.sort(key=key_fn, reverse=(order == "desc"))
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
