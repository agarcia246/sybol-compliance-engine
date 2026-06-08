from unittest.mock import MagicMock

from rag.query import query_regulations


def test_query_regulations_returns_compliance_result(
    mock_mistral, mock_vector_index, env_vars
):
    result = query_regulations(
        query="What are GDPR data processing requirements?",
        index=mock_vector_index,
    )

    assert result.summary == "Synthesized compliance summary."
    assert len(result.regulation_refs) == 1
    assert result.regulation_refs[0].regulation == "GDPR"
    assert result.regulation_refs[0].article == "5"
    mock_mistral.complete.assert_called_once()


def test_query_regulations_with_regulation_type_filter(
    mock_mistral, mock_vector_index, env_vars
):
    result = query_regulations(
        query="AI transparency rules",
        index=mock_vector_index,
        regulation_type="eu_ai_act",
    )

    assert result.summary == "Synthesized compliance summary."
    mock_vector_index.as_retriever.assert_called_once()
    call_kwargs = mock_vector_index.as_retriever.call_args.kwargs
    assert call_kwargs["similarity_top_k"] == 5
    assert call_kwargs["filters"] is not None


def test_query_regulations_handles_missing_metadata(mock_mistral, env_vars, mocker):
    index = MagicMock()
    node = MagicMock()
    node.node.metadata = {}
    node.node.get_content.return_value = "Short excerpt."
    index.as_retriever.return_value.retrieve.return_value = [node]

    result = query_regulations(query="test query", index=index)

    assert result.regulation_refs[0].regulation == "Unknown"
    assert result.regulation_refs[0].article == "Unknown"
    assert result.regulation_refs[0].source_url == ""
