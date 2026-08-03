"""MCP server for converting text between common casing styles, wired to
skills/text_case_skill.md. Handy for normalizing headings, identifiers, or
metadata keys before indexing.
"""
import re

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("text_case")

_WORD_RE = re.compile(r"[A-Za-z0-9]+")


def _words(text: str) -> list:
    # Split on non-alphanumerics AND on camelCase boundaries so "myVariableName"
    # and "my-variable name" both tokenize the same way.
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    return _WORD_RE.findall(spaced)


@mcp.tool()
def to_case(text: str, style: str = "snake") -> str:
    """Convert text to a casing style. style: "upper", "lower", "title",
    "snake" (snake_case), "kebab" (kebab-case), or "camel" (camelCase).
    Returns the converted text.
    """
    style = style.lower().strip()
    if not text.strip():
        return "No text to convert."

    if style == "upper":
        return text.upper()
    if style == "lower":
        return text.lower()

    words = _words(text)
    if not words:
        return "No convertible words found."

    if style == "title":
        return " ".join(w.capitalize() for w in words)
    if style == "snake":
        return "_".join(w.lower() for w in words)
    if style == "kebab":
        return "-".join(w.lower() for w in words)
    if style == "camel":
        first, *rest = words
        return first.lower() + "".join(w.capitalize() for w in rest)

    return f"Error: unknown style '{style}'. Choose from: upper, lower, title, snake, kebab, camel."


if __name__ == "__main__":
    mcp.run()
