---
name: hashing
triggers:
  - "hash this"
  - "hash of"
  - "md5"
  - "sha1"
  - "sha256"
  - "checksum"
  - "content hash"
tools:
  - hash_text
---

Use `hash_text(text, algo, short)` when the user wants a hash or checksum of some text, or a
deterministic ID derived from content.

`sha256` is the default and the right choice for content IDs and dedup checks. Only use `md5`/`sha1`
if the user explicitly asks — remind them those are unsuitable for security purposes. Pass
`short=true` when they want a compact human-readable ID rather than the full digest.
