# Current Architecture: Learn

This document describes the architecture that currently exists in the repository. It is intentionally limited to implemented code and configured project structure; the dependency list contains several capabilities that have not been connected yet.

## Project Metadata

- **Name:** `learn`
- **Version:** `0.1.0`
- **Python:** `>=3.14`
- **Author:** Afaq Ejaz
- **Build backend:** `uv_build`

## Repository Structure

```
Learn/
├── pyproject.toml
├── README.md                         # Currently empty
├── Project-data/
│   ├── ARCHITECTURE.md               # This document
│   └── PROJECT_STATUS_SUMMARY.txt
└── src/
    └── learn/
        ├── __init__.py               # Currently empty
        ├── main.py                   # FastAPI and Inngest setup
        ├── vector_db.py  
        └── qdrant_storage/           # Currently empty
```

## Runtime Architecture

The current application has one implemented runtime module, `src/learn/main.py`:

1. `python-dotenv` loads values from a local `.env` file into the process environment.
2. A logger named `uvicorn` is passed to the Inngest client.
3. An `inngest.Inngest` client is created with the application ID `rag_app`, production mode disabled, and `PydanticSerializer`.
4. The `rag_agent_pdf` async function is registered with Inngest.
5. The function listens for the event `rag/ingest_pdf` and currently returns the placeholder payload `{"hello": "world"}`.
6. A `FastAPI` application object is created.
7. `inngest.fast_api.serve` mounts the registered Inngest function onto the FastAPI application.

There are currently no application-defined REST routes, document-processing steps, model calls, vector operations, or Streamlit views. Requests to an undefined route, such as `/`, return FastAPI's normal `404 Not Found` response.

## Active Components

### FastAPI and Uvicorn

FastAPI provides the ASGI application object in `main.py`. Uvicorn is the server used to run that application during development.

### Inngest

Inngest is the only registered workflow integration. The single workflow is identified as `RAG: Ingest app` and is triggered by the `rag/ingest_pdf` event. Its handler is asynchronous and accepts an `inngest.Context`, but its business logic is still a placeholder.

### Environment Configuration

`load_dotenv()` is called during module import. No environment variables are read directly by the current code, and no configuration validation is implemented.

## Configured but Currently Unused

The following dependencies are declared in `pyproject.toml` but have no implementation in `src/learn/` yet:

- Google GenAI LLM and embedding integrations through LlamaIndex
- LlamaIndex indexing, core, and file-reader packages
- Qdrant client and the empty `qdrant_storage/` directory
- Streamlit
- Inngest experimental AI utilities

Their presence indicates the intended technology choices, but they are not part of the current execution path.

## Packaging and Execution

The project uses a `src` layout and `uv_build` as its build backend. `pyproject.toml` declares the console script `learn = "learn:main"`; however, `learn/__init__.py` is currently empty, so that script target is not implemented yet. The working development invocation used for the current ASGI application is equivalent to running Uvicorn with `main:app` from `src/learn` (or the corresponding package-qualified module from the project root).

## Current Boundaries and Gaps

- The API boundary is only the FastAPI application plus the routes mounted by `inngest.fast_api.serve`.
- The workflow boundary exists, but the PDF ingestion workflow performs no ingestion.
- There is no persistence layer or Qdrant connection.
- There is no LLM or embedding initialization.
- There is no user interface layer.
- There are no project tests, explicit error handling, or input validation in the current source tree.
