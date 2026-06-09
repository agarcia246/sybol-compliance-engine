from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from src.api.dependencies import get_index


def test_get_index_returns_existing_index():
    sentinel = object()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(index=sentinel)))

    assert get_index(request) is sentinel


def test_get_index_raises_503_when_index_missing():
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(index=None)))

    with pytest.raises(HTTPException) as exc_info:
        get_index(request)

    assert exc_info.value.status_code == 503
    assert "RAG pipeline not available" in exc_info.value.detail