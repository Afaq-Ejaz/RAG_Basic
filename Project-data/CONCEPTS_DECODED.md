# The RAG Codebase Blueprint: Learn to Code, Not Just Copy

> **For the Developer Escaping Tutorial Hell**:  
> Watching a tutorial video and copying code line-by-line feels like learning, until the video ends and you stare at a blank screen wondering: *"What did I actually build? Why did they use that import? How do these files connect?"*
>
> This document is designed to give you **true technical intuition**. After reading this, you will understand the mechanics, the vocabulary, the file relationships, and how to write code like this independently.

---

## 1. The Core Mental Model: What is RAG?

Before touching any code, understand the real-world problem.

### The "Open-Book Exam" Analogy
* **Standard LLM (ChatGPT / Gemini without RAG)** = **A Closed-Book Exam.**  
  The AI relies only on what it memorized during its training cutoff. If you ask it: *"What is written in my private company PDF?"*, it either guesses (hallucinates) or says *"I don't know"*.
* **RAG (Retrieval-Augmented Generation)** = **An Open-Book Exam.**  
  When you ask a question, the system:
  1. Opens your textbook (retrieves relevant pages from your PDF).
  2. Hands those exact pages to Gemini along with your question.
  3. Says: *"Answer the question using ONLY these pages."*

### The Two Halves of Every RAG System

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. INGESTION PIPELINE (Offline / Preparation)               │
│ PDF -> Read Text -> Chop into Chunks -> Convert to Numbers  │
│ -> Store in Vector Database (Qdrant)                        │
└─────────────────────────────────────────────────────────────┘
                               ▲
                               │ Stores knowledge
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. RETRIEVAL & GENERATION PIPELINE (Online / When User Asks)│
│ User Question -> Convert to Numbers -> Search Vector DB     │
│ -> Retrieve Best Chunks -> Send to LLM -> Final Answer      │
└─────────────────────────────────────────────────────────────┘
```

Your codebase currently implements the **Ingestion Pipeline** and has the types ready for the **Retrieval Pipeline**.

---

## 2. The Codebase Anatomy: How the Files Talk to Each Other

Beginners often get confused because tutorials jump between files. Here is the dependency graph showing who imports whom and why:

```text
               ┌──────────────────────┐
               │   custom_types.py    │ ◄─── Defines the contracts (Pydantic models)
               └──────────┬───────────┘
                          │ (used by everyone for clean data shapes)
         ┌────────────────┼────────────────┐
         ▼                                 ▼
┌─────────────────┐               ┌─────────────────┐
│ data_loader.py  │               │  vector_db.py   │
│ - Reads PDF     │               │ - Talks to      │
│ - Chunks text   │               │   Qdrant DB     │
│ - Calls Gemini  │               │ - Upserts &     │
│   for vectors   │               │   searches      │
└────────┬────────┘               └────────┬────────┘
         │                                 │
         └────────────────┬────────────────┘
                          ▼
                  ┌───────────────┐
                  │    main.py    │ ◄─── The Conductor / Orchestrator
                  │ - FastAPI API │      Glues data_loader & vector_db together
                  │ - Inngest job │      inside safe, retryable steps
                  └───────────────┘
