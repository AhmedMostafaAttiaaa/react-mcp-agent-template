---
name: extract
triggers:
  - "extract emails"
  - "extract urls"
  - "extract numbers"
  - "pull out"
  - "find all emails"
  - "find all urls"
  - "list the links"
  - "hashtags"
tools:
  - extract
---

Use `extract(text, kind, unique)` when the user wants to collect specific tokens out of a piece of
text: `emails`, `urls`, `numbers`, `hashtags`, or `mentions`.

This is the mirror image of the text_clean skill — text_clean *removes* URLs/emails, this one
*gathers* them. Leave `unique=true` unless the user needs every occurrence including repeats.
Return the matches as given; don't invent or normalize values the regex didn't produce.
