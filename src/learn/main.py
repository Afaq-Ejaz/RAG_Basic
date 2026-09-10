import logging
from fastapi import FastAPI   
import inngest 
from inngest.experimental import ai
import inngest.fast_api
import uuid
import os
import datetime
from dotenv import load_dotenv
from .data_loader import load_and_chunk_pdf , embedd_text
from .vector_db import QdrantStorage 
from .custom_types import RAGChunkAndSrc,RAGQueryResult,RAGSearchResult,RAGUpsertResult

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
        pass

    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        pass

    chunks_and_src = await ctx.step.run("load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc)
    ingested = await ctx.step.run("embed-and-upsert" , lambda: _upsert(chunks_and_src), output_type=RAGUpsertResult) 
    return ingested.model_dump()

app = FastAPI()

inngest.fast_api.serve(app, inngest_client , [rag_agent_pdf])