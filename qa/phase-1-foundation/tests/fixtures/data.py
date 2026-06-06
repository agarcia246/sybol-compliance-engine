"""Deterministic sample data shared across the test suite.

Nothing here touches the network or the filesystem. Embeddings are tiny,
hand-built unit-ish vectors (not 384-d) so similarity ordering is easy to
reason about in assertions; swap in real 384-d vectors only where a test
specifically exercises dimensionality.
"""

from __future__ import annotations

import hashlib
from typing import Any

# --- Regulation chunks for the RAG index ------------------------------------
# payload mirrors the chunk metadata the LlamaIndex pipeline attaches:
# regulation name, article number, section, plus the chunk text.

SAMPLE_REGULATION_CHUNKS: list[dict[str, Any]] = [
    {
        "id": "ai-act-50",
        "vector": [1.0, 0.0, 0.0, 0.0],
        "payload": {
            "regulation": "EU AI Act",
            "article": "Article 50",
            "section": "Transparency obligations",
            "url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
            "text": (
                "Providers of AI systems generating synthetic content must "
                "ensure outputs are marked as artificially generated."
            ),
        },
    },
    {
        "id": "ai-act-5",
        "vector": [0.9, 0.1, 0.0, 0.0],
        "payload": {
            "regulation": "EU AI Act",
            "article": "Article 5",
            "section": "Prohibited practices",
            "url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
            "text": "Biometric categorisation inferring sensitive attributes is prohibited.",
        },
    },
    {
        "id": "gdpr-22",
        "vector": [0.0, 1.0, 0.0, 0.0],
        "payload": {
            "regulation": "GDPR",
            "article": "Article 22",
            "section": "Automated decision-making",
            "url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
            "text": (
                "Data subjects have the right not to be subject to solely "
                "automated decisions with legal effects."
            ),
        },
    },
    {
        "id": "gdpr-17",
        "vector": [0.0, 0.9, 0.1, 0.0],
        "payload": {
            "regulation": "GDPR",
            "article": "Article 17",
            "section": "Right to erasure",
            "url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
            "text": (
                "The right to erasure interacts with VC immutability; "
                "off-chain storage with on-chain status is preferred."
            ),
        },
    },
    {
        "id": "lopdgdd-35",
        "vector": [0.0, 0.0, 1.0, 0.0],
        "payload": {
            "regulation": "LOPDGDD",
            "article": "Article 35.4",
            "section": "Mandatory DPIA list",
            "url": "https://www.boe.es/eli/es/lo/2018/12/05/3",
            "text": (
                "Processing operations on the AEPD list require a mandatory "
                "Data Protection Impact Assessment."
            ),
        },
    },
]

# A query embedding that should rank the AI Act Article 50 chunk first.
SAMPLE_QUERY_VECTOR_TRANSPARENCY = [0.95, 0.05, 0.0, 0.0]
EMBED_DIM = 4


# --- Golden dataset labels (TC-001 .. TC-003) -------------------------------
# Maps a logical image id to its category and the expected authenticity-score
# band per the scoring framework (0.0-0.3 non-compliant / 0.3-0.7 review /
# 0.7-1.0 compliant).

GOLDEN_DATASET: list[dict[str, Any]] = [
    {
        "image_id": "real_camera_01",
        "category": "authentic",
        "expected_range": (0.7, 1.0),
        "expected_status": "compliant",
    },
    {
        "image_id": "midjourney_01",
        "category": "ai_generated",
        "expected_range": (0.0, 0.3),
        "expected_status": "non-compliant",
    },
    {
        "image_id": "photoshop_composite_01",
        "category": "edited",
        "expected_range": (0.3, 0.7),
        "expected_status": "review",
    },
]


def make_media_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


SAMPLE_IMAGE_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 64  # minimal JPEG-ish header
SAMPLE_MEDIA_HASH = make_media_hash(SAMPLE_IMAGE_BYTES)


# --- Unsigned VC payload (what the VC Generation Layer hands to Sybol) -------


def make_unsigned_vc(
    media_hash: str = SAMPLE_MEDIA_HASH,
    authenticity_score: float = 0.86,
    compliance_status: str = "compliant",
) -> dict[str, Any]:
    """Build a fresh unsigned VC payload matching the §2.5 schema."""
    return {
        "@context": ["https://www.w3.org/ns/credentials/v2"],
        "type": ["VerifiableCredential", "MediaComplianceCredential"],
        "credentialSubject": {
            "id": f"urn:media:{media_hash}",
            "mediaHash": media_hash,
            "authenticityScore": authenticity_score,
            "scoreBreakdown": {"m": 0.9, "a": 0.88, "v": 0.84, "p": 0.82},
            "complianceStatus": compliance_status,
            "regulationRefs": [
                {
                    "regulation": "EU AI Act",
                    "article": "Article 50",
                    "url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
                }
            ],
            "modelVersion": "media-scorer-0.1.0",
            "analysisTimestamp": "2026-05-01T12:00:00Z",
            "evidenceUrl": "https://qdrant.internal/audit/abc123",
        },
    }
