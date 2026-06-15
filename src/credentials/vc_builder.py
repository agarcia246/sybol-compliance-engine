import uuid
from datetime import datetime, timezone

from src.rag.models import ComplianceResult
from src.scoring.models import ScoringResult

VC_CONTEXT = "https://www.w3.org/2018/credentials/v1"


def _iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_vc_payload(
    result: ScoringResult,
    rag: ComplianceResult,
    *,
    credential_id: str | None = None,
    evidence_url: str | None = None,
    expiration_date: str | None = None,
) -> dict:
    """
    Build an unsigned W3C VC Data Model 1.1 payload for Sybol businessLogic API.

    Issuer DID is resolved server-side from the authenticated tenant context;
    it is not included in the request body.
    """
    if credential_id is None:
        credential_id = f"urn:uuid:{uuid.uuid4()}"

    issuance_date = _iso_timestamp()

    payload: dict = {
        "@context": [VC_CONTEXT],
        "id": credential_id,
        "type": ["VerifiableCredential", "MediaComplianceCredential"],
        "issuanceDate": issuance_date,
        "credentialSubject": {
            "id": f"urn:media:{result.media_hash}",
            "mediaHash": result.media_hash,
            "authenticityScore": result.authenticity_score,
            "scoreBreakdown": {
                "m": result.score_breakdown.m,
                "a": result.score_breakdown.a,
                "v": result.score_breakdown.v,
                "p": result.score_breakdown.p,
            },
            "complianceStatus": result.compliance_status.value,
            "modelVersion": result.model_version,
            "analysisTimestamp": _iso_timestamp(),
            "regulationRefs": [
                {"regulation": r.regulation, "article": r.article, "url": r.source_url}
                for r in rag.regulation_refs
            ],
            "evidenceUrl": evidence_url,
        },
    }

    if expiration_date is not None:
        payload["expirationDate"] = expiration_date

    return payload