```

### The Rule of Separation of Concerns
Notice why this is split into 4 files instead of one giant 500-line script:
1. [custom_types.py](file:///f:/Learn/src/learn/custom_types.py) has **zero dependencies on AI or databases**. It only defines data blueprints.
2. [data_loader.py](file:///f:/Learn/src/learn/data_loader.py) only cares about **files, text, and embeddings**. It knows nothing about FastAPI or Inngest.
3. [vector_db.py](file:///f:/Learn/src/learn/vector_db.py) only cares about **storing and querying vectors**. It knows nothing about PDFs.
4. [main.py](file:///f:/Learn/src/learn/main.py) is the **manager**. It imports the tools from the other 3 files and directs traffic.

---

## 3. Demystifying the Imports & Dependencies

Why did the tutorial author choose these specific libraries in `pyproject.toml`?

| Library / Import | What it Actually Is | What Problem it Solves for You |
| :--- | :--- | :--- |
| `fastapi` | Web server framework | Allows your Python code to receive web requests (`GET`, `POST`) from a frontend or webhook. |
| `uvicorn` | ASGI web server runner | The engine that actually runs FastAPI on a port (e.g., `localhost:8000`). |
| `inngest` | Background workflow engine | Prevents crashes. If processing a 100-page PDF takes 2 minutes, Inngest runs it in the background with automatic retries and step checkpoints. |
| `llama_index.readers.file.PDFReader` | Document parser | Extracts raw text from messy PDF byte streams without you having to parse binary streams. |
| `llama_index.core.node_parser.SentenceSplitter` | Smart text splitter | Chops huge text into smaller bite-sized paragraphs without cutting words in half mid-sentence. |
| `google.genai` | Official Google AI SDK | Connects to Google's servers to create embeddings (`gemini-embedding-001`) and run Gemini models. |
| `qdrant-client` | Vector database client | A database specifically built for searching multi-dimensional vectors (arrays of floating-point numbers). |
| `pydantic` | Data validation library | Guarantees that data passed between functions has the exact expected fields and types. |
| `python-dotenv` (`load_dotenv`) | Environment variable loader | Reads your secret API keys from `.env` file into system memory so you don't commit secrets to Git. |

---

## 4. Deep Dive: File-by-File Line Breakdown

---

### File 1: [custom_types.py](file:///f:/Learn/src/learn/custom_types.py) — The Blueprints

#### Why do professional devs write this file first?
In amateur code, functions pass random dictionaries around: `{"data": [...]}`. If someone renames `"data"` to `"chunks"`, the whole app breaks silently with a `KeyError` 20 minutes into execution.  
`Pydantic` models act as **strict contracts**. If data doesn't match the blueprint, Python raises an immediate, helpful error.

```python
import pydantic 

class RAGChunkAndSrc(pydantic.BaseModel):
    chunks: list[str]            # The text fragments chopped from the PDF
    source_id: str | None = None # The filename or PDF title (optional)

class RAGUpsertResult(pydantic.BaseModel):
    ingested: int                # Count of how many vector chunks were saved

class RAGSearchResult(pydantic.BaseModel):
    context: list[str]           # Matching text chunks found in the database
    source: list[str]            # Filenames where those chunks came from

class RAGQueryResult(pydantic.BaseModel):
    answer: str                  # The final generated answer for the user
    sources: list[str]           # Citations ("found in Page 3 of report.pdf")
    num_context: int             # How many text fragments were used to form the answer
```

* **Mental Model**: Think of these like standardized shipping containers. No matter what truck or boat carries the data, the container shape is guaranteed.

---

### File 2: [data_loader.py](file:///f:/Learn/src/learn/data_loader.py) — The Raw Material Factory

This file does two distinct jobs:
1. **Load and Chunk** the PDF.
2. **Convert Chunked Text into Embeddings** (numbers).

#### Concept A: Why do we "Chunk" text?
LLMs and embedding models have input limits. If you feed an entire 200-page book into an embedding model:
- The meaning gets watered down into a bland generic summary.
- You waste money and memory.
- When searching later, the database can't point you to the exact paragraph you need.

#### Concept B: What is `chunk_size=1000` and `chunk_overlap=200`?
```python
splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)
```
* `chunk_size=1000`: Target approximately 1,000 characters per text slice.
* `chunk_overlap=200`: Each chunk copies the last 200 characters of the previous chunk!
* **Why overlap?** Imagine a crucial sentence starts at character 990 and finishes at character 1020. If you slice cleanly at 1000, you slice the sentence in half and destroy its meaning. Overlap preserves context across boundaries.

#### Concept C: What on Earth is an "Embedding"?
Look at line 25:
```python
def embedd_text(text: list[str]) -> list[list[float]]:
```
* **The Non-Tech Picture**: Imagine a 3D globe. "King" sits at latitude 10, longitude 20, altitude 5. "Queen" sits right next to it at 10, 20, 6. "Bicycle" sits on the other side of the planet.
* **The Tech Reality**: Google's `gemini-embedding-001` model takes a sentence and turns it into a list of **3,072 decimal numbers** (a 3,072-dimensional vector coordinate). 
* Sentences with similar meanings have coordinates close together in 3,072-dimensional space, even if they use completely different words!
  * *"The puppy was playful"* and *"The young dog had lots of energy"* produce nearly identical coordinates!

#### Line-by-Line Code Breakdown:
```python
# 1. Initialize the Google GenAI client
client = genai.Client() # Reads GEMINI_API_KEY from your environment automatically
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 3072  # Dimension size of the coordinate list

