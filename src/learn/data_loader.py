from google import genai
from google.genai.types import EmbedContentConfig
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 3072  # default output size for this model

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_chunk_pdf(path:str):
    docs = PDFReader().load_data(file=Path(path))
    texts = [d.text for d in docs if getattr(d,"text" , None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))

    return chunks

def embedd_text(text: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=EMBED_MODEL,
        contents=text, #type: ignore[arg-type]
        config=EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=EMBED_DIM,
        ),
    )
    if response.embeddings is None:
        raise ValueError("Gemini returned no embeddings")

    embeddings = []
    for item in response.embeddings:
        if item.values is None:
            raise ValueError("Gemini returned an empty embedding for one input")
        embeddings.append(item.values)
    return embeddings