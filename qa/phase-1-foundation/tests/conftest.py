"""Shared pytest fixtures and global test configuration.

This is the foundation Phase 1 delivers. Everything downstream (RAG eval,
golden-dataset scoring, VC schema validation, error-handling, regression and
determinism tests) builds on the fixtures defined here.

Key responsibilities:
* **Central seeding** — random / numpy / torch seeded once per session so
  scoring and embedding behaviour is reproducible (project doc §3.7).
* **Reusable mock clients** — Mistral Large, Qdrant, Sybol, each as a fixture
  that resets between tests.
* **Pre-seeded variants** — e.g. a Qdrant client already loaded with the
  sample regulation index, so RAG tests don't repeat setup.
* **App wiring helper** — once the FastAPI app exists, ``override_dependencies``
  swaps the real external clients for these mocks in one place.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Iterator
from typing import Any

import pytest

from tests.fixtures import data as sample
from tests.mocks import MockMistralClient, MockQdrantClient, MockSybolClient

GLOBAL_SEED = 1337


# --- Determinism -------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def _seed_everything() -> None:
    """Seed all RNGs once per session for reproducible scoring/embeddings."""
    random.seed(GLOBAL_SEED)
    try:
        import numpy as np

        np.random.seed(GLOBAL_SEED)
    except ImportError:
        pass
    try:
        import torch

        torch.manual_seed(GLOBAL_SEED)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(GLOBAL_SEED)
    except ImportError:
        pass


@pytest.fixture(autouse=True)
def _reseed_per_test() -> None:
    """Reset the stdlib RNG before each test so order can't leak state."""
    random.seed(GLOBAL_SEED)


# --- Mock clients ------------------------------------------------------------


@pytest.fixture
def mock_llm() -> Iterator[MockMistralClient]:
    """Fresh Mistral Large mock. Program it per test via queue/register."""
    client = MockMistralClient()
    yield client
    client.reset()


@pytest.fixture
def mock_qdrant() -> Iterator[MockQdrantClient]:
    """Fresh, empty Qdrant mock."""
    client = MockQdrantClient()
    yield client
    client.reset()


@pytest.fixture
def mock_sybol() -> Iterator[MockSybolClient]:
    """Fresh Sybol VC-issuance mock."""
    client = MockSybolClient()
    yield client
    client.reset()


# --- Pre-loaded / convenience fixtures --------------------------------------

REGULATION_COLLECTION = "regulations"


@pytest.fixture
def seeded_qdrant(mock_qdrant: MockQdrantClient) -> MockQdrantClient:
    """Qdrant mock pre-loaded with the sample regulation index."""
    mock_qdrant.create_collection(
        REGULATION_COLLECTION,
        vectors_config={"size": sample.EMBED_DIM, "distance": "Cosine"},
    )
    mock_qdrant.upsert(REGULATION_COLLECTION, sample.SAMPLE_REGULATION_CHUNKS)
    return mock_qdrant


@pytest.fixture
def regulation_chunks() -> list[dict[str, Any]]:
    return [dict(c) for c in sample.SAMPLE_REGULATION_CHUNKS]


@pytest.fixture
def golden_dataset() -> list[dict[str, Any]]:
    return [dict(c) for c in sample.GOLDEN_DATASET]


@pytest.fixture
def unsigned_vc() -> dict[str, Any]:
    """A fresh, schema-valid unsigned VC payload (regenerated each test)."""
    return sample.make_unsigned_vc()


@pytest.fixture
def sample_image_bytes() -> bytes:
    return sample.SAMPLE_IMAGE_BYTES


# --- FastAPI dependency-override helper --------------------------------------
# The app doesn't exist yet (Phase 1 unblocks it). This factory is the single
# place the suite will wire mocks into the real app once it lands, e.g.:
#
#     from src.app import app, get_llm, get_qdrant, get_sybol
#     client = override_dependencies(app, {get_llm: mock_llm, ...})
#
# Keeping it here means no test ever reaches a live Mistral/Qdrant/Sybol.


@pytest.fixture
def override_dependencies() -> Callable[..., Any]:
    def _override(app: Any, overrides: dict[Callable[..., Any], Any]):
        from fastapi.testclient import TestClient  # imported lazily

        for dependency, replacement in overrides.items():
            app.dependency_overrides[dependency] = lambda r=replacement: r
        return TestClient(app)

    return _override
