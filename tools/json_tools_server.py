"""MCP server for quick JSON formatting/validation, wired to skills/json_tools_skill.md.
Handy for inspecting tool payloads or config snippets without leaving the agent.
"""
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("json_tools")


@mcp.tool()
def format_json(text: str, mode: str = "pretty", indent: int = 2) -> str:
    """Parse a JSON string and reformat it. mode: "pretty" (indented), "minify"
    (compact, no spaces), or "validate" (just report whether it parses). Returns
    an error message with the parse location if the JSON is invalid.
    """
    mode = mode.lower().strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return f"Invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}."

    if mode == "validate":
        return "Valid JSON."
    if mode == "minify":
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    if mode == "pretty":
        return json.dumps(data, indent=max(indent, 0), ensure_ascii=False)
    return f"Error: unknown mode '{mode}'. Choose from: pretty, minify, validate."


if __name__ == "__main__":
    mcp.run()
