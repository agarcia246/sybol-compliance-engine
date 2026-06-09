from functools import lru_cache

from fastapi import HTTPException, Request
from llama_index.core import VectorStoreIndex
import os
from dataclasses import dataclass, field
from qdrant_client import QdrantClient


@dataclass
class Settings:
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "dev"))
    qdrant_url: str = field(default_factory=lambda: os.getenv("QDRANT_URL", "http://localhost:6333"))
    qdrant_api_key: str | None = field(default_factory=lambda: os.getenv("QDRANT_API_KEY"))
    qdrant_collection: str = field(default_factory=lambda: os.getenv("QDRANT_COLLECTION", "regulations"))
    qdrant_audit_collection: str = field(default_factory=lambda: os.getenv("QDRANT_AUDIT_COLLECTION", "media_audit"))
    sybol_api_key: str | None = field(default_factory=lambda: os.getenv("SYBOL_API_KEY"))
    sybol_issuer_did: str | None = field(default_factory=lambda: os.getenv("SYBOL_ISSUER_DID"))


def get_settings() -> Settings:
    return Settings()


def get_qdrant_client(settings: Settings | None = None) -> QdrantClient:
    settings = settings or get_settings()
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)


def get_index(request: Request) -> VectorStoreIndex:
    index = getattr(request.app.state, "index", None)
    if index is None:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline not available. Ensure Qdrant is running and the index has been initialized.",
        )
    return index
