import json

import pytest

from src.credentials.vc_builder import VC_CONTEXT, build_vc_payload
from src.rag.models import ComplianceResult, RegulationRef
from src.scoring.models import ComplianceStatus, ScoringResult, SignalBreakdown


@pytest.fixture
def scoring_result():
    return ScoringResult(
        authenticity_score=0.85,
        score_breakdown=SignalBreakdown(m=0.9, a=0.8, v=0.85, p=0.85),
        compliance_status=ComplianceStatus.COMPLIANT,
        media_hash="abc123deadbeef",
        model_version="v1.0",
    )


@pytest.fixture
def compliance_result():
    return ComplianceResult(
        summary="No violations found.",
        regulationRefs=[
            RegulationRef(
                regulation="GDPR",
                article="5",
                sourceUrl="https://eur-lex.europa.eu/gdpr",
                excerpt="Article 5 requires lawful processing.",
            )
        ],
    )


def test_all_required_fields_present(scoring_result, compliance_result):
    payload = build_vc_payload(scoring_result, compliance_result)

    assert payload["@context"] == [VC_CONTEXT]
    assert payload["id"].startswith("urn:uuid:")
    assert "VerifiableCredential" in payload["type"]
    assert "MediaComplianceCredential" in payload["type"]
    assert payload["issuanceDate"]
    assert "issuer" not in payload
    assert "validFrom" not in payload
    assert "credentialSchema" not in payload
    assert "credentialStatus" not in payload

    subject = payload["credentialSubject"]
    assert subject["mediaHash"] == "abc123deadbeef"
    assert subject["authenticityScore"] == 0.85
    assert subject["scoreBreakdown"] == {"m": 0.9, "a": 0.8, "v": 0.85, "p": 0.85}
    assert subject["complianceStatus"] == "compliant"
    assert subject["modelVersion"] == "v1.0"
    assert subject["analysisTimestamp"]


def test_expiration_date_when_passed(scoring_result, compliance_result):
    expiry = "2027-06-14T12:00:00Z"
    payload = build_vc_payload(
        scoring_result, compliance_result, expiration_date=expiry
    )
    assert payload["expirationDate"] == expiry


def test_evidence_url_populated_when_passed(scoring_result, compliance_result):
    url = "http://localhost:6333/collections/media_audit/points/some-uuid"
    payload = build_vc_payload(scoring_result, compliance_result, evidence_url=url)
    assert payload["credentialSubject"]["evidenceUrl"] == url


def test_evidence_url_none_when_not_passed(scoring_result, compliance_result):
    payload = build_vc_payload(scoring_result, compliance_result)
    assert payload["credentialSubject"]["evidenceUrl"] is None


def test_regulation_refs_use_url_key(scoring_result, compliance_result):
    payload = build_vc_payload(scoring_result, compliance_result)
    refs = payload["credentialSubject"]["regulationRefs"]
    assert len(refs) == 1
    ref = refs[0]
    assert ref["regulation"] == "GDPR"
    assert ref["article"] == "5"
    assert ref["url"] == "https://eur-lex.europa.eu/gdpr"
    assert "sourceUrl" not in ref
    assert "excerpt" not in ref


def test_credential_id_reused_when_provided(scoring_result, compliance_result):
    cid = "urn:uuid:test-fixed-id"
    payload = build_vc_payload(scoring_result, compliance_result, credential_id=cid)
    assert payload["id"] == cid


def test_payload_is_json_serializable(scoring_result, compliance_result):
    payload = build_vc_payload(
        scoring_result,
        compliance_result,
        evidence_url="http://localhost:6333/collections/media_audit/points/x",
    )
    serialized = json.dumps(payload)
    assert "VerifiableCredential" in serialized


def test_empty_regulation_refs(scoring_result):
    rag = ComplianceResult(summary="No refs.", regulationRefs=[])
    payload = build_vc_payload(scoring_result, rag)
    assert payload["credentialSubject"]["regulationRefs"] == []
