from scoring.models import ComplianceStatus
from scoring.pipeline import load_scoring_pipeline, score_image


def test_score_image_end_to_end(sample_jpeg_bytes, mock_deepfake_model, mocker):
    mocker.patch("scoring.pipeline.rebuild_provenance_index", return_value={})
    result = score_image(sample_jpeg_bytes, content_type="image/jpeg")

    assert 0.0 <= result.authenticity_score <= 1.0
    assert len(result.media_hash) == 64
    assert 0.0 <= result.score_breakdown.m <= 1.0
    assert 0.0 <= result.score_breakdown.a <= 1.0
    assert 0.0 <= result.score_breakdown.v <= 1.0
    assert 0.0 <= result.score_breakdown.p <= 1.0
    assert result.compliance_status in ComplianceStatus


def test_load_scoring_pipeline(mock_deepfake_model, mocker):
    mocker.patch("scoring.pipeline.rebuild_provenance_index", return_value={})
    load_scoring_pipeline()
