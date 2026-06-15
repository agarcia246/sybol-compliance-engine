# Sybol Compliance Engine — Project Status

**Last updated:** 14 June 2026  
**Team lead:** Javier Cruz  
**Partner:** Sybol — Iñigo García de Mata (CTO)  
**Presentation deadline:** 25 June 2026, 16:00  

This document is the single source of truth for what has been built, what remains, and how close the project is to its stated goals. It reflects the repository state on the `devel` branch.

---

## Executive summary

The **Compliance AI Engine** is a FastAPI service that scores media authenticity against EU regulatory requirements and issues a W3C Verifiable Credential via Sybol's identity infrastructure.

| Area | Status | Notes |
|------|--------|-------|
| Core scoring pipeline | **Done** | Four signals, weighted score, compliance bands |
| RAG compliance engine | **Code done, data missing** | Pipeline implemented; regulation PDFs not in repo |
| VC payload construction | **Mostly done** | VC 1.1-style payload; some VC 2.0 fields deferred |
| Sybol signing integration | **Scaffolded, blocked** | Client ready; real Cognito tokens pending |
| Automated tests | **Done** | 93 tests, ~90% coverage |
| QA golden dataset | **Not started** | Only README stubs in `qa/test_cases/` |
| Research paper | **Not started** | No `paper/draft.md` |
| End-to-end demo | **Partially ready** | `/api/analyze` works standalone; `/api/issue` blocked |

**Bottom line:** Engineering is roughly **75–80% complete**. The remaining work is dominated by external dependencies (Sybol auth), input data (regulation PDFs and labeled images), validation (acceptance tests and metrics), and deliverables (paper, technical docs, demo materials).

---

## Project goals

### Problem statement

There is no standardized, machine-readable way to prove whether a piece of media is authentic and which EU regulations apply. This project connects media scoring, regulatory retrieval, and cryptographically signed credentials into one pipeline.

### What we are building

Three interconnected parts:

1. **Media Authenticity Scoring** — Four independent signals (`m`, `a`, `v`, `p`) combined into a score in `[0.0, 1.0]` with compliance status mapping.
2. **RAG Compliance Engine** — Ingests EU regulation PDFs, retrieves relevant articles, and produces structured `regulationRefs` for explainability.
3. **Verifiable Credential Issuance** — Encodes score, breakdown, regulation citations, and audit trail into a W3C VC signed through Sybol's `businessLogic` API.

### Deliverables (priority order)

| Priority | Deliverable | Deadline | Status |
|----------|-------------|----------|--------|
| **Primary** | Research paper (publication standard) | 25 Jun 2026 | Not started |
| **Secondary** | Functional end-to-end demo (upload → score → signed VC) | 25 Jun 2026 | Partial — scoring works; signing blocked |
| **Tertiary** | Production-ready Sybol integration | 25 Jun 2026 (stretch) | Scaffolded |

### Compliance score interpretation

| Score range | Status | Meaning |
|-------------|--------|---------|
| 0.0 – 0.3 | `non-compliant` | Likely AI-generated or deepfake |
| 0.3 – 0.7 | `review` | Partially authentic or edited — human review |
| 0.7 – 1.0 | `compliant` | Passes signal checks |

---

## Team and ownership

| Person | Area | Primary responsibilities |
|--------|------|--------------------------|
| **Javier Cruz** | Technical lead | Scoring pipeline, VC payload, audit trail, repo/docs |
| **Alex Garcia Perdriau** | RAG & backend | PDF ingest, Qdrant indexing, `/query`, FastAPI, Railway |
| **Darius-Luca Petruti** | Infra & Sybol | CI/CD, Railway, Sybol API client, deployment |
| **Saba Zarandia** | QA lead | pytest framework, TC-001–006, schema/property tests |
| **Youssef Ayman** | QA & RAG eval | Golden dataset, RAG metrics, QA log |
| **Maxim Heller** | Research / legal | Regulation PDFs, legal validation, paper Ch. 3, DPIA |
| **Jana Eltoni** | Research / paper | Ch. 1 & 4, formatting, demo materials |

---

