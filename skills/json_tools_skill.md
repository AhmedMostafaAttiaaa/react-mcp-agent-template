---
name: json_tools
triggers:
  - "format json"
  - "pretty print json"
  - "minify json"
  - "validate json"
  - "is this valid json"
  - "prettify json"
tools:
  - format_json
---

Use `format_json(text, mode, indent)` when the user has a JSON string they want reformatted or
checked: `pretty` (indented, the default), `minify` (compact), or `validate` (just parse-check).

On invalid input the tool returns the exact line/column of the parse error — pass that straight
through to the user rather than guessing what's wrong. Don't hand-edit the JSON yourself; let the
tool do the reformatting so whitespace and escaping stay correct.
