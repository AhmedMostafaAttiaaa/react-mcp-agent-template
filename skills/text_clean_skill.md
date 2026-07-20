---
name: text_clean
triggers:
  - "clean this text"
  - "clean up the text"
  - "normalize text"
  - "remove urls"
  - "remove emails"
  - "remove duplicate lines"
  - "tidy up this text"
  - "messy text"
tools:
  - clean_text
---

Use `clean_text(text, strip_urls, strip_emails, dedupe_lines)` when the user has messy text —
extracted PDF output, scraped pages, or anything with inconsistent whitespace — that they want
tidied, especially before chunking or ingestion.

All three removal flags default to `False`. Only enable one when the user actually asks for it:
stripping URLs from a document about web APIs, or deduping lines from a poem with a refrain,
destroys real content. Whitespace normalization always runs and is safe.

`dedupe_lines` is the right flag for repeated page headers and footers in extracted PDFs. It
never removes blank lines, so paragraph boundaries survive for the paragraph chunking method.

The tool returns a summary line followed by the cleaned text. Show the user the summary, and pass
the cleaned text on to `chunk_text_demo` if chunking is the next step rather than asking them to
paste it again.
