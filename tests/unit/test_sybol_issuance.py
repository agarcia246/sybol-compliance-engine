"""VC issuance via the Sybol mock — TC-006 signing + §3.6 thresholds (Saba, Step 4).

This connects the two halves of credential issuance:
  1. credentials.vc_builder.build_vc_payload  -> the *unsigned* VC 1.1 payload
  2. MockSybolClient.issue_credential          -> simulates Sybol signing it
     (adds issuer DID, proof, credentialStatus) and returns the signed credential.

The real Sybol businessLogic API is external and not callable from CI, so
MockSybolClient stands in for it. That lets us assert the parts the unsigned
builder can't cover on its own:
  * the signed credential carries issuer, proof, and a credentialStatus entry
  * the signed credential preserves the builder's base (@context, id, subject)
  * VC Issuance Success Rate >= 95%  (README_Saba / §3.6 threshold)
  * the error path (TC-004): a Sybol failure is surfaced cleanly and counted

MockSybolClient is salvaged from the Phase 1 foundation (it is the only Sybol
test double in the project) and is stdlib-only, so it pulls in no heavy deps.
"""

import pytest

from credentials.vc_builder import build_vc_payload
from rag.models import ComplianceResult, RegulationRef
from scoring.models import ComplianceStatus, ScoringResult, SignalBreakdown
from tests.mocks.sybol import MockSybolClient, SybolAPIError


@pytest.fixture
def sybol() -> MockSybolClient:
    return MockSybolClient()


def _result(status: ComplianceStatus = ComplianceStatus.COMPLIANT) -> ScoringResult:
    return ScoringResult(
        authenticity_score=0.86,
        score_breakdown=SignalBreakdown(m=0.9, a=0.8, v=0.85, p=0.9),
        compliance_status=status,
        media_hash="a" * 64,
        model_version="model@test",
    )


def _rag() -> ComplianceResult:
    return ComplianceResult(
        summary="Standard EU media-provenance duties apply.",
        regulation_refs=[
            RegulationRef(
                regulation="EU AI Act",
                article="Article 50",
                source_url="https://eur-lex.europa.eu/eli/reg/2024/1689",
                excerpt="Synthetic content must be marked as artificially generated.",
            )
        ],
    )


def _unsigned_payload(status: ComplianceStatus = ComplianceStatus.COMPLIANT) -> dict:
    return build_vc_payload(_result(status), _rag())


def test_builder_output_is_accepted_by_sybol(sybol):
    # The unsigned payload from the real builder must satisfy Sybol's validation.
    signed = sybol.issue_credential(_unsigned_payload())
    assert sybol.issue_count == 1
    assert sybol.success_rate == 1.0
    assert signed["credentialSubject"]["mediaHash"] == "a" * 64


def test_signed_credential_has_issuer_proof_and_status(sybol):
    signed = sybol.issue_credential(_unsigned_payload())
    assert signed["issuer"] == sybol.issuer_did
    assert signed["proof"]["type"] == "DataIntegrityProof"
    assert signed["proof"]["proofValue"].startswith("z")
    assert signed["credentialStatus"]["statusPurpose"] == "revocation"


def test_signing_preserves_builder_base(sybol):
    # Signing must layer on top of the unsigned payload, not discard it: the
    # builder's @context, id, type and credentialSubject survive into the
    # signed credential unchanged.
    unsigned = _unsigned_payload()
    signed = sybol.issue_credential(unsigned)
    assert signed["@context"] == unsigned["@context"]
    assert signed["id"] == unsigned["id"]
    assert signed["type"] == unsigned["type"]
    assert signed["credentialSubject"] == unsigned["credentialSubject"]


def test_issuance_success_rate_meets_threshold(sybol):
    # §3.6: VC Issuance Success Rate >= 95%. Issue 20, force one failure -> 95%.
    sybol.fail_next()
    for _ in range(20):
        try:
            sybol.issue_credential(_unsigned_payload())
        except SybolAPIError:
            pass
    assert sybol.issue_count == 20
    assert sybol.success_rate >= 0.95


def test_issuance_failure_is_surfaced_cleanly(sybol):
    # TC-004 error path: a Sybol outage raises a typed error, not a crash, and is
    # still recorded as an attempt for the success-rate maths.
    sybol.fail_next(SybolAPIError("Sybol service unavailable", 503))
    with pytest.raises(SybolAPIError) as exc:
        sybol.issue_credential(_unsigned_payload())
    assert exc.value.status_code == 503
    assert sybol.issue_count == 1
    assert sybol.success_rate == 0.0


def test_rejects_payload_missing_required_subject_fields(sybol):
    # Defensive: a malformed payload (not from our builder) is rejected with 400.
    with pytest.raises(SybolAPIError) as exc:
        sybol.issue_credential({"credentialSubject": {"mediaHash": "x"}})
    assert exc.value.status_code == 400


def test_httpx_style_post_surface(sybol):
    # The mock also exposes POST /credentials/issue for endpoint-level tests.
    resp = sybol.post("/credentials/issue", json=_unsigned_payload())
    assert resp.status_code == 200
    assert resp.json()["issuer"] == sybol.issuer_did
