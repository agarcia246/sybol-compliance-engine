"""Reusable mock clients for the Sybol compliance-engine test suite.

Import these anywhere in the suite::

    from tests.mocks import MockMistralClient, MockQdrantClient, MockSybolClient

They are also exposed as pytest fixtures in ``tests/conftest.py``
(``mock_llm``, ``mock_qdrant``, ``mock_sybol``).
"""

from tests.mocks.mistral import (
    DEFAULT_COMPLIANCE_ANSWER,
    ChatCompletionResponse,
    MockMistralClient,
)
from tests.mocks.qdrant import MockQdrantClient, Record, ScoredPoint
from tests.mocks.sybol import (
    DEFAULT_ISSUER_DID,
    MockSybolClient,
    SybolAPIError,
)

__all__ = [
    "MockMistralClient",
    "ChatCompletionResponse",
    "DEFAULT_COMPLIANCE_ANSWER",
    "MockQdrantClient",
    "ScoredPoint",
    "Record",
    "MockSybolClient",
    "SybolAPIError",
    "DEFAULT_ISSUER_DID",
]