# 2. Extract and slice
def load_and_chunk_pdf(path: str):
    docs = PDFReader().load_data(file=Path(path)) # Reads raw PDF pages
    texts = [d.text for d in docs if getattr(d, "text", None)] # Filters empty pages
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t)) # Chops text with overlap
    return chunks

# 3. Request embeddings from Google
def embedd_text(text: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=text,
        config=EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT", # Tells Gemini: "These are documents being saved for search"
            output_dimensionality=EMBED_DIM,
        ),
    )
    # Extract values: returns a list of 3,072-number floats for each chunk
    embeddings = []
    for item in response.embeddings:
        embeddings.append(item.values)
    return embeddings
```

---

### File 3: [vector_db.py](file:///f:/Learn/src/learn/vector_db.py) — The Semantic Memory

#### Why can't we just use SQL (`SELECT * FROM table WHERE text LIKE '%keyword%'`)?
* Keyword search fails if the user searches for *"canine"* when the document says *"dog"*.
* Vector databases search by **meaning (geometry)**, not exact letters.

#### What is Qdrant?
Qdrant is an open-source vector search engine. It stores points. Each point contains:
1. `id`: Unique identifier (UUID or integer).
2. `vector`: The 3,072 floats created by Gemini.
3. `payload`: The original text snippet + source metadata (filename, page).

#### What is `Distance.COSINE`?
Cosine distance measures the **angle** between two vectors in multi-dimensional space:
- Angle = 0° (Cosine = 1.0) -> Identical meaning.
- Angle = 90° (Cosine = 0.0) -> Completely unrelated topics.

#### Line-by-Line Code Breakdown:
```python
class QdrantStorage:
    def __init__(self, url: str = "http://localhost:6333", collection="docs", dim=3072):
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection
        # Check if the folder/collection exists; if not, create it with 3072-dim Cosine space
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )

    def upsert(self, ids, vectors, payloads):
        # Package raw lists into Qdrant PointStructs
        points = [
            PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) 
            for i in range(len(ids))
        ]
        # "Upsert" = Update if ID exists, Insert if it is new
        self.client.upsert(self.collection, points=points)

    def search(self, query_vector, top_k: int = 5):
        # Finds the 5 closest vectors to the user query's coordinate
        results = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k
        ).points

        contexts = []
        sources = set()

        for r in results:
            payload = getattr(r, "payload", None) or {}
            text = payload.get("text", "")
            source = payload.get("source", "")
            if text:
                contexts.append(text)
                sources.add(source)

        return {"contexts": contexts, "sources": sources}
