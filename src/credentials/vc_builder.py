import os
import uuid
from datetime import datetime, timezone


from src.scoring.models import ScoringResult
from src.rag.models import ComplianceResult

DEFAULT_ISSUER_DID = "did:web:sybol.ai"
DEFAULT_SCHEMA_DID = "https://sybol.ai/schemas/media-compliance-credential/v1"


def _issuer_did() -> str:
    return os.getenv("SYBOL_ISSUER_DID") or DEFAULT_ISSUER_DID



def build_vc_payload(result: ScoringResult, rag: ComplianceResult) -> dict:   

    credential_id = f"urn:uuid:{uuid.uuid4()}"
    valid_from = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


    return {
        "id": credential_id,
        "type": ["VerifiableCredential", "MediaComplianceCredential"],
        "issuer": _issuer_did(),
        "validFrom": valid_from,
        "credentialSchema": {
            "id":DEFAULT_SCHEMA_DID,
            "type": "JsonSchema",
        },
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
            "analysisTimestamp": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
            "regulationRefs": [r.model_dump(by_alias=True) for r in rag.regulation_refs],
        },

        # This is a stub and must be updated when SYB-51 is completed
        "credentialStatus": {
            "id": f"https://sybol.ai/status/{credential_id}#0",
            "type": "StatusList2021Entry",
            "statusPurpose": "revocation",
            "statusListIndex": "0",
            "statusListCredential": "https://sybol.ai/status/list/1"
        }
    }