## Architecture overview

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Upload     │────▶│  Scoring Module  │────▶│  RAG Engine     │────▶│  VC Builder  │
│  (image)    │     │  m, a, v, p      │     │  Qdrant+Mistral │     │  unsigned VC │
└─────────────┘     └──────────────────┘     └─────────────────┘     └──────┬───────┘
                                                                            │
                     ┌──────────────────┐     ┌─────────────────┐          │
                     │  Qdrant audit    │◀────│  /issue route   │◀─────────┘
                     │  (evidenceUrl) │     │  orchestration  │
                     └──────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │  Sybol API      │
                                                │  signed VC      │
                                                └─────────────────┘
```

### Confirmed stack

| Layer | Technology |
|-------|------------|
| API | FastAPI |
| RAG | LlamaIndex |
| Vector DB | Qdrant |
| LLM synthesis | Mistral Large |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local) |
| Deepfake model | `dima806/deepfake_vs_real_image_detection` |
| Vision | OpenCV |
| EXIF | ExifRead |
| Perceptual hash | imagehash |
| Deployment | Railway |
| Credential standard | W3C VC (1.1 payload shape; 2.0 target in scope) |

---

## Component status

### 1. Media scoring (`src/scoring/`)

| Item | Status | Details |
|------|--------|---------|
| Preprocessing (resize 224×224, RGB, EXIF before transform) | Done | `preprocess.py` |
| Signal `m` — metadata integrity | Done | EXIF fields, editing software tags, timestamps |
| Signal `a` — generative artifacts | Done | CNN deepfake detector, FFT, noise residual |
| Signal `v` — visual consistency | Done | OpenCV lighting/shadow/edge checks; no facial landmarks |
| Signal `p` — provenance | Done (limited data) | pHash vs reference index; **reference folder empty** |
| Weighted scoring `S = wm·m + wa·a + wv·v + wp·p` | Done | Hand-tuned weights in `constants.py` |
| Platt scaling calibration | **Not done** | `PLATT_ENABLED = False`; no `platt_params.json` |
| Compliance status mapping | Done | Thresholds 0.3 / 0.7 |
| SHA-256 `media_hash` | Done | Hash of raw file before resize |
| `POST /api/analyze` | Done | Works without Qdrant or Mistral |
| Deepfake model download | Done | ~100 MB from HuggingFace on first run |

**Gaps:** Provenance defaults to `0.5` when `qa/test_cases/authentic/` is empty. Platt calibration and weight tuning on a golden dataset are not implemented. Scoring accuracy against acceptance thresholds (≥ 85%) has not been measured.

---

### 2. RAG compliance engine (`src/rag/`)

| Item | Status | Details |
|------|--------|---------|
| PDF ingestion (`SimpleDirectoryReader`) | Done | Expects PDFs in `research/regulations/` |
| Article-level chunking (`SentenceSplitter`) | Done | 400–600 token target with overlap |
| Local embedding | Done | No external embedding API calls |
| Qdrant indexing with metadata | Done | Regulation name, article, section tags |
| Query pipeline (embed → top-k=5 → Mistral) | Done | `query_regulations()` |
| Hallucination guard | Done | Drops citations with `Unknown` regulation/article |
| Structured `regulationRefs` output | Done | Ready for VC payload |
| Ingest CLI (`scripts/ingest.py`) | Done | One-off ingest into Qdrant |
| Regulation PDFs in repo | **Missing** | Only `research/regulations/README_Maxim.md` exists |
| Legal accuracy review | **Not done** | Maxim validation pending |
| RAG evaluation harness (ragas/deepeval) | **Not done** | No precision/recall/hallucination metrics |

**Required PDFs (not yet added):**

- `eu_ai_act.pdf`
- `gdpr.pdf`
- `espr_dpp.pdf`
- `lopdgdd.pdf`
- `ley_13_2022.pdf`

---

### 3. Verifiable credentials (`src/credentials/`)

| Item | Status | Details |
|------|--------|---------|
| Unsigned VC payload builder | Done | `vc_builder.py` |
| Qdrant audit trail (`evidenceUrl`) | Done | `audit.py` — metadata only, no raw images |
| Sybol API client | Done (scaffold) | `sybol_client.py` — httpx, error handling, proof validation |
| `POST /api/issue` orchestration | Done | Score → RAG → audit → build → sign |
| Sybol live signing | **Blocked** | Tokens are `TBD_` placeholders |
| VC Data Model 2.0 full compliance | **Partial** | See field comparison below |

**VC field status:**

| Field (scope doc) | In payload? | Notes |
|-------------------|-------------|-------|
| `id` | Yes | `urn:uuid:{uuid}` |
| `type` | Yes | `VerifiableCredential`, `MediaComplianceCredential` |
| `issuer` | No | Resolved server-side by Sybol from auth context |
| `issuanceDate` | Yes | VC 1.1 field name |
| `validFrom` | No | VC 2.0 field — deferred |
| `credentialSchema` | No | Pending Sybol catalog confirmation |
| `credentialStatus` | No | StatusList2021 — pending catalog confirmation |
| `credentialSubject.*` | Yes | Score, breakdown, status, refs, hash, timestamps |
| `evidenceUrl` | Yes | Qdrant audit record URL |

---

### 4. API layer (`src/api/`)

| Endpoint | Method | Status | Dependencies |
|----------|--------|--------|--------------|
| `/health` | GET | **Live** | None |
| `/api/analyze` | POST | **Live** | Scoring only |
| `/api/query` | POST | **Live** (503 if no index) | Qdrant + ingest + `MISTRAL_API_KEY` |
| `/api/issue` | POST | **Live** (503 if unconfigured) | Qdrant + Mistral + Sybol tokens |

Interactive docs: `http://localhost:8000/docs`

