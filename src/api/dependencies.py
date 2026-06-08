from fastapi import HTTPException, Request
from llama_index.core import VectorStoreIndex


def get_index(request: Request) -> VectorStoreIndex:
    index = getattr(request.app.state, "index", None)
    if index is None:
        raise HTTPException(
            503,
            "RAG pipeline not available. Set QDRANT_URL in src/.env and ensure Qdrant is running.",
        )
    return index