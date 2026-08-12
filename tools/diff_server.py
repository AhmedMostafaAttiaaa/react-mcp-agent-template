"""MCP server for line-level text diffing, wired to skills/diff_skill.md. Useful for
showing what changed between two versions of a document or answer.
"""
import difflib

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("diff_tool")


@mcp.tool()
def diff_text(a: str, b: str, label_a: str = "a", label_b: str = "b") -> str:
    """Produce a unified line-by-line diff between two texts. Lines prefixed with
    '-' are only in the first text, '+' only in the second, ' ' in both. Returns a
    note if the two texts are identical.
    """
    a_lines = a.splitlines()
    b_lines = b.splitlines()
    if a_lines == b_lines:
        return "No differences — the two texts are identical."

    diff = difflib.unified_diff(a_lines, b_lines, fromfile=label_a, tofile=label_b, lineterm="")
    lines = list(diff)

    added = sum(1 for ln in lines if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in lines if ln.startswith("-") and not ln.startswith("---"))
    summary = f"{added} line(s) added, {removed} line(s) removed:\n"
    return summary + "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
