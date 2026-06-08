from .constants import (
    PLATT_ENABLED,
    THRESHOLD_COMPLIANT,
    THRESHOLD_NON_COMPLIANT,
    WA,
    WM,
    WP,
    WV,
)
from .detector import get_deepfake_model
from .models import ComplianceStatus, ScoringResult, SignalBreakdown


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def calibrate(raw_score: float) -> float:
    if not PLATT_ENABLED:
        return raw_score
    # Future: load Platt parameters from src/scoring/data/platt_params.json
    return raw_score


def compute_authenticity_score(breakdown: SignalBreakdown) -> float:
    raw = (
        WM * breakdown.m
        + WA * breakdown.a
        + WV * breakdown.v
        + WP * breakdown.p
    )
    return _clamp(calibrate(raw))


def map_compliance_status(score: float) -> ComplianceStatus:
    if score < THRESHOLD_NON_COMPLIANT:
        return ComplianceStatus.NON_COMPLIANT
    if score < THRESHOLD_COMPLIANT:
        return ComplianceStatus.REVIEW
    return ComplianceStatus.COMPLIANT


def build_result(media_hash: str, breakdown: SignalBreakdown) -> ScoringResult:
    authenticity_score = compute_authenticity_score(breakdown)
    try:
        model_version = get_deepfake_model().version
    except Exception:
        model_version = "dima806/deepfake_vs_real_image_detection@unloaded"

    return ScoringResult(
        authenticity_score=authenticity_score,
        score_breakdown=breakdown,
        compliance_status=map_compliance_status(authenticity_score),
        media_hash=media_hash,
        model_version=model_version,
    )
