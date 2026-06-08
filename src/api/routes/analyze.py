from fastapi import APIRouter, File, HTTPException, UploadFile

from api.schemas import AnalyzeResponse
from scoring.pipeline import score_image
from scoring.preprocess import ScoringError

router = APIRouter()


@router.post(
    "",
    response_model=AnalyzeResponse,
    summary="Score media authenticity",
    responses={
        400: {"description": "Unsupported file type or corrupted file"},
    },
)
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(400, "Unsupported file type")

    content = await file.read()
    try:
        result = score_image(
            content,
            filename=file.filename,
            content_type=file.content_type,
        )
    except ScoringError as exc:
        raise HTTPException(400, detail=str(exc)) from exc

    breakdown = result.score_breakdown
    return AnalyzeResponse(
        authenticity_score=result.authenticity_score,
        score_breakdown=[breakdown.m, breakdown.a, breakdown.v, breakdown.p],
        compliance_status=result.compliance_status.value,
        media_hash=result.media_hash,
    )
