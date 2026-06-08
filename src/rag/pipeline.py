from llama_index.core import VectorStoreIndex

from src.rag.indexer import build_vector_store, load_documents


def build_index() -> VectorStoreIndex:
    vector_store = build_vector_store()
    documents = load_documents()
    return VectorStoreIndex.from_documents(documents, vector_store=vector_store)