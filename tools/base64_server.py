"""MCP server for Base64 encode/decode of text, wired to skills/base64_skill.md.
Useful for inspecting encoded payloads or preparing small blobs.
"""
import base64
import binascii

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("base64_tool")


@mcp.tool()
def base64_transform(text: str, mode: str = "encode") -> str:
    """Base64-encode or -decode text (UTF-8). mode: "encode" (text -> base64) or
    "decode" (base64 -> text). Returns an error if decode input isn't valid Base64
    or doesn't decode to UTF-8 text.
    """
    mode = mode.lower().strip()
    if not text:
        return "No text provided."

    if mode == "encode":
        return base64.b64encode(text.encode("utf-8")).decode("ascii")
    if mode == "decode":
        try:
            raw = base64.b64decode(text, validate=True)
        except (binascii.Error, ValueError):
            return "Error: input is not valid Base64."
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return "Error: decoded bytes are not valid UTF-8 text (binary data?)."
    return f"Error: unknown mode '{mode}'. Choose from: encode, decode."


if __name__ == "__main__":
    mcp.run()
