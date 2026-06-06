"""Mock for the Qdrant vector store client.

Qdrant has two jobs in this system:

1. **RAG index** — stores regulation-chunk embeddings (all-MiniLM-L6-v2, 384-d)
   with ``regulation`` / ``article`` / ``section`` metadata, queried top-k=5 with
   optional metadata filtering.
2. **Audit trail** — stores each media scoring result as a payload; the stored
   record URL becomes ``evidenceUrl`` in the Verifiable Credential.

This mock keeps everything in memory and does *real* cosine-similarity search so
``search`` returns a meaningful ranking rather than a hardcoded list. It mimics
the ``qdrant_client.QdrantClient`` surface (``create_collection``, ``upsert``,
``search`` / ``query_points``, ``retrieve``, ``scroll``, ``delete``,
``count``) and accepts both Qdrant's ``Filter``/``FieldCondition`` objects and
plain ``{"key": value}`` dicts so tests don't need the real SDK installed.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScoredPoint:
    """Mirrors qdrant_client.models.ScoredPoint."""

    id: str | int
    score: float
    payload: dict[str, Any] = field(default_factory=dict)
    vector: list[float] | None = None


@dataclass
class Record:
    """Mirrors qdrant_client.models.Record (retrieve/scroll result)."""

    id: str | int
    payload: dict[str, Any] = field(default_factory=dict)
    vector: list[float] | None = None


@dataclass
class _StoredPoint:
    id: str | int
    vector: list[float]
    payload: dict[str, Any]


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError(f"vector dim mismatch: {len(a)} != {len(b)}")
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _normalise_filter(query_filter: Any) -> dict[str, Any]:
    """Reduce a Qdrant Filter (or plain dict) to ``{field: must-equal-value}``.

    Supports the common case the RAG layer uses: filter retrieval by
    ``regulation`` or ``article``. Both the real ``models.Filter(must=[...])``
    object and a plain dict are accepted.
    """
    if query_filter is None:
        return {}
    if isinstance(query_filter, dict):
        return dict(query_filter)

    conditions: dict[str, Any] = {}
    must = getattr(query_filter, "must", None) or []
    for cond in must:
        key = getattr(cond, "key", None)
        match = getattr(cond, "match", None)
        value = getattr(match, "value", None) if match is not None else None
        if key is not None:
            conditions[key] = value
    return conditions


class MockQdrantClient:
    """In-memory stand-in for ``qdrant_client.QdrantClient``."""

    def __init__(self, **_: Any) -> None:
        # collection name -> {"dim": int, "points": {id: _StoredPoint}}
        self._collections: dict[str, dict[str, Any]] = {}
        self.calls: list[tuple[str, dict[str, Any]]] = []

    # -- bookkeeping ----------------------------------------------------------

    def _record(self, op: str, **kwargs: Any) -> None:
        self.calls.append((op, kwargs))

    def reset(self) -> None:
        self._collections.clear()
        self.calls.clear()

    # -- collections ----------------------------------------------------------

    def create_collection(self, collection_name: str, vectors_config: Any = None, **kwargs: Any) -> bool:
        self._record("create_collection", collection_name=collection_name)
        dim = None
        if vectors_config is not None:
            dim = getattr(vectors_config, "size", None)
            if isinstance(vectors_config, dict):
                dim = vectors_config.get("size", dim)
        self._collections[collection_name] = {"dim": dim, "points": {}}
        return True

    def recreate_collection(self, collection_name: str, vectors_config: Any = None, **kwargs: Any) -> bool:
        return self.create_collection(collection_name, vectors_config, **kwargs)

    def collection_exists(self, collection_name: str) -> bool:
        return collection_name in self._collections

    def get_collections(self) -> list[str]:
        return list(self._collections)

    def _ensure(self, collection_name: str) -> dict[str, Any]:
        if collection_name not in self._collections:
            # Match Qdrant's lenient auto-handling in tests by creating lazily.
            self._collections[collection_name] = {"dim": None, "points": {}}
        return self._collections[collection_name]

    # -- writes ---------------------------------------------------------------

    def upsert(self, collection_name: str, points: Iterable[Any], **kwargs: Any) -> dict[str, str]:
        self._record("upsert", collection_name=collection_name)
        coll = self._ensure(collection_name)
        for p in points:
            pid = getattr(p, "id", None) if not isinstance(p, dict) else p.get("id")
            vector = getattr(p, "vector", None) if not isinstance(p, dict) else p.get("vector")
            payload = getattr(p, "payload", None) if not isinstance(p, dict) else p.get("payload")
            if pid is None:
                raise ValueError("point requires an id")
            if coll["dim"] is None and vector is not None:
                coll["dim"] = len(vector)
            coll["points"][pid] = _StoredPoint(id=pid, vector=list(vector or []), payload=dict(payload or {}))
        return {"status": "completed"}

    def delete(self, collection_name: str, points_selector: Iterable[Any], **kwargs: Any) -> dict[str, str]:
        self._record("delete", collection_name=collection_name)
        coll = self._ensure(collection_name)
        for pid in points_selector:
            coll["points"].pop(pid, None)
        return {"status": "completed"}

    # -- reads ----------------------------------------------------------------

    def _passes_filter(self, payload: dict[str, Any], conditions: dict[str, Any]) -> bool:
        return all(payload.get(k) == v for k, v in conditions.items())

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 5,
        query_filter: Any = None,
        with_payload: bool = True,
        with_vectors: bool = False,
        **kwargs: Any,
    ) -> list[ScoredPoint]:
        self._record("search", collection_name=collection_name, limit=limit)
        coll = self._ensure(collection_name)
        conditions = _normalise_filter(query_filter)

        scored: list[ScoredPoint] = []
        for sp in coll["points"].values():
            if conditions and not self._passes_filter(sp.payload, conditions):
                continue
            score = _cosine(query_vector, sp.vector) if sp.vector else 0.0
            scored.append(
                ScoredPoint(
                    id=sp.id,
                    score=score,
                    payload=dict(sp.payload) if with_payload else {},
                    vector=list(sp.vector) if with_vectors else None,
                )
            )
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:limit]

    def query_points(self, collection_name: str, query: list[float], limit: int = 5, **kwargs: Any):
        """Newer Qdrant API. Returns an object with a ``.points`` attribute."""
        points = self.search(collection_name, query, limit=limit, **kwargs)

        @dataclass
        class _QueryResponse:
            points: list[ScoredPoint]

        return _QueryResponse(points=points)

    def retrieve(
        self,
        collection_name: str,
        ids: Iterable[Any],
        with_payload: bool = True,
        with_vectors: bool = False,
        **kwargs: Any,
    ) -> list[Record]:
        self._record("retrieve", collection_name=collection_name)
        coll = self._ensure(collection_name)
        out: list[Record] = []
        for pid in ids:
            sp = coll["points"].get(pid)
            if sp is not None:
                out.append(
                    Record(
                        id=sp.id,
                        payload=dict(sp.payload) if with_payload else {},
                        vector=list(sp.vector) if with_vectors else None,
                    )
                )
        return out

    def scroll(
        self, collection_name: str, limit: int = 100, with_payload: bool = True, **kwargs: Any
    ) -> tuple[list[Record], None]:
        self._record("scroll", collection_name=collection_name)
        coll = self._ensure(collection_name)
        records = [
            Record(id=sp.id, payload=dict(sp.payload) if with_payload else {})
            for sp in list(coll["points"].values())[:limit]
        ]
        return records, None  # (records, next_page_offset)

    def count(self, collection_name: str, **kwargs: Any) -> int:
        coll = self._ensure(collection_name)
        return len(coll["points"])
