from fastapi import APIRouter, Depends
from pydantic import BaseModel

from rag.models import ComplianceResult
from rag.query import query_regulations
from api.dependencies import get_index

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    regulation_type: str | None = None


@router.post("", response_model=ComplianceResult)
def query(req: QueryRequest, index=Depends(get_index)):
    return query_regulations(req.query, index, req.regulation_type)
