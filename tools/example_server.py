"""Placeholder MCP server with a few dummy tools, wired to skills/example_skill.md."""
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("example")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def get_current_time() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


@mcp.tool()
def word_count(text: str) -> int:
    """Count the whitespace-separated words in a piece of text."""
    return len(text.split())


if __name__ == "__main__":
    mcp.run()
