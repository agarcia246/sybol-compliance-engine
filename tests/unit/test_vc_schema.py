"""TC-006 — unsigned VC payload validates against its data model (Saba, Step 4).

Acceptance target (README_Saba): "VC Schema Validation Pass Rate: 100%".

These tests validate the *unsigned* payload produced by
credentials.vc_builder.build_vc_payload against a JSON Schema that encodes its
real shape. The builder targets the **W3C VC Data Model 1.1** (it emits
`@context: [https://www.w3.org/2018/credentials/v1]` and `issuanceDate`), not
2.0 — see test_vc_data_model_version below, which documents that gap explicitly.

What the builder intentionally does NOT include, and is therefore out of scope
here (validated in test_sybol_issuance.py instead):
  * `issuer` — resolved server-side from the authenticated tenant, not in the body
  * `credentialStatus` and `proof` — attached later by Sybol signing
"""

import json
from datetime import datetime
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from credentials.vc_builder import build_vc_payload
from rag.models import ComplianceResult, RegulationRef
from scoring.models import ComplianceStatus, ScoringResult, SignalBreakdown

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "vc_1_1_schema.json"


@pytest.fixture(scope="module")
def vc_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.fixture
def scoring_result() -> ScoringResult:
    return ScoringResult(
        authenticity_score=0.86,
        score_breakdown=SignalBreakdown(m=0.9, a=0.8, v=0.85, p=0.9),
        compliance_status=ComplianceStatus.COMPLIANT,
        media_hash="a" * 64,
        model_version="dima806/deepfake_vs_real_image_detection@test",
    )


@pytest.fixture
def compliance_result() -> ComplianceResult:
    return ComplianceResult(
        summary="Image is authentic; standard EU media-provenance duties apply.",
        regulation_refs=[
            RegulationRef(
                regulation="EU AI Act",
                article="Article 50",
                source_url="https://eur-lex.europa.eu/eli/reg/2024/1689",
                excerpt="Providers must mark synthetic content as artificially generated.",
            )
        ],
    )


def test_payload_matches_schema(vc_validator, scoring_result, compliance_result):
    payload = build_vc_payload(scoring_result, compliance_result)
    errors = sorted(vc_validator.iter_errors(payload), key=lambda e: list(e.path))
    assert not errors, "VC payload failed schema validation:\n" + "\n".join(
        f"  - {'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors
    )


def test_payload_declares_verifiable_credential_type(scoring_result, compliance_result):
    payload = build_vc_payload(scoring_result, compliance_result)
    assert "VerifiableCredential" in payload["type"]
    assert "MediaComplianceCredential" in payload["type"]


def test_vc_data_model_version(scoring_result, compliance_result):
    # The builder currently emits VC Data Model 1.1 (the /2018/credentials/v1
    # context + issuanceDate). README_Saba/TC-006 reference "VC 2.0"; this test
    # documents the actual version so a future migration to 2.0 (which would use
    # the /ns/credentials/v2 context + validFrom) updates this in one obvious place.
    payload = build_vc_payload(scoring_result, compliance_result)
    assert payload["@context"][0] == "https://www.w3.org/2018/credentials/v1"
    assert "issuanceDate" in payload
    assert "validFrom" not in payload  # would flip on a VC 2.0 migration


def test_issuance_date_is_iso8601_utc(scoring_result, compliance_result):
    payload = build_vc_payload(scoring_result, compliance_result)
    # Builder emits a trailing 'Z'; fromisoformat needs +00:00 before 3.11.
    parsed = datetime.fromisoformat(payload["issuanceDate"].replace("Z", "+00:00"))
    assert parsed.tzinfo is not None


def test_issuer_is_not_in_unsigned_body(scoring_result, compliance_result):
    # Per the builder docstring: issuer DID is resolved server-side from the
    # tenant context and must NOT appear in the unsigned request body.
    payload = build_vc_payload(scoring_result, compliance_result)
    assert "issuer" not in payload


def test_subject_score_fields_match_source_result(scoring_result, compliance_result):
    payload = build_vc_payload(scoring_result, compliance_result)
    subject = payload["credentialSubject"]
    assert subject["mediaHash"] == scoring_result.media_hash
    assert subject["authenticityScore"] == scoring_result.authenticity_score
    assert subject["complianceStatus"] == scoring_result.compliance_status.value
    assert subject["scoreBreakdown"] == {
        "m": scoring_result.score_breakdown.m,
        "a": scoring_result.score_breakdown.a,
        "v": scoring_result.score_breakdown.v,
        "p": scoring_result.score_breakdown.p,
    }


def test_regulation_refs_shape(scoring_result, compliance_result):
    # The builder maps each ref to {regulation, article, url}. Assert that exact
    # shape so a field rename in vc_builder is caught here.
    payload = build_vc_payload(scoring_result, compliance_result)
    ref = payload["credentialSubject"]["regulationRefs"][0]
    assert set(ref.keys()) == {"regulation", "article", "url"}
    assert ref["regulation"] == "EU AI Act"
    assert ref["url"] == "https://eur-lex.europa.eu/eli/reg/2024/1689"


@pytest.mark.parametrize(
    "status",
    [
        ComplianceStatus.COMPLIANT,
        ComplianceStatus.NON_COMPLIANT,
        ComplianceStatus.REVIEW,
    ],
)
def test_schema_holds_for_every_compliance_status(
    vc_validator, compliance_result, status
):
    result = ScoringResult(
        authenticity_score=0.5,
        score_breakdown=SignalBreakdown(m=0.5, a=0.5, v=0.5, p=0.5),
        compliance_status=status,
        media_hash="b" * 64,
        model_version="model@test",
    )
    payload = build_vc_payload(result, compliance_result)
    assert vc_validator.is_valid(payload)


def test_empty_regulation_refs_still_valid(vc_validator, scoring_result):
    # A compliant image may carry zero regulation refs — still a valid payload.
    empty_rag = ComplianceResult(
        summary="No specific obligations identified.", regulation_refs=[]
    )
    payload = build_vc_payload(scoring_result, empty_rag)
    assert vc_validator.is_valid(payload)


def test_optional_fields_are_threaded_through(
    vc_validator, scoring_result, compliance_result
):
    # credential_id / evidence_url / expiration_date are optional builder kwargs.
    payload = build_vc_payload(
        scoring_result,
        compliance_result,
        credential_id="urn:uuid:00000000-0000-4000-8000-000000000000",
        evidence_url="https://evidence.example/abc",
        expiration_date="2030-01-01T00:00:00Z",
    )
    assert payload["id"] == "urn:uuid:00000000-0000-4000-8000-000000000000"
    assert payload["credentialSubject"]["evidenceUrl"] == "https://evidence.example/abc"
    assert payload["expirationDate"] == "2030-01-01T00:00:00Z"
    assert vc_validator.is_valid(payload)
