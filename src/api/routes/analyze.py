from fastapi import APIRouter, File, UploadFile, HTTPException
from api.schemas import AnalyzeResponse
router = APIRouter()



@router.post(
    "", 
    response_model=AnalyzeResponse, 
    summary="Score media authenticity",
    responses={
        400: {"description": "Unsupported file type or corrupted file"},
        501: {"description": "Scoring Pipeline not yet implemented"},
    },
)
async def analyze(file:UploadFile = File(...)):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(400, "Unsupported file type")


    #TODO: call scoring pipeline
    return {"status":"not_implemented"} #FIX THIS