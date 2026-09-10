# Architecture: Learn (PDF RAG)

A lightweight, event-driven PDF RAG pipeline combining **FastAPI**, **Inngest**, **Google GenAI**, and **Qdrant**.

---

## 1. System Pipelines

### A. Ingestion Flow (Event-Driven)
Triggered asynchronously via Inngest event `rag/ingest_pdf`:

```text
[PDF File]
   │
   ▼
[Step 1: load-and-chunk] ────► LlamaIndex PDFReader + SentenceSplitter (1000/200)
   │                           Returns: RAGChunkAndSrc
   ▼
[Step 2: embed-and-upsert] ──► Gemini embed_content (gemini-embedding-001, 3072d)
   │                           Qdrant upsert (collection: "docs", cosine)
   ▼                           Returns: RAGUpsertResult
[Qdrant Storage]
```

### B. Retrieval & Synthesis Flow (Planned)
Synchronous query endpoint for Q&A:

```text
[User Query]
   │
   ▼
[Embed Query] ───────────────► Gemini Embedding (RETRIEVAL_QUERY)
   │
   ▼
[Vector Search] ─────────────► Qdrant query_points (top_k=5)
   │                           Returns: RAGSearchResult (contexts, sources)
   ▼
[LLM Generation] ────────────► Gemini Chat / LlamaIndex LLM
   │                           Returns: RAGQueryResult (answer, sources, num_context)
[Response]
```

---

## 2. Component Map & Contracts

| Module | Core Responsibility | Key Types / I/O |
| :--- | :--- | :--- |
| [main.py](file:///f:/Learn/src/learn/main.py) | FastAPI app + Inngest durable workflow runner (`rag_agent_pdf`) | Inngest Event -> `RAGUpsertResult` |
| [custom_types.py](file:///f:/Learn/src/learn/custom_types.py) | Pydantic data schemas across pipeline steps | `RAGChunkAndSrc`, `RAGUpsertResult`, `RAGSearchResult`, `RAGQueryResult` |
| [data_loader.py](file:///f:/Learn/src/learn/data_loader.py) | PDF text extraction (`PDFReader`), chunking (`SentenceSplitter`), Gemini embeddings | Input: `path: str` / `list[str]`<br>Output: `chunks: list[str]`, `embeddings: list[list[float]]` |
| [vector_db.py](file:///f:/Learn/src/learn/vector_db.py) | Qdrant client wrapper for collection creation, batch upsert, and similarity search | Input: `ids, vectors, payloads`<br>Output: `{"contexts": [...], "sources": {...}}` |
| `qdrant_storage/` | Local persistence directory for Qdrant | Vector index and payload storage |

---

## 3. Project Structure

```text
Learn/
├── pyproject.toml              # Dependencies & scripts (FastAPI, Inngest, LlamaIndex, Qdrant)
├── README.md                   # Project overview
├── Project-data/
│   ├── ARCHITECTURE.md         # This file
│   ├── CONCEPTS_DECODED.md     # In-depth mental models & tutorial-escape guide
│   └── PROJECT_STATUS_SUMMARY.txt # Quick status cheat-sheet
└── src/
    └── learn/
        ├── __init__.py
        ├── main.py             # FastAPI + Inngest workflow orchestrator
        ├── custom_types.py     # Shared Pydantic data models
        ├── data_loader.py      # PDF parsing & Gemini embedding generator
        ├── vector_db.py        # Qdrant client wrapper
        └── qdrant_storage/     # Local vector store data
```

---

## 4. Current State & Implementation Gaps

- **Ready**:
  - `data_loader.py` can load, chunk, and embed documents.
  - `vector_db.py` can initialize collections, upsert vectors, and execute similarity queries.
  - `custom_types.py` specifies all data contracts.
  - `main.py` has the Inngest function structure and step layout.
- **In Progress**:
  - Implement the internal `_load` and `_upsert` logic in `main.py` using `data_loader` and `vector_db`.
  - Add query/search handler to feed retrieved context into Gemini for question answering (`RAGQueryResult`).
  - Add API trigger endpoints or UI (Streamlit).
