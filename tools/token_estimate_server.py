"""MCP server for rough LLM token estimates, wired to skills/token_estimate_skill.md.
No tokenizer dependency — uses the common ~4-chars-per-token heuristic so you can
sanity-check whether text fits a context window before sending it.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("token_estimate")

# English averages roughly 4 characters per token across common BPE tokenizers.
# This is an estimate, not an exact count — good enough for budgeting, not billing.
_CHARS_PER_TOKEN = 4.0


@mcp.tool()
def estimate_tokens(text: str, context_window: int = 8192) -> str:
    """Estimate the token count of text using the ~4-chars-per-token heuristic, and
    report what fraction of a given context_window it would use. This is an
    approximation for budgeting, not an exact tokenizer count.
    """
    if not text.strip():
        return "No text to estimate."
    if context_window <= 0:
        return "Error: context_window must be greater than 0."

    chars = len(text)
    words = len(text.split())
    est_tokens = max(1, round(chars / _CHARS_PER_TOKEN))
    pct = est_tokens / context_window * 100
    fits = "fits" if est_tokens <= context_window else "EXCEEDS"

    return (
        f"~{est_tokens} tokens (est.) from {chars} chars / {words} words\n"
        f"{fits} a {context_window}-token window — ~{pct:.1f}% used\n"
        f"(heuristic: ~{_CHARS_PER_TOKEN:g} chars/token; not an exact tokenizer count)"
    )


if __name__ == "__main__":
    mcp.run()
