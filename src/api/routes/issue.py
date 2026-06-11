from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from llama_index.core import VectorStoreIndex

from src.api.dependencies import get_index
from src.api.schemas import IssueResponse
from src.credentials.vc_builder import build_vc_payload
from src.rag.query import query_regulations
from src.scoring.pipeline import score_image
from src.scoring.preprocess import ScoringError


router = APIRouter(tags=["credentials"])

SUPPORTED_TYPES = ("image/jpeg", "image/png", "image/webp")


@router.post(
    "/issue",
    response_model=IssueResponse,
    summary="Build unsigned VC payload",
    responses={
        400: {"description": "Unsupported or corrupted file"},
    },
)

async def issue(
    file:UploadFile = File(...),
    index: VectorStoreIndex = Depends(get_index),
):
    if file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(400, "Unsupported file type")
    
    content = await file.read()
    try:
        result = score_image(
            content,
            filename= file.filename,
            content_type=file.content_type,
        )
    except ScoringError as exec:
        raise HTTPException(400, detail=str(exec)) from exec

    rag_query = (
        f"What EU regulations apply to media with authenticity score "
        f"{result.authenticity_score:.2f} and compliance status "
        f"{result.compliance_status.value}?"
    )
    rag = query_regulations(rag_query, index)

    payload = build_vc_payload(result, rag)

    return IssueResponse(
        status="unsigned_vc_build",
        vc_id=payload["id"],
        detail="Payload ready for Sybol signing"
    )