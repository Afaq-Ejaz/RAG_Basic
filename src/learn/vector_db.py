from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams , Distance  ,PointStruct

class QdrantStorage:
    def __init__(self , url:str = "http://localhost:6333" , collection="docs" , dim=3072):
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config= VectorParams(size=dim , distance= Distance.COSINE)
            )
        self.dim = dim

    