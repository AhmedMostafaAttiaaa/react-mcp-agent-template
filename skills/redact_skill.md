---
name: redact
triggers:
  - "redact"
  - "mask"
  - "anonymize"
  - "hide emails"
  - "remove personal"
  - "scrub"
tools:
  - redact_text
---

Use `redact_text(text, kinds)` when the user wants to mask sensitive tokens before sharing or
logging text: `emails`, `urls`, and/or `phones` (comma-separated). Each match becomes a
`[REDACTED-<KIND>]` placeholder.

This is the privacy mirror of the extract skill — extract *collects* these tokens, redact *hides*
them. Be honest about scope: these are simple pattern matches, not a guaranteed PII scrubber. Names,
addresses, and unusual formats won't be caught, so tell the user to eyeball the result before
trusting it for anything sensitive.
