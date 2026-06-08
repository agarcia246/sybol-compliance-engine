from functools import lru_cache

from fastapi import HTTPException, Request

from llama_index.core import VectorStoreIndex
from pydantic_settings import BaseSettings, SettingsConfigDict
from qdrant_client import QdrantClient


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "regulations"
    qdrant_audit_collection: str = "media_audit"
    sybol_api_key: str | None = None
    sybol_issuer_did: str | None = None


@lru_cache
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