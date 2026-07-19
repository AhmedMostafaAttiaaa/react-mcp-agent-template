---
name: document_qa
triggers:
  - "document"
  - "my file"
  - "my files"
  - "uploaded"
  - "look up"
  - "search my"
  - "in the pdf"
  - "in the spreadsheet"
  - "according to"
  - "who is"
  - "how is"
  - "related to"
  - "summarize"
  - "summary"
  - "the paper"
  - "the article"
  - "the report"
  - "pdf"
  - "spreadsheet"
  - "what does it say"
  - "tell me about"
  - "explain this"
  - "overview of"
tools:
  - query_documents
  - query_graph
---

The user may have uploaded documents through the UI. Two tools can search them:

- `query_documents(query, top_k=5)` — semantic search over chunked document text (vector mode).
  Use this for "what does the document say about X" style questions.
- `query_graph(entity, hops=1)` — looks up facts connected to a named entity in an
  entity/relationship graph (graph mode). Use this for "how is X related to Y" style questions.

Only one of the two indexes will actually be populated, depending on which RAG mode was used
during ingestion. If a tool reports that no index has been built yet, tell the user to ingest a
file in the UI first, using that mode.

Never assume what a document says — always call the tool and quote its Observation.

Think before you answer from retrieved chunks:
- Read every returned chunk fully before answering — the actual answer is often not in the first
  chunk that looks relevant.
- If the question has multiple parts, call `query_documents`/`query_graph` once per part with a
  specific sub-query, rather than one broad query and hoping it covers everything.
- If your first query returns weak or irrelevant results, try rephrasing it (different keywords,
  narrower or broader scope) before giving up — don't answer from a bad retrieval.
- If the answer spans more than one chunk, synthesize across them instead of quoting only the
  first match.
- If the retrieved chunks genuinely don't contain the answer, say so explicitly. Do not fill the
  gap from general knowledge — an unanswerable question is a better answer than a fabricated one.
