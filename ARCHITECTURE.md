# Project Architecture: Learn

## Project Overview

**Learn** is a Python project designed to build intelligent applications leveraging modern AI and data processing technologies. The project integrates FastAPI for web services, LLM capabilities via Google GenAI, and vector database management with Qdrant.

**Author:** Afaq Ejaz  
**Version:** 0.1.0  
**Python Version Requirement:** >=3.14

---

## Directory Structure

```
Learn/
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # Project documentation (empty)
├── ARCHITECTURE.md         # This file
└── src/
    └── learn/
        ├── __init__.py     # Package initialization
        └── main.py         # Application entry point
```

---

## Technology Stack

### Web Framework
- **FastAPI** (>=0.141.1) - Modern async web framework for building APIs

### AI/LLM Integration
- **Google GenAI** - LLM and embedding services
  - `llama-index-llms-google-genai` (>=0.10.0) - LLM provider
  - `llama-index-embeddings-google-genai` (>=0.5.1) - Embedding models

### Data & Vector Databases
- **Qdrant Client** (>=1.19.0) - Vector database client for semantic search
- **LlamaIndex** (>=0.14.24) - Data indexing and retrieval framework
  - `llama-index-core` - Core functionality
  - `llama-index-readers-file` (>=0.6.0) - File reading capabilities

### Workflow Orchestration
- **Inngest** (>=0.5.19) - Event-driven orchestration and workflow engine
  - Includes experimental AI features

### UI Framework
- **Streamlit** (>=1.62.0) - Web app framework for building data/ML interfaces

### Server & Utilities
- **Uvicorn** (>=0.52.4) - ASGI server for running FastAPI applications
- **python-dotenv** (>=1.2.3) - Environment variable management

---

## Core Components

### 1. **Entry Point** (`src/learn/main.py`)
Currently initializes:
- Logging configuration
- FastAPI application instance
- Inngest client for workflow orchestration
- Environment variable loading via dotenv

**Status:** Under development - imports structured but main application logic not yet implemented

### 2. **Package Structure** (`src/learn/`)
- **`__init__.py`** - Package initialization (currently empty)
- **`main.py`** - Core application logic and API setup

---

## Planned Architecture Components

Based on the dependencies, the project is expected to include:

1. **REST API Layer** - FastAPI endpoints
2. **LLM Integration** - Google GenAI for language model tasks
3. **Vector Search** - Qdrant-backed semantic search capabilities
4. **File Processing** - LlamaIndex file readers for document ingestion
5. **Workflow Engine** - Inngest for event-driven orchestration
6. **UI Application** - Streamlit dashboard (optional)

---

## Build & Deployment

- **Build System:** uv_build (>=0.12.0, <0.13.0)
- **Package Script:** `learn = "learn:main"` - CLI entry point

---

## Development Status

- ✅ Project structure established
- ✅ Dependencies configured
- ⏳ Core application logic (in development)
- ⏳ API endpoints
- ⏳ LLM integration
- ⏳ Vector database setup

---

## Next Steps

1. Implement core application logic in `main.py`
2. Define API routes and endpoints
3. Set up LLM and embedding model initialization
4. Configure Qdrant vector database connection
5. Implement document ingestion pipeline
6. Add Streamlit UI (if needed)
7. Configure workflow automation with Inngest
