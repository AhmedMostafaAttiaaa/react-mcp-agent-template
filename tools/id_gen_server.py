"""MCP server for generating identifiers, wired to skills/id_gen_skill.md. Handy for
tagging documents, chunks, or trace runs with a unique ID.
"""
import secrets
import uuid

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("id_gen")

_MAX = 50


@mcp.tool()
def generate_id(style: str = "uuid4", count: int = 1) -> str:
    """Generate one or more random identifiers. style: "uuid4" (standard UUID),
    "hex" (16-char hex token), or "urlsafe" (URL-safe token). count is how many to
    produce (1-50). Returns one ID per line.
    """
    style = style.lower().strip()
    if count < 1 or count > _MAX:
        return f"Error: count must be between 1 and {_MAX}."

    generators = {
        "uuid4": lambda: str(uuid.uuid4()),
        "hex": lambda: secrets.token_hex(8),
        "urlsafe": lambda: secrets.token_urlsafe(12),
    }
    gen = generators.get(style)
    if gen is None:
        return f"Error: unknown style '{style}'. Choose from: {', '.join(generators)}."

    return "\n".join(gen() for _ in range(count))


if __name__ == "__main__":
    mcp.run()
