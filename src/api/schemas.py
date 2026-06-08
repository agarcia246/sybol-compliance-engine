from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    metadata: float = Field(..., alias="m")
    artifact: float = Field(..., alias="a")
    visual: float = Field(..., alias="v")
    provenance: float = Field(..., alias="p")
class AnalyzeResponse(BaseModel):
    authenticity_score: float = Field(..., ge=0.0, le=1.0)
    score_breakdown: list[float]
    compliance_status: str  # compliant | non-compliant | review
    media_hash: str