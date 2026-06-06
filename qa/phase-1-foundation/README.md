# QA Test Framework — Phase 1 Foundation

Owner: Saba Zarandia (QA Lead). This is the **Phase 1** deliverable that unblocks
all QA work on the Sybol × IEU Labs compliance engine: the pytest framework,
shared fixtures (`conftest.py`), and reusable mock clients for the three
external dependencies.

Nothing in the test suite ever touches the network — Mistral, Qdrant, and Sybol
are all mocked.

## Layout

```
pyproject.toml              # pytest / coverage / ruff / black / mypy config
requirements-dev.txt        # pinned test + tooling deps
.github/workflows/ci.yml    # lint -> type-check -> unit -> integration -> coverage
tests/
  conftest.py               # central seeding + all shared fixtures
  mocks/
    mistral.py              # MockMistralClient   (Mistral Large LLM)
    qdrant.py               # MockQdrantClient    (vector store + audit trail)
    sybol.py                # MockSybolClient     (VC issuance API)
  fixtures/
    data.py                 # regulation chunks, golden labels, VC payloads
  unit/
    test_foundation.py      # self-tests + worked examples for each mock
  integration/              # (Phase 2+) end-to-end-via-mocks tests
```

## Running

```bash
pip install -r requirements-dev.txt
pytest                 # whole suite
pytest -m unit         # fast gate
pytest -m "rag or vc"  # by area
pytest --cov           # coverage (gates >=80% on src/ once it exists)
```

## The three mocks

All three are plain Python with **no hard dependency** on the real SDKs, so the
suite runs fast and offline. Each records its calls and supports failure
injection for error-path testing.

### `MockMistralClient` (`tests/mocks/mistral.py`)
Stand-in for `mistralai.Mistral`. Exposes `chat.complete(...)` /
`chat.complete_async(...)` returning an SDK-shaped response (`resp.text` /
`resp.choices[0].message.content`).

```python
def test_rag_synthesis(mock_llm):
    mock_llm.register("right to erasure", '{"regulationRefs": [{"regulation": "GDPR", ...}]}')
    # ... drive the RAG layer; assert on mock_llm.calls to check no hallucinated laws
```

Program it with `queue_response` / `queue_json` (FIFO), `register(substring, resp)`
(content match), or `fail_next(error)`. Default returns deterministic compliance
JSON.

### `MockQdrantClient` (`tests/mocks/qdrant.py`)
Stand-in for `qdrant_client.QdrantClient`. In-memory with **real cosine
similarity**, so `search(..., limit=5)` returns a meaningful top-k ranking.
Supports metadata filtering (`query_filter={"regulation": "GDPR"}` or a real
`models.Filter`), `upsert`, `retrieve`, `scroll`, `count`, `delete`. Use the
`seeded_qdrant` fixture for an index pre-loaded with sample regulation chunks.

### `MockSybolClient` (`tests/mocks/sybol.py`)
Stand-in for Sybol's businessLogic VC issuance. `issue_credential(payload)`
validates the unsigned VC, then attaches `issuer` DID, `proof`, and a
`StatusList2021Entry` `credentialStatus`, returning a signed W3C VC 2.0
credential. Tracks `success_rate` and supports `fail_next()` for the §3.6
"issuance success >= 95%" threshold. Also offers an httpx-style
`post("/credentials/issue", json=...)` surface.

> Parameterised TBDs (issuer DID, catalog schema ref, single-call vs separate
> signing endpoint) live in the constructor — update them once Iñigo confirms,
> in one place.

## Key fixtures (`conftest.py`)

| Fixture | What you get |
| --- | --- |
| `mock_llm`, `mock_qdrant`, `mock_sybol` | fresh mock clients, auto-reset |
| `seeded_qdrant` | Qdrant pre-loaded with the sample regulation index |
| `regulation_chunks`, `golden_dataset` | sample data copies |
| `unsigned_vc` | a fresh schema-valid unsigned VC payload each test |
| `sample_image_bytes` | minimal image bytes + known SHA-256 |
| `override_dependencies` | wires the mocks into the FastAPI app (Phase 2+) |

Seeding is centralised and autouse: `random`, `numpy`, and `torch` are seeded
once per session (and the stdlib RNG re-seeded per test) for reproducible
scoring and embeddings.

## Wiring into the app (once `src/` exists)

The FastAPI app doesn't exist yet — Phase 1 unblocks it. When it lands, define
DI providers (e.g. `get_llm`, `get_qdrant`, `get_sybol`) and swap them in one
place:

```python
def test_issue_endpoint(override_dependencies, mock_llm, mock_qdrant, mock_sybol):
    from src.app import app, get_llm, get_qdrant, get_sybol
    client = override_dependencies(app, {
        get_llm: mock_llm, get_qdrant: mock_qdrant, get_sybol: mock_sybol,
    })
    r = client.post("/credentials/issue", files={"image": ...})
    assert r.status_code == 200
```

## Map to the QA test plan (§3.7)

The patterns in `test_foundation.py` seed each downstream category: VC schema
validation (TC-006), golden-dataset score ranges (TC-001–003), RAG retrieval
(TC-005), and error handling (TC-004). Property-based, regression, and
determinism tests build on the same fixtures.
