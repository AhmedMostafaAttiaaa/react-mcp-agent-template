---
name: slugify
triggers:
  - "slugify"
  - "make a slug"
  - "url slug"
  - "url friendly"
  - "filename from"
  - "make it url safe"
tools:
  - slugify
---

Use `slugify(text, separator, max_length)` when the user wants a URL- or filename-safe version of
some text — a title turned into a slug, an anchor ID, or a stable filename.

It lowercases, strips accents (café → cafe), drops punctuation, and joins words with `-` by default.
Pass `separator="_"` if they want underscores, and `max_length` to cap the length (it trims on a
word boundary, never mid-word). This overlaps the text_case `kebab` style — prefer slugify when the
goal is specifically a URL/filename and accent-stripping matters.
