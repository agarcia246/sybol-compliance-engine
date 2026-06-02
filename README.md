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

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill the values.
4. Run the API locally:
   ```bash
   uvicorn main:app --reload
   ```

## Branch Policy

All development happens on the `devel` branch. Do not push directly to `main`.
