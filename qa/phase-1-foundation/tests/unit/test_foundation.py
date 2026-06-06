"""Self-tests for the Phase 1 foundation.

These prove the framework + mocks + fixtures actually work, and they double as
worked examples for Saba and Youssef when they write the real test suite. They
also map onto the project's test categories (§3.7) so the patterns are visible:
schema validation, golden-dataset ranges, RAG retrieval, error handling.
"""

from __future__ import annotations

import json

import pytest

from tests.fixtures import data as sample
from tests.mocks import MockMistralClient, MockSybolClient, SybolAPIError

pytestmark = pytest.mark.unit


# --- Mistral Large mock ------------------------------------------------------


class TestMockMistral:
    def test_default_returns_structured_compliance_json(self, mock_llm: MockMistralClient):
        resp = mock_llm.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": "Is AI-generated media allowed under EU law?"}],
        )
        data = json.loads(resp.text)
        assert "regulationRefs" in data
        assert data["regulationRefs"][0]["regulation"] == "EU AI Act"
        assert mock_llm.call_count == 1

    def test_queue_is_consumed_fifo(self, mock_llm: MockMistralClient):
        mock_llm.queue_response("first").queue_response("second")
        r1 = mock_llm.chat.complete(model="m", messages=[{"role": "user", "content": "x"}])
        r2 = mock_llm.chat.complete(model="m", messages=[{"role": "user", "content": "x"}])
        assert (r1.text, r2.text) == ("first", "second")

    def test_substring_matcher(self, mock_llm: MockMistralClient):
        mock_llm.register("right to erasure", '{"hit": true}')
        resp = mock_llm.chat.complete(
            model="m",
            messages=[{"role": "user", "content": "Explain the right to erasure under GDPR"}],
        )
        assert json.loads(resp.text) == {"hit": True}

    def test_records_what_was_sent(self, mock_llm: MockMistralClient):
        mock_llm.chat.complete(
            model="mistral-large-latest", messages=[{"role": "user", "content": "hi"}], temperature=0.0
        )
        call = mock_llm.calls[-1]
        assert call.model == "mistral-large-latest"
        assert call.kwargs["temperature"] == 0.0

    def test_fail_next_raises_then_recovers(self, mock_llm: MockMistralClient):
        mock_llm.fail_next(RuntimeError("503"))
        with pytest.raises(RuntimeError):
            mock_llm.chat.complete(model="m", messages=[{"role": "user", "content": "x"}])
        # next call succeeds
        resp = mock_llm.chat.complete(model="m", messages=[{"role": "user", "content": "x"}])
        assert resp.text

    async def test_async_interface(self, mock_llm: MockMistralClient):
        resp = await mock_llm.chat.complete_async(model="m", messages=[{"role": "user", "content": "x"}])
        assert resp.text


# --- Qdrant mock -------------------------------------------------------------


@pytest.mark.rag
class TestMockQdrant:
    def test_seeded_index_has_all_chunks(self, seeded_qdrant):
        assert seeded_qdrant.count("regulations") == len(sample.SAMPLE_REGULATION_CHUNKS)

    def test_topk_search_ranks_by_similarity(self, seeded_qdrant):
        results = seeded_qdrant.search(
            "regulations",
            query_vector=sample.SAMPLE_QUERY_VECTOR_TRANSPARENCY,
            limit=5,
        )
        # AI Act Art. 50 (transparency) should rank first for this query.
        assert results[0].payload["article"] == "Article 50"
        assert results[0].score >= results[-1].score

    def test_metadata_filter_by_regulation(self, seeded_qdrant):
        results = seeded_qdrant.search(
            "regulations",
            query_vector=[0.0, 1.0, 0.0, 0.0],
            limit=5,
            query_filter={"regulation": "GDPR"},
        )
        assert results
        assert all(r.payload["regulation"] == "GDPR" for r in results)

    def test_audit_trail_roundtrip(self, mock_qdrant):
        mock_qdrant.create_collection("audit", vectors_config={"size": 4})
        mock_qdrant.upsert("audit", [{"id": "rec1", "vector": [0, 0, 0, 1], "payload": {"score": 0.86}}])
        rec = mock_qdrant.retrieve("audit", ids=["rec1"])[0]
        assert rec.payload["score"] == 0.86

    def test_dim_mismatch_is_caught(self, seeded_qdrant):
        with pytest.raises(ValueError):
            seeded_qdrant.search("regulations", query_vector=[1.0, 0.0], limit=1)


# --- Sybol VC issuance mock --------------------------------------------------


@pytest.mark.vc
class TestMockSybol:
    def test_issue_adds_issuer_proof_and_status(self, mock_sybol: MockSybolClient, unsigned_vc):
        signed = mock_sybol.issue_credential(unsigned_vc)
        assert signed["issuer"] == "did:web:sybol.id"
        assert signed["proof"]["type"] == "DataIntegrityProof"
        assert signed["credentialStatus"]["statusPurpose"] == "revocation"
        assert "validFrom" in signed and "issuanceDate" not in signed  # VC 2.0 uses validFrom

    def test_rejects_payload_missing_required_fields(self, mock_sybol: MockSybolClient):
        with pytest.raises(SybolAPIError) as exc:
            mock_sybol.issue_credential({"credentialSubject": {"mediaHash": "abc"}})
        assert exc.value.status_code == 400

    def test_failure_injection_tracks_success_rate(self, mock_sybol: MockSybolClient, unsigned_vc):
        mock_sybol.issue_credential(unsigned_vc)  # ok
        mock_sybol.fail_next()  # next fails
        with pytest.raises(SybolAPIError):
            mock_sybol.issue_credential(unsigned_vc)
        mock_sybol.issue_credential(unsigned_vc)  # ok
        assert mock_sybol.issue_count == 3
        assert mock_sybol.success_rate == pytest.approx(2 / 3)

    def test_httpx_style_post_surface(self, mock_sybol: MockSybolClient, unsigned_vc):
        resp = mock_sybol.post("/credentials/issue", json=unsigned_vc)
        assert resp.status_code == 200
        assert resp.json()["issuer"] == "did:web:sybol.id"


# --- Foundation guarantees ---------------------------------------------------


class TestFoundation:
    def test_seed_is_applied(self):
        import random

        # _reseed_per_test ran before this test; first draw is deterministic.
        assert random.random() == pytest.approx(0.6177528569514706, abs=1e-12)

    def test_unsigned_vc_fixture_is_fresh_each_test(self, unsigned_vc):
        unsigned_vc["credentialSubject"]["authenticityScore"] = 0.0  # mutate
        # If the fixture leaked state, a later test would see 0.0; covered by
        # the next test re-requesting it.
        assert unsigned_vc["credentialSubject"]["mediaHash"] == sample.SAMPLE_MEDIA_HASH

    def test_unsigned_vc_fixture_not_leaked(self, unsigned_vc):
        assert unsigned_vc["credentialSubject"]["authenticityScore"] == 0.86
