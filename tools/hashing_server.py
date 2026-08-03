"""MCP server for hashing text, wired to skills/hashing_skill.md. A stable content
hash is a cheap way to give a document or chunk a deterministic ID or to detect
that two pieces of text are identical before re-embedding them.
"""
import hashlib

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hashing")

_ALGOS = {"md5", "sha1", "sha256"}


@mcp.tool()
def hash_text(text: str, algo: str = "sha256", short: bool = False) -> str:
    """Compute a hex digest of the given text. algo: "md5", "sha1", or "sha256"
    (default). If short is true, return only the first 12 hex characters — enough
    for a human-readable ID, not for cryptographic use.
    """
    algo = algo.lower().strip()
    if algo not in _ALGOS:
        return f"Error: unknown algo '{algo}'. Choose from: md5, sha1, sha256."

    digest = hashlib.new(algo, text.encode("utf-8")).hexdigest()
    if short:
        digest = digest[:12]
    return f"{algo}{'(short)' if short else ''}: {digest}"


if __name__ == "__main__":
    mcp.run()
