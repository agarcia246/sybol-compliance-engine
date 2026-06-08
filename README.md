# sybol-compliance-engine

`sybol-compliance-engine` is a Compliance AI Engine built by IEU Labs in collaboration with Sybol to score media authenticity against EU regulatory requirements and issue a W3C Verifiable Credential signed through Sybol's DID infrastructure.

## Confirmed Stack

| Layer | Technology |
|---|---|
| RAG framework | LlamaIndex |
| Vector database | Qdrant |
| LLM synthesis | Mistral Large |
| Embedding model | sentence-transformers/all-MiniLM-L6-v2 |
| Deepfake detection model | HuggingFace dima806/deepfake_vs_real_image_detection |
| Vision/signal processing | OpenCV |
| EXIF metadata extraction | ExifRead |
| Perceptual hashing | imagehash |
| API framework | FastAPI |
| Deployment platform | Railway |
| Credential standard | W3C VC Data Model 2.0 |

## Team

| Team Area | Members |
|---|---|
| Technical | Javier, Alex, Darius |
| Research | Maxim, Jana |
| QA | Youssef, Saba |

## Setup

### Prerequisites

- Python 3.10–3.13
- [Poetry](https://python-poetry.org/) (recommended) or pip

### Install dependencies

```bash
poetry install --with dev
```

Or with pip:

```bash
pip install -e ".[dev]"
```

On first run, the scoring pipeline downloads the deepfake detection model from HuggingFace (~100 MB). This happens once and is cached locally.

### Environment variables

Copy the example env file and fill in your values:

```bash
cp src/.env.example src/.env
```

| Variable | Required for | Description |
|---|---|---|
| `MISTRAL_API_KEY` | `/query` | Mistral Large API key for RAG synthesis |
| `QDRANT_URL` | `/query`, app startup | Qdrant instance URL (e.g. `http://localhost:6333`) |
| `QDRANT_API_KEY` | `/query` | Qdrant API key (optional for local Qdrant) |
| `SYBOL_*` | `/issue` | Sybol VC signing — pending Darius/Iñigo confirmation |

Scoring via `/analyze` does not require Qdrant or Mistral. If Qdrant is unavailable at startup, `/analyze` still works but `/query` returns 503 until Qdrant is running.

## Running the API

1. Create your local env file (once):

```bash
cp src/.env.example src/.env
```

For local Qdrant (optional, only needed for `/query`), set `QDRANT_URL=http://localhost:6333` in `src/.env`.

2. Start the server from the project root:

```bash
PYTHONPATH=src python3 -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

If you have Poetry installed:

```bash
PYTHONPATH=src poetry run uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

3. Open the API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

The first startup downloads the deepfake model (~100 MB) and may take 15–30 seconds.

Health check:

```bash
curl http://localhost:8000/health
```

## API Endpoints

| Endpoint | Method | Status | Description |
|---|---|---|---|
| `/health` | GET | Live | Service health check |
| `/analyze` | POST | Live | Score media authenticity (four signals → compliance status) |
| `/query` | POST | Live | Query RAG pipeline for regulation citations |
| `/issue` | POST | Stub | VC issuance — not yet implemented |

Interactive docs: `http://localhost:8000/docs`

## Score an image

### Option A — HTTP request (full API)

With the server running, upload any JPEG, PNG, or WebP file:

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@/path/to/your/image.png"
```

Example response:

```json
{
  "authenticity_score": 0.64,
  "score_breakdown": [0.46, 0.88, 0.70, 0.50],
  "compliance_status": "review",
  "media_hash": "b26da027829d45fb153c23cc0cfe0a3300e077c98d53f534f6e9ec51f33beffb"
}
```

| Field | Meaning |
|---|---|
| `authenticity_score` | Overall score in `[0.0, 1.0]` |
| `score_breakdown` | `[m, a, v, p]` — metadata, artifacts, visual, provenance |
| `compliance_status` | `compliant` (≥ 0.7), `review` (0.3–0.7), `non-compliant` (< 0.3) |
| `media_hash` | SHA-256 of the raw file before any processing |

### Option B — Python (scoring only, no Qdrant)

To test scoring without starting the API or connecting to Qdrant:

```bash
PYTHONPATH=src python3 -c "
from pathlib import Path
from scoring.pipeline import score_image

path = Path('path/to/your/image.png')
result = score_image(path.read_bytes(), filename=path.name, content_type='image/png')
print(result.model_dump_json(indent=2))
"
```

Replace `path/to/your/image.png` with your file path and set `content_type` to `image/jpeg` or `image/webp` as appropriate.

## Tests

```bash
poetry run pytest tests/unit/ --cov=src --cov-fail-under=80
poetry run pytest tests/integration/
```

## Branch Policy

All development happens on the `devel` branch. Do not push directly to `main`.
