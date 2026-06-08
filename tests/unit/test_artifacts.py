from scoring.artifacts import _fft_score, _noise_residual_score, score_artifacts
from scoring.preprocess import preprocess


def test_artifact_subscores_bounded(sample_png_bytes, mock_deepfake_model):
    preprocessed = preprocess(sample_png_bytes, content_type="image/png")
    fft = _fft_score(preprocessed.model_image)
    noise = _noise_residual_score(preprocessed.model_image)
    assert 0.0 <= fft <= 1.0
    assert 0.0 <= noise <= 1.0


def test_score_artifacts_returns_bounded_value(sample_png_bytes, mock_deepfake_model):
    preprocessed = preprocess(sample_png_bytes, content_type="image/png")
    score = score_artifacts(preprocessed)
    assert 0.0 <= score <= 1.0
