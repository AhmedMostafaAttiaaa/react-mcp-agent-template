---
name: id_gen
triggers:
  - "generate id"
  - "generate uuid"
  - "random id"
  - "unique id"
  - "give me a uuid"
  - "random token"
tools:
  - generate_id
---

Use `generate_id(style, count)` when the user needs one or more random identifiers: `uuid4`
(standard UUID, the default), `hex` (short hex token), or `urlsafe` (URL-safe token).

Pass `count` when they want several at once (up to 50). These come from Python's `secrets`/`uuid`,
so they're suitable as random IDs — return them exactly as generated.
