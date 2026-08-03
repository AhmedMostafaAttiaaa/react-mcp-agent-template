---
name: token_estimate
triggers:
  - "how many tokens"
  - "estimate tokens"
  - "token count"
  - "context window"
  - "will it fit"
  - "fit in context"
  - "token budget"
tools:
  - estimate_tokens
---

Use `estimate_tokens(text, context_window)` when the user wants to know roughly how many tokens a
piece of text is, or whether it will fit in a model's context window.

Always present the result as an estimate, never an exact count — the tool uses a ~4-chars-per-token
heuristic, not a real tokenizer, so it can be off for code, non-English text, or unusual formatting.
If the user names a specific model, pass its context window (e.g. 8192, 32768, 128000) so the
"fits / exceeds" verdict is meaningful. This pairs with the text_stats `estimate_chunks` tool when
planning ingestion: chunks for retrieval sizing, tokens for prompt-budget sizing.
