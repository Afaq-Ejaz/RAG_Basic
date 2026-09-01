import logging
from fastapi import FastAPI   
import inngest 
from inngest.experimental import ai
import inngest.fast_api
import uuid
import os
import datetime
from dotenv import load_dotenv

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
    return {"hello":"world"}


app = FastAPI()

inngest.fast_api.serve(app, inngest_client , [rag_agent_pdf])