```

---

### File 4: [main.py](file:///f:/Learn/src/learn/main.py) — The Orchestrator

This file brings all the individual pieces together into a production-grade workflow.

#### The Big Concepts in `main.py`:
1. **`app = FastAPI()`**: The web server interface.
2. **`inngest_client = inngest.Inngest(...)`**: Connects to the Inngest workflow engine.
3. **`@inngest_client.create_function`**: Registers an asynchronous background job that wakes up whenever event `"rag/ingest_pdf"` is fired.
4. **`ctx.step.run`**: Defines checkpoints:
   - Step 1: `"load-and-chunk"`
   - Step 2: `"embed-and-upsert"`

#### What the code in `main.py` is doing and what needs to be filled in:
Currently, the function in `main.py` looks like this:
```python
async def rag_agent_pdf(ctx: inngest.Context):
    def _load(ctx: inngest.Context) -> RAGChunkAndSrc:
        # TODO: Get PDF file path from event (ctx.event.data["pdf_path"])
        # Call load_and_chunk_pdf(pdf_path) from data_loader.py
        # Return RAGChunkAndSrc(chunks=chunks, source_id=pdf_path)
        pass

    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        # TODO: Call embedd_text(chunks_and_src.chunks) from data_loader.py
        # Generate IDs (using uuid) and payloads ({"text": chunk, "source": source_id})
        # Call QdrantStorage().upsert(ids, vectors, payloads)
        # Return RAGUpsertResult(ingested=len(vectors))
        pass

    # Step 1: Executes _load with automatic retry & checkpoint
    chunks_and_src = await ctx.step.run("load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc)
    
    # Step 2: Takes output of Step 1 and runs _upsert with automatic retry & checkpoint
    ingested = await ctx.step.run("embed-and-upsert", lambda: _upsert(chunks_and_src), output_type=RAGUpsertResult) 
    
    return ingested.model_dump()
```

* Notice how clean this is: `chunks_and_src` (from Step 1) feeds directly into `_upsert` (Step 2).
* If Step 2 fails, Step 1 never re-runs. That is the beauty of **Durable Execution**.

---

## 5. End-to-End Walkthrough: Follow a Single Sentence

Let's trace what happens to a single sentence from start to finish:

1. **You have a PDF file**: `invoice.pdf` contains: *"Total amount due is $500 payable by October 1st."*
2. **Trigger**: An event is emitted to Inngest:
   `{"name": "rag/ingest_pdf", "data": {"pdf_path": "./invoice.pdf"}}`
3. **Step 1 (`_load`)**:
   - `PDFReader` reads `invoice.pdf`.
   - `SentenceSplitter` outputs a list of strings: `["Total amount due is $500 payable by October 1st.", ...]`.
   - Packaged into `RAGChunkAndSrc(chunks=[...], source_id="invoice.pdf")`.
4. **Step 2 (`_upsert`)**:
   - Sent to Google GenAI -> returned as `[0.0123, -0.0452, ..., 0.0891]` (3,072 numbers).
   - Wrapped into a `PointStruct(id="uuid-1", vector=[...], payload={"text": "Total amount due is $500...", "source": "invoice.pdf"})`.
   - Saved into Qdrant vector database collection `"docs"`.
5. **Retrieval (Later, when asking questions)**:
   - User asks: *"How much do I owe and when is the deadline?"*
   - Query is embedded into 3,072 numbers.
   - Qdrant compares angles (`Distance.COSINE`) and finds `uuid-1` has a 94% similarity match!
   - Returns the payload text: *"Total amount due is $500 payable by October 1st."*
   - Sent to Gemini: *"Based on this text, how much do I owe?"* -> Gemini answers: *"You owe $500 by October 1st."*

---

## 6. The Independent Coder's Mental Toolkit

When building any backend or AI app on your own, **never write code top to bottom blindly**. Follow this 4-step framework:

### Step 1: Draw the Data on Paper (Types First)
Before writing logic, ask: *"What data goes into this system, and what shape does it take?"*
Define your Pydantic classes first. That sets the target.

### Step 2: Build Small, Independent "Pure" Helpers
Write functions that do one simple thing and test them in isolation:
- Does `load_and_chunk_pdf("test.pdf")` print a list of strings? Test it with a 1-line script.
- Does `embedd_text(["hello"])` return 3,072 numbers? Test it with a 1-line script.

### Step 3: Wrap External Services in Classes
Don't sprinkle database code all over your app. Put it in a wrapper class (like `QdrantStorage`). That way, if you ever switch from Qdrant to Pinecone or ChromaDB, you only modify **one file** (`vector_db.py`), not your entire codebase!

### Step 4: Wire with Orchestrators & APIs
Once your building blocks are tested and working, import them into `main.py` and hook them up to FastAPI routes or Inngest events.