Startup behaviour: if Qdrant is unavailable, the app still starts; `/api/analyze` works, but `/api/query` and `/api/issue` return 503 until the index is available.

---

### 5. Infrastructure and deployment

| Item | Status | Details |
|------|--------|---------|
| `railway.toml` | Done | Uvicorn start command, `/health` check |
| GitHub Actions CI (`.github/workflows/ci.yml`) | Done | Lint, format, mypy, pytest on `devel` PRs/pushes |
| Poetry + dev dependencies | Done | pytest, ruff, black, mypy, coverage |
| OpenAPI export script | Done | `scripts/export_openapi.py` |
| Railway Qdrant service | Unknown | Documented; needs persistent volume at `/qdrant/storage` |
| Production env vars on Railway | Partial | `QDRANT_URL` in example; Sybol tokens TBD |
| Auto-deploy from `main` | Documented | Requires Railway ↔ GitHub connection |

---

## Testing and QA status

### Automated tests (done)

| Metric | Value |
|--------|-------|
| Total tests | **93** (84 unit + 9 integration) |
| Coverage | **~90%** (threshold: 80%) |
| Framework | pytest + pytest-cov + pytest-mock + pytest-asyncio |
| External mocks | Qdrant, Mistral, Sybol, deepfake model in `conftest.py` |

**Test layout:**

```
tests/
├── conftest.py
├── unit/          # 20 test files — scoring, RAG, API, credentials
└── integration/   # scoring pipeline, RAG pipeline, VC pipeline
```

### QA deliverables (not done)

| Item | Owner | Status |
|------|-------|--------|
| Golden image dataset (`authentic/`, `ai_generated/`, `edited/`, `corrupted/`) | Youssef | Not started — README only |
| TC-001: authentic → compliant (0.8–1.0) | Saba + Youssef | Not implemented |
| TC-002: AI-generated → non-compliant (0.0–0.3) | Saba + Youssef | Not implemented |
| TC-003: edited → review (0.3–0.7) | Saba + Youssef | Not implemented |
| TC-004: corrupted file → clean error | Saba + Youssef | Not implemented |
| TC-005: RAG query → valid regulation refs | Saba + Youssef | Not implemented |
| TC-006: VC → valid schema, all fields | Saba | Not implemented |
| `tests/e2e/` full workflow tests | Saba | Not created |
| jsonschema VC validation tests | Saba | Dependency installed, no tests |
| hypothesis property-based scoring tests | Saba | Dependency installed, no tests |
| RAG evaluation (precision ≥ 80%, recall ≥ 75%, hallucination ≤ 5%) | Youssef | Not run |
| QA log (Section 3.5 of project doc) | Youssef | Not started |

