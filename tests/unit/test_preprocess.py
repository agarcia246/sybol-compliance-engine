import hashlib

import pytest

from scoring.preprocess import ScoringError, preprocess


def test_preprocess_png_produces_expected_fields(sample_png_bytes):
    result = preprocess(sample_png_bytes, content_type="image/png")

    assert result.media_hash == hashlib.sha256(sample_png_bytes).hexdigest()
    assert result.original_image.size == (64, 64)
    assert result.model_image.size == (224, 224)
    assert result.content_type == "image/png"


def test_preprocess_jpeg(sample_jpeg_bytes):
    result = preprocess(sample_jpeg_bytes, content_type="image/jpeg")
    assert result.model_image.mode == "RGB"


def test_preprocess_rejects_empty_file():
    with pytest.raises(ScoringError, match="Empty file") as exc:
        preprocess(b"")
    assert exc.value.code == "empty_file"


def test_preprocess_rejects_corrupt_file(corrupt_bytes):
    with pytest.raises(ScoringError, match="Unsupported or unrecognized") as exc:
        preprocess(corrupt_bytes)
    assert exc.value.code == "unsupported_format"


def test_preprocess_rejects_unsupported_mime(sample_png_bytes):
    with pytest.raises(ScoringError, match="Unsupported file type") as exc:
        preprocess(sample_png_bytes, content_type="image/gif")
    assert exc.value.code == "unsupported_format"


def test_hash_computed_before_resize(sample_png_bytes):
    original = preprocess(sample_png_bytes, content_type="image/png")
    expected_hash = hashlib.sha256(sample_png_bytes).hexdigest()
    assert original.media_hash == expected_hash