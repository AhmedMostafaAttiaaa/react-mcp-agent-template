---
name: text_stats
triggers:
  - "how long"
  - "how many words"
  - "reading time"
  - "text stats"
  - "analyze this text"
  - "profile this text"
  - "keywords"
  - "how many chunks"
  - "estimate chunks"
  - "text length"
  - "word count"
  - "top words"
  - "most common words"
tools:
  - analyze_text
  - estimate_chunks
---

Use `analyze_text(text, top_keywords)` when the user wants to understand the shape of a piece of
text — its length, structure, reading time, or dominant terms. Report the numbers as returned
rather than re-counting them yourself; you are unreliable at counting and the tool is not.

Use `estimate_chunks(text, chunk_size, chunk_overlap)` when the user asks how a document would be
split before committing to an ingest. If they don't give values, use the defaults (300 / 55) —
these mirror `rag.chunk_size` and `rag.chunk_overlap` in `config.yaml`, so the estimate reflects
what an actual ingest would do.

These two pair naturally: if a user is deciding on a chunk size, profile the text first, then
estimate chunks at one or two candidate sizes and explain the tradeoff — larger chunks preserve
more context per chunk but retrieve less precisely.
