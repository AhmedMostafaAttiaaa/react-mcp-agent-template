---
name: sort_lines
triggers:
  - "sort lines"
  - "sort these"
  - "sort alphabetically"
  - "order these lines"
  - "sort the list"
  - "dedupe and sort"
tools:
  - sort_lines
---

Use `sort_lines(text, order, unique, case_sensitive)` when the user gives a list of lines and wants
them ordered: `asc` (A→Z, default) or `desc`.

Set `unique=true` when they also want duplicates removed. Sorting ignores case by default; only pass
`case_sensitive=true` if the user cares that uppercase sorts before lowercase. Return the tool's
output directly rather than re-ordering the lines yourself.
