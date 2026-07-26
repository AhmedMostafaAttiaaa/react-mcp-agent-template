---
name: chunking_methods
description: Demonstrates and compares text chunking strategies used for RAG/document ingestion.
triggers:
  - "chunking"
  - "chunk method"
  - "chunking method"
  - "chunking strategy"
  - "text chunking"
  - "rag chunking"
  - "document chunking"
  - "split text"
  - "split into chunks"
  - "divide text"
  - "break text"
  - "how to chunk"
  - "chunk this"
  - "show chunks"
  - "chunk size"
  - "chunk overlap"
  - "overlapping chunks"
  - "sentence chunking"
  - "paragraph chunking"
  - "compare chunking"
  - "compare chunking methods"
tools:
  - chunk_text_demo
---

# Purpose

Use `chunk_text_demo(text, method, chunk_size, chunk_overlap)` whenever the user wants to:

- see how text would be chunked
- compare chunking strategies
- understand chunk size or overlap
- debug a RAG ingestion pipeline
- experiment with different chunking parameters

Do **not** call the tool if the user is only asking conceptual questions such as "What is chunking?" or "Why is overlap useful?" In those cases, answer directly.

---

# Available methods

## fixed

Sliding word window.

Characteristics:

- Uses `chunk_size`
- Uses `chunk_overlap`
- Fast
- Predictable chunk lengths
- May split sentences
- Best matches this project's ingestion pipeline

Default whenever the user does not specify a method.

---

## sentence

Groups complete sentences.

Characteristics:

- Never splits a sentence
- Ignores overlap
- Chunk lengths vary
- Better readability
- Better semantic boundaries

---

## paragraph

Groups complete paragraphs.

Characteristics:

- Never splits paragraphs
- Ignores overlap
- Largest semantic units
- Variable chunk sizes
- Best for well-structured documents

---

# Defaults

Unless the user specifies otherwise:

- method = `fixed`
- chunk_size = 200
- chunk_overlap = 50

If the user provides only some parameters, use defaults for the remainder.

---

# Tool usage rules

## Single method

Call the tool exactly once.

Example:

> "Chunk this text."

↓

```
chunk_text_demo(
    text,
    "fixed",
    200,
    50
)
```

---

## Explicit method

Respect the user's requested method.

Examples:

- fixed
- sentence
- paragraph

---

## Comparison requests

If the user asks to compare chunking methods:

- Call the tool once for each requested method.
- If no methods are specified, compare all three:
  - fixed
  - sentence
  - paragraph

After all tool calls:

Summarise:

- number of chunks
- average chunk size
- whether sentences are split
- whether overlap exists
- semantic coherence
- which method is likely best for RAG retrieval

Do not speculate beyond what the tool output shows.

---

# Recommendations

When appropriate:

Recommend **fixed** when:

- matching this project's ingestion pipeline
- consistent embedding sizes are preferred
- overlap helps retrieval

Recommend **sentence** when:

- preserving natural language boundaries
- documents contain long prose

Recommend **paragraph** when:

- documents already have meaningful paragraph structure
- preserving context is more important than chunk uniformity

---

# Parameter guidance

If the user asks for advice:

Small chunks (100–200 words)

- higher retrieval precision
- less context

Medium chunks (200–400 words)

- good general-purpose default

Large chunks (400–800 words)

- more context
- fewer embeddings
- may reduce retrieval precision

Overlap:

0

- no redundancy
- smallest index

20–50 words

- good general-purpose setting

50–100 words

- stronger context continuity
- more duplicated text
- larger vector store

---

# Error handling

If:

- the text is empty
- the text contains only whitespace
- chunk_size is invalid
- chunk_overlap is negative
- chunk_overlap ≥ chunk_size (for fixed)

Explain the issue and ask the user to provide valid input instead of calling the tool again with guessed values.

---

# Output style

Keep explanations concise.

When demonstrating chunking:

1. Briefly explain the chosen strategy.
2. Present the tool output.
3. Summarise notable observations.
4. If comparing methods, finish with a short recommendation tailored to the user's goal.

Never invent chunk contents or statistics that were not returned by the tool.
