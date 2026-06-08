from llama_index.core import Document
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.api.dependencies import get_settings


def build_vector_store() -> QdrantVectorStore:
    settings = get_settings()
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )
    return QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
    )


def load_documents() -> list[Document]:
    # Replace with your PDF ingestion once you hook regulation parsing in
    return [
        Document(
            text="Temporary sample regulation text.",
            metadata={"source": "placeholder"},
        )
    ]