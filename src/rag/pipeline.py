from llama_index.core import VectorStoreIndex

from src.rag.embeder import get_embedding_model
from src.rag.indexer import (
    build_index as indexer_build_index,
)
from src.rag.indexer import (
    load_documents,
)
from src.rag.indexer import (
    load_index as indexer_load_index,
)
from src.rag.ingest import chunk_documents


def build_index(documents: list | None = None) -> tuple[VectorStoreIndex, object]:
    docs = documents if documents is not None else load_documents()
    embed_model = get_embedding_model()
    return indexer_build_index(docs, embed_model)


def load_index() -> tuple[VectorStoreIndex, object]:
    embed_model = get_embedding_model()
    return indexer_load_index(embed_model)


def load_pipeline():
    index, client = load_index()
    embed_model = get_embedding_model()
    return index, embed_model, client


def ingest_and_index():
    documents = load_documents()
    if not documents:
        raise FileNotFoundError("No regulation PDFs found")

    nodes = chunk_documents(documents)
    index, client = build_index(nodes)
    embed_model = get_embedding_model()
    return index, embed_model, client


def build_pipeline():
    return ingest_and_index()
