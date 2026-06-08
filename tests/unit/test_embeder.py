from rag.embeder import get_embedding_model


def test_get_embedding_model(mock_embed_model):
    model = get_embedding_model()
    assert model is mock_embed_model
