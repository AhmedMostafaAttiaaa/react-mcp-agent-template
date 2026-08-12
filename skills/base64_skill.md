---
name: base64_tool
triggers:
  - "base64"
  - "base 64"
  - "encode this"
  - "decode this"
  - "b64"
tools:
  - base64_transform
---

Use `base64_transform(text, mode)` when the user wants to Base64-encode or decode a string:
`encode` (text → base64) or `decode` (base64 → text).

Decoding validates the input and only returns text that is valid UTF-8 — if it gets non-Base64 or
binary bytes, it says so rather than emitting garbage. Pass the tool's message through as-is on
those errors instead of trying to decode by hand.
