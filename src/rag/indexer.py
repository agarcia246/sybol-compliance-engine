import os

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

COLLECTION_NAME = "regulations"


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        os.environ["QDRANT_URL"],
        api_key=os.environ.get("QDRANT_API_KEY"),
    )


def _delete_collection_if_exists(client: QdrantClient) -> None:
    collections = client.get_collections().collections
    if any(c.name == COLLECTION_NAME for c in collections):
        client.delete_collection(COLLECTION_NAME)


def load_index(embedding_model):
    client = get_qdrant_client()
    store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
    )
    index = VectorStoreIndex.from_vector_store(
        store,
        embed_model=embedding_model,
    )
    return index, client


def build_index(nodes, embedding_model, recreate_collection: bool = True):
    client = get_qdrant_client()

    if recreate_collection:
        _delete_collection_if_exists(client)

    store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
    )
    storage_context = StorageContext.from_defaults(vector_store=store)

    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
        embed_model=embedding_model,
    )
    return index, client
