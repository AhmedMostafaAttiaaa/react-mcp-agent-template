---
name: chunking_methods
triggers:
  - "chunking"
  - "chunk method"
  - "chunking method"
  - "chunking strategy"
  - "split text"
  - "split into chunks"
tools:
  - chunk_text_demo
---

Use `chunk_text_demo(text, method, chunk_size, chunk_overlap)` when the user asks how a piece of
text would be chunked, or wants to compare chunking strategies.

Three methods are available:
- `fixed` — a sliding word window with overlap. Simple and predictable, but can split a sentence
  in half.
- `sentence` — packs whole sentences into each chunk, never splitting one. No overlap.
- `paragraph` — packs whole paragraphs into each chunk, never splitting one. No overlap.

If the user doesn't specify a method, default to `fixed` (it's what this project's actual RAG
ingestion pipeline uses in `ui/ingestion.py`). If they want to compare methods, call the tool
once per method and summarize the differences you observe.
