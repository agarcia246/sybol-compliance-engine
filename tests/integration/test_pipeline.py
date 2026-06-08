from unittest.mock import MagicMock

import pytest

from rag.pipeline import build_pipeline, ingest_and_index, load_pipeline


def test_load_pipeline(mock_qdrant_client, mock_embed_model, mocker):
    mock_index = MagicMock()
    mocker.patch(
        "rag.pipeline.load_index", return_value=(mock_index, mock_qdrant_client)
    )

    index, embed_model, client = load_pipeline()

    assert index is mock_index
    assert embed_model is mock_embed_model
    assert client is mock_qdrant_client


def test_ingest_and_index(mock_qdrant_client, mock_embed_model, mocker):
    mock_doc = MagicMock()
    mock_node = MagicMock()
    mock_index = MagicMock()

    mocker.patch("rag.pipeline.load_documents", return_value=[mock_doc])
    mocker.patch("rag.pipeline.chunk_documents", return_value=[mock_node])
    mocker.patch(
        "rag.pipeline.build_index",
        return_value=(mock_index, mock_qdrant_client),
    )

    index, embed_model, client = ingest_and_index()

    assert index is mock_index
    assert embed_model is mock_embed_model
    assert client is mock_qdrant_client


def test_ingest_and_index_raises_when_no_documents(mock_embed_model, mocker):
    mocker.patch("rag.pipeline.load_documents", return_value=[])

    with pytest.raises(FileNotFoundError, match="No regulation PDFs found"):
        ingest_and_index()


def test_build_pipeline_delegates_to_ingest_and_index(mocker):
    expected = (MagicMock(), MagicMock(), MagicMock())
    mocker.patch("rag.pipeline.ingest_and_index", return_value=expected)

    result = build_pipeline()
    assert result == expected
