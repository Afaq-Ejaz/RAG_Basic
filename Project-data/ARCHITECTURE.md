# Project Architecture: Learn

This project is a small RAG-style application architecture built around PDF ingestion, embedding generation, vector storage, and a lightweight API/workflow layer. The design is simple and modular: each piece does one job, and they connect through a clear data flow.

## High-Level Architecture

```text
PDF File
   ↓
data_loader.py
   ↓
Chunk text into smaller parts
   ↓
Google GenAI embeddings
   ↓
vector_db.py
   ↓
Qdrant vector database
   ↓
Similarity search / retrieval
   ↓
FastAPI + Inngest entry point
```

This means the application is intended to work like a basic document search system:
- load PDF content,
- split it into chunks,
- create vector embeddings,
- save and retrieve them from Qdrant,
- expose the workflow through FastAPI and Inngest.

## Core Design

### 1. Application Entry Layer
The app starts from the web/workflow layer and acts as the orchestrator.

- `src/learn/main.py` — Starts the FastAPI app and registers the Inngest function responsible for the PDF workflow.
- `pyproject.toml` — Declares project metadata, dependencies, and the app script entry.

### 2. Document Processing Layer
This layer takes raw PDF files and prepares them for search.

- `src/learn/data_loader.py` — Loads a PDF, splits text into chunks, and creates embeddings using Google GenAI.

Flow:
1. PDF is read using `PDFReader`
2. Text is chopped into chunks using `SentenceSplitter`
3. Each chunk is converted into a vector using `genai.Client().models.embed_content`
4. The vector output is ready for storage and similarity search

### 3. Vector Storage Layer
This layer stores vectors and handles retrieval.

- `src/learn/vector_db.py` — Wraps Qdrant operations for collection creation, upserting vectors, and querying nearest matches.
- `src/learn/qdrant_storage/` — Local directory used for Qdrant metadata/state.

Flow:
1. A collection is created if it does not exist
2. Vectors are stored with their payload text and source metadata
3. A search request sends a query vector to Qdrant
4. Matching document chunks are returned as context for retrieval

### 4. Runtime Services
These are the external service boundaries shared by the app.

- Google GenAI — Acts as the embedding provider.
- Qdrant — Stores and searches vectors.
- FastAPI — Hosts the web app interface / HTTP boundary.
- Inngest — Handles workflow events and async function triggers.

## Repository Structure

```text
Learn/
├── pyproject.toml                              # Project config, dependencies, and packaging setup
├── README.md                                   # Project readme placeholder
├── Project-data/
│   ├── ARCHITECTURE.md                         # Architecture overview for the project
│   └── PROJECT_STATUS_SUMMARY.txt              # Simple project status summary
├── src/
│   └── learn/
│       ├── __init__.py                         # Package initialization file
│       ├── main.py                             # FastAPI + Inngest application entry point
│       ├── data_loader.py                      # PDF loading, chunking, and embedding generation
│       ├── vector_db.py                        # Qdrant storage and similarity search wrapper
│       └── qdrant_storage/                    # Local storage directory for Qdrant state/collections
```

## Architectural Responsibility Split

- `main.py` handles app startup and workflow trigger setup.
- `data_loader.py` handles document ingestion and embedding preparation.
- `vector_db.py` handles persistence and retrieval.
- `qdrant_storage/` stores vector database state.
- `pyproject.toml` defines the software stack and package setup.

## Current Reality

The architecture is intentionally simple and still in progress:

- FastAPI and Inngest are connected.
- PDF reading and text chunking are implemented.
- Embedding generation is implemented.
- Qdrant storage and search are implemented.
- The workflow is still a foundation, not a full production pipeline yet.

This means the project already contains the basic building blocks of a document RAG system, but the end-to-end orchestration is not fully connected yet.
