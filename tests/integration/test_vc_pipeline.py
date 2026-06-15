"""Integration tests: score -> RAG -> VC payload (SYB-52)."""

import json
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from credentials.vc_builder import build_vc_payload
from rag.query import query_regulations
from scoring.models import ComplianceStatus, ScoringResult, SignalBreakdown
from scoring.pipeline import score_image
from src.api.dependencies import (
    Settings,
    get_index,
    get_qdrant_client,
    get_settings,
    get_sybol_client,
)
from src.api.main import app
from src.credentials.sybol_client import SybolClient


@pytest.fixture
def mock_scoring_result():
    return ScoringResult(
        authenticity_score=0.85,
        score_breakdown=SignalBreakdown(m=0.9, a=0.8, v=0.85, p=0.85),
        compliance_status=ComplianceStatus.COMPLIANT,
        media_hash="deadbeef001122",
        model_version="v1.0",
    )


@pytest.fixture
def mock_index():
    return MagicMock()


@pytest.fixture
def mock_qdrant():
    client = MagicMock()
    client.get_collections.return_value.collections = []
    return client


@pytest.fixture
def mock_settings():
    return Settings(
        qdrant_url="http://localhost:6333",
        qdrant_audit_collection="media_audit",
    )


def test_score_rag_vc_payload_end_to_end(
    sample_jpeg_bytes,
    mock_deepfake_model,
    mock_mistral,
    mock_vector_index,
    env_vars,
    mocker,
):
    """Real score_image + query_regulations + build_vc_payload in-process."""
    mocker.patch("scoring.pipeline.rebuild_provenance_index", return_value={})

    scoring_result = score_image(sample_jpeg_bytes, content_type="image/jpeg")
    rag = query_regulations(
        "What EU regulations apply to this media?",
        mock_vector_index,
    )
    payload = build_vc_payload(
        scoring_result,
        rag,
        evidence_url="http://localhost:6333/collections/media_audit/points/test",
    )

    assert len(scoring_result.media_hash) == 64
    assert payload["credentialSubject"]["mediaHash"] == scoring_result.media_hash
    refs = payload["credentialSubject"]["regulationRefs"]
    assert len(refs) >= 1
    for ref in refs:
        assert "regulation" in ref
        assert "article" in ref
        assert "url" in ref
        assert ref["regulation"] != "Unknown"
        assert ref["article"] != "Unknown"
    json.dumps(payload)


def test_empty_regulation_refs_produce_valid_vc_payload(
    sample_jpeg_bytes, mock_deepfake_model, mock_mistral, env_vars, mocker
):
    mocker.patch("scoring.pipeline.rebuild_provenance_index", return_value={})

    index = MagicMock()
    index.as_retriever.return_value.retrieve.return_value = []

    scoring_result = score_image(sample_jpeg_bytes, content_type="image/jpeg")
    rag = query_regulations("test query", index)
    payload = build_vc_payload(scoring_result, rag)

    assert rag.regulation_refs == []
    assert payload["credentialSubject"]["regulationRefs"] == []


def test_issue_route_returns_503_when_rag_fails(
    mocker,
    sample_jpeg_bytes,
    mock_scoring_result,
    mock_index,
    mock_qdrant,
    mock_settings,
):
    mocker.patch("src.api.routes.issue.score_image", return_value=mock_scoring_result)
    mocker.patch(
        "src.api.routes.issue.query_regulations",
        side_effect=TimeoutError("Mistral request timed out"),
    )

    sybol = MagicMock(spec=SybolClient)
    sybol.is_configured = True

    app.dependency_overrides[get_index] = lambda: mock_index
    app.dependency_overrides[get_qdrant_client] = lambda: mock_qdrant
    app.dependency_overrides[get_settings] = lambda: mock_settings
    app.dependency_overrides[get_sybol_client] = lambda: sybol

    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/api/issue",
            files={"file": ("test.jpg", sample_jpeg_bytes, "image/jpeg")},
        )
        assert response.status_code == 503
        assert "rag pipeline failed" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()
