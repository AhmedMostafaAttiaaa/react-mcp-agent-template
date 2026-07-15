---
name: math_and_time
triggers:
  - "add"
  - "plus"
  - "what time"
  - "current time"
  - "word count"
  - "reverse"
  - "count words"
tools:
  - add
  - get_current_time
  - reverse_text
  - word_count
---

Use the `add` tool for arithmetic addition instead of computing it yourself.
Use `get_current_time` when the user asks about the current date or time.
Use `word_count` when the user asks how many words are in a piece of text.

Always pass arguments as a single JSON object matching the tool's schema.
