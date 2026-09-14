import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
import uuid
import os
import datetime
from dotenv import load_dotenv
from learn.data_loader import load_and_chunk_pdf, embedd_text
from learn.vector_db import QdrantStorage
from learn.custom_types import RAGChunkAndSrc,RAGQueryResult,RAGSearchResult,RAGUpsertResult
from google import genai 
from inngest.experimental import ai

load_dotenv()

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger= logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()

)

@inngest_client.create_function(
    fn_id="RAG: Ingest app",
    trigger=inngest.TriggerEvent(event= "rag/ingest_pdf"),

)
async def rag_agent_pdf(ctx: inngest.Context):
    def _load(ctx: inngest.Context)-> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id" , pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        vecs = embedd_text(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, name=f"{source_id}: {i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id , "text" : chunks[i] } for i in range(len(chunks))]
        QdrantStorage().upsert(ids,vecs,payloads)
        return RAGUpsertResult(ingested=len(chunks))

    chunks_and_src = await ctx.step.run("load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc)
    ingested = await ctx.step.run("embed-and-upsert" , lambda: _upsert(chunks_and_src), output_type=RAGUpsertResult) 
    return ingested.model_dump()

@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger= inngest.TriggerEvent(event="rag/query_pdf_ai")
)

async def rag_query_pdf_ai(ctx: inngest.Context):
    def _search(question:str , top_k: int=5):
        query_vec = embedd_text([question])[0]
        store = QdrantStorage()
        found = store.search(query_vec,top_k)

        return RAGSearchResult(context=found["contexts"], source=found["sources"])

    question = ctx.event.data["question"]
    top_k = ctx.event.data.get("top_k",5)

    found = await ctx.step.run("embed-and-search" , lambda: _search(question,top_k) , output_type=RAGSearchResult)

    context_block = "\n\n".join(f"- {c}" for c in found.context)
    user_content = (
        "Use the following context to answer the question.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
        "Answer concisely using the context above."
    )
# from inngest.experimental import ai

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 

    async def call_gemini():
        response = await client.aio.models.generate_content(
            model="gemini-3.6-flash",

            contents=[
                {"role": "user", "parts": [{"text": user_content}]}
            ], 
            
            config={
                "max_output_tokens": 1024,
                "temperature": 0.2,
                
                # 2. Add your "system" role here!
                "system_instruction": "You answer questions using only the provided context."
            }
        )
        return response.text

    # Execute it safely through Inngest
    res = await ctx.step.run("llm-answer", call_gemini)

    # Return the final RAG response
    return {
        "answer": res.strip(), 
        "sources": found.source, 
        "num_contexts": len(found.context)
    }

app = FastAPI()

inngest.fast_api.serve(app, inngest_client , [rag_agent_pdf, rag_query_pdf_ai])