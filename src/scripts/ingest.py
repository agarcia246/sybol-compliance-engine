"""One-off CLI to ingest regulation PDFs into Qdrant.

Usage (from project root):
    PYTHONPATH=src poetry run python -m scripts.ingest

Requires PDFs in research/regulations/ and QDRANT_URL in src/.env.
"""

from rag.pipeline import ingest_and_index

if __name__ == "__main__":
    ingest_and_index()
    print("Ingestion complete.")
