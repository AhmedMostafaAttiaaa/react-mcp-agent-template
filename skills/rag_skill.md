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