---

## Research and documentation status

| Item | Owner | Status |
|------|-------|--------|
| `docs/architecture.md` | Javier | **Missing** |
| `docs/vc_schema.md` | Javier | **Missing** |
| `paper/draft.md` | Team | **Missing** |
| Paper Chapter 3 — Regulatory Landscape | Maxim | Not started |
| Paper Chapter 1 — Introduction | Jana | Not started |
| Paper Chapter 4 — System Design | Jana | Blocked on `architecture.md` |
| Paper Chapter 5 — Evaluation | Saba + Youssef | Blocked on TC execution |
| DPIA documentation | Maxim | Not started |
| Project change log (Tab 4) | Team | Essentially empty |
| Demo walkthrough script and slides | Jana | Not started |

---

## Environment variables

Copy `src/.env.example` to `src/.env`:

| Variable | Required for | Current status |
|----------|--------------|----------------|
| `MISTRAL_API_KEY` | `/api/query`, `/api/issue` (RAG step) | Placeholder in example |
| `QDRANT_URL` | `/api/query`, `/api/issue` | Example points to Railway internal URL |
| `QDRANT_API_KEY` | Qdrant auth (optional locally) | Example value present |
| `SYBOL_API_URL` | `/api/issue` | Set to `https://api.sybol.io/api/bl/credentials` |
| `SYBOL_ACCESS_TOKEN` | `/api/issue` | **`TBD_pending_darius_confirmation_with_inigo`** |
| `SYBOL_ID_TOKEN` | `/api/issue` | **`TBD_pending_darius_confirmation_with_inigo`** |
| `SYBOL_REQUEST_TIMEOUT` | `/api/issue` | Default `10.0` |

---

## Blockers and dependencies

### Critical path

```
Maxim adds PDFs → Alex/Darius runs ingest → Javier scoring + VC ready
                                                      ↓
                              Iñigo confirms Sybol endpoint + tokens (Darius)
                                                      ↓
                              End-to-end /api/issue demo → QA validation → paper
```

### Blocker 1 — Sybol signing (highest priority)

**Owner:** Darius → Iñigo (`inigo@sybol.id`)

Open questions (from `src/credentials/README_Darius.md`):

1. Issuer DID value (or confirmation it is resolved from tenant auth context)
2. `MEDIA_COMPLIANCE_CREDENTIAL` registered in Sybol catalog
3. Signing endpoint confirmation (`POST /api/bl/credentials` vs alternative)
4. Valid Cognito `access_token` and `id_token` for integration testing

Until resolved, `/api/issue` returns **503** with message: *"Sybol signing is not configured"*.

### Blocker 2 — Regulation PDFs

**Owner:** Maxim

Without PDFs, ingest fails with `FileNotFoundError: No regulation PDFs found` and RAG cannot run in production.

### Blocker 3 — Golden dataset

**Owner:** Youssef

Without labeled images, scoring accuracy cannot be validated and provenance signal has no reference index.

---

## Acceptance criteria gap analysis

From the project scope (`docs/AI Lab Summer Work.md`) and QA READMEs:

| Criterion | Target | Measured? |
|-----------|--------|-----------|
| RAG Precision | ≥ 80% | No |
| RAG Recall | ≥ 75% | No |
| Hallucination Rate | ≤ 5% | No |
| Scoring Accuracy | ≥ 85% | No |
| False Positive Rate | ≤ 10% | No |
| False Negative Rate | ≤ 10% | No |
| VC Schema Validation Pass Rate | 100% | No |
| VC Issuance Success Rate | ≥ 95% | No (blocked on Sybol) |
| Test coverage | ≥ 80% | **Yes — ~90%** |

---

## What works today (verification steps)

### Scoring only (no external services)

```bash
poetry install --with dev
PYTHONPATH=src poetry run uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@/path/to/image.png"
```

### Automated test suite

```bash
poetry run pytest tests/unit/ --cov=src --cov-fail-under=80
poetry run pytest tests/integration/
```

### Full pipeline (when dependencies are ready)

