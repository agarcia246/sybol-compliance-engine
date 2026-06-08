from fastapi import APIRouter, Depends
from llama_index.core import VectorStoreIndex

from src.api.dependencies import get_index
from src.api.schemas import QueryResponse

router = APIRouter(tags=["rag"])


@router.post("/query", response_model=QueryResponse)
def query(payload: dict, index: VectorStoreIndex = Depends(get_index)) -> QueryResponse:
    query_engine = index.as_query_engine(similarity_top_k=5)
    result = query_engine.query(payload["question"])

    return QueryResponse(
        answer=str(result),
        regulation_refs=[],
    )