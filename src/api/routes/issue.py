from fastapi import APIRouter, File, UploadFile
from api.schemas import ScoreBreakdown
router = APIRouter()



@router.post("", response_model=ScoreBreakdown, summary="Compliance Score")
async def analyze(file:UploadFile = File(...)):


    #TODO: finish once credentials + sybol are ready
    return {"status":"not_implemented"} #FIX THIS