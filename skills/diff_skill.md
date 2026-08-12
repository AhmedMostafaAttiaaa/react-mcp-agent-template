---
name: diff_tool
triggers:
  - "diff"
  - "compare these"
  - "what changed"
  - "difference between"
  - "compare two"
tools:
  - diff_text
---

Use `diff_text(a, b, label_a, label_b)` when the user wants to see how two pieces of text differ —
two drafts, two versions of a document, or before/after of an edit.

The output is a unified diff: `-` lines are only in the first text, `+` only in the second. Report
the added/removed summary and the diff as returned; don't restate the whole texts. Pass meaningful
labels (e.g. "old", "new") when the user's framing implies them.