1. Start Qdrant: `docker run -p 6333:6333 qdrant/qdrant`
2. Add regulation PDFs to `research/regulations/`
3. Ingest: `PYTHONPATH=src poetry run python -m scripts.ingest`
4. Set `MISTRAL_API_KEY` and Sybol tokens in `src/.env`
5. Call `POST /api/issue` with an image file

---

## Recommended priority (before 25 June)

### Week of 14 June — must-have for demo

| # | Action | Owner | Unblocks |
|---|--------|-------|----------|
| 1 | Contact Iñigo for Sybol tokens + endpoint + catalog confirmation | Darius | Signed VC demo |
| 2 | Add five regulation PDFs to `research/regulations/` | Maxim | RAG + `/api/issue` |
| 3 | Run Qdrant ingest on deployed/staging instance | Alex / Darius | Live `/api/query` |
| 4 | Create golden dataset (5–10 images per category minimum) | Youssef | TC-001–004 |
| 5 | Smoke-test full `/api/issue` flow once tokens arrive | Javier / Darius | Demo readiness |

### Week of 18 June — presentation prep

| # | Action | Owner |
|---|--------|-------|
| 6 | Run TC-001–006 manually; log pass/fail | Saba + Youssef |
| 7 | Write `docs/architecture.md` and `docs/vc_schema.md` | Javier |
| 8 | Draft paper chapters (Maxim Ch.3, Jana Ch.1/4) | Maxim, Jana |
| 9 | Prepare demo script with curated test images | Jana |
| 10 | Validate RAG citations against source PDFs | Maxim |

### Stretch (if time allows)

- Implement Platt scaling with calibrated `platt_params.json`
- Add VC 2.0 fields (`validFrom`, `credentialSchema`, `credentialStatus`) once Sybol confirms
- Automate TC-001–006 and jsonschema validation
- Build RAG evaluation harness with ragas/deepeval
- Complete DPIA documentation

---

## Repository map (implementation)

```
src/
├── api/                  # FastAPI app, routes, schemas, dependencies
│   └── routes/
│       ├── analyze.py    # POST /api/analyze
│       ├── query.py      # POST /api/query
│       └── issue.py      # POST /api/issue
├── scoring/              # Media authenticity pipeline
├── rag/                  # Regulation ingest, index, query
├── credentials/          # VC builder, Sybol client, audit trail
└── scripts/
    ├── ingest.py         # One-off PDF → Qdrant ingest
    └── export_openapi.py

tests/                    # 93 automated tests
qa/test_cases/            # README stubs only — no image data yet
research/regulations/     # README only — no PDFs yet
paper/                    # README stubs only — no draft yet
docs/                     # Project scope doc + this status file
sybol_docs/               # Sybol platform reference documentation (not part of engine code)
```

---

## Summary scorecard

| Workstream | Progress | Blocker |
|------------|----------|---------|
| Scoring engine | ████████░░ 85% | Golden dataset + Platt calibration |
| RAG engine | ███████░░░ 70% | Regulation PDFs + legal review |
| VC issuance | ██████░░░░ 60% | Sybol tokens + catalog fields |
| API & deployment | ████████░░ 85% | Production env configuration |
| Automated testing | █████████░ 90% | E2E + acceptance tests |
| QA validation | ██░░░░░░░░ 15% | Dataset + TC execution |
| Research paper | ░░░░░░░░░░ 0% | All chapters |
| Demo readiness | ████░░░░░░ 40% | Sybol + data + script |

---

## References

- [README.md](../README.md) — setup and run instructions
- [docs/AI Lab Summer Work.md](./AI%20Lab%20Summer%20Work.md) — full scope, task split, dependency chain
- [src/credentials/README_Darius.md](../src/credentials/README_Darius.md) — Sybol integration notes
- [research/regulations/README_Maxim.md](../research/regulations/README_Maxim.md) — required PDF list
- [qa/test_cases/README_Saba.md](../qa/test_cases/README_Saba.md) — test case definitions
- [qa/test_cases/README_Youssef.md](../qa/test_cases/README_Youssef.md) — dataset requirements

---

*Maintained by the technical team. Update this file when a major milestone is completed or a blocker is resolved.*
