---
name: text_case
triggers:
  - "convert case"
  - "change case"
  - "uppercase"
  - "lowercase"
  - "title case"
  - "snake_case"
  - "camelcase"
  - "kebab-case"
tools:
  - to_case
---

Use `to_case(text, style)` when the user wants to reformat text into a casing style: `upper`,
`lower`, `title`, `snake`, `kebab`, or `camel`.

The tokenizer handles mixed input — it splits on spaces, punctuation, and camelCase boundaries —
so "myVariableName", "my-variable name", and "My Variable Name" all convert consistently. If the
user doesn't name a style, ask which one rather than guessing, since the right choice depends on
where the text is going (identifiers vs. headings).
