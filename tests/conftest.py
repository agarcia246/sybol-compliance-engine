from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("QDRANT_API_KEY", "test-key")
    monkeypatch.setenv("MISTRAL_API_KEY", "test-mistral-key")


@pytest.fixture
def mock_qdrant_client(mocker):
    client = MagicMock()
    client.get_collections.return_value.collections = []
    mocker.patch("rag.indexer.QdrantClient", return_value=client)
    mocker.patch("rag.indexer.QdrantVectorStore")
    return client


@pytest.fixture
def mock_embed_model(mocker):
    model = MagicMock()
    mocker.patch("rag.embeder.HuggingFaceEmbedding", return_value=model)
    mocker.patch("rag.pipeline.get_embedding_model", return_value=model)
    return model


@pytest.fixture
def mock_mistral(mocker):
    llm = MagicMock()
    llm.complete.return_value = "Synthesized compliance summary."
    mocker.patch("rag.query.MistralAI", return_value=llm)
    return llm


@pytest.fixture
def mock_vector_index(mocker):
    index = MagicMock()
    node = MagicMock()
    node.node.metadata = {
        "regulation_name": "GDPR",
        "article_number": "5",
        "source_path": "/research/regulations/gdpr.pdf",
    }
    node.node.get_content.return_value = "Article 5 requires lawful processing."
    index.as_retriever.return_value.retrieve.return_value = [node]
    return index


@pytest.fixture
def sample_document_nodes():
    from llama_index.core.schema import Document, TextNode

    doc = Document(
        text="Article 5 of GDPR requires lawful processing. Section 2 covers consent.",
        metadata={"regulation_name": "GDPR", "regulation_type": "gdpr"},
    )
    splitter_nodes = [
        TextNode(
            text=doc.text,
            metadata=dict(doc.metadata),
        )
    ]
    return splitter_nodes
