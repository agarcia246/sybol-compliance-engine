import scoring.visual as visual_module
from scoring.preprocess import preprocess
from scoring.visual import score_visual


def test_score_visual_bounded(sample_png_bytes):
    preprocessed = preprocess(sample_png_bytes, content_type="image/png")
    score = score_visual(preprocessed)
    assert 0.0 <= score <= 1.0


def test_visual_module_does_not_import_mediapipe():
    assert "mediapipe" not in visual_module.__dict__
