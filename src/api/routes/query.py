from fastapi import APIRouter, Depends
from llama_index.core import VectorStoreIndex

from src.api.dependencies import get_index
from src.api.schemas import QueryResponse
from src.rag.query import query_regulations

router = APIRouter(tags=["rag"])


@router.post("/query", response_model=QueryResponse)
def query(payload: dict, index: VectorStoreIndex = Depends(get_index)) -> QueryResponse:
    result = query_regulations(payload["question"], index)
    return QueryResponse(
        answer=result.summary,
        regulation_refs=[
            {"regulation": r.regulation, "article": r.article, "url": r.source_url}
            for r in result.regulation_refs
        ],
    )
