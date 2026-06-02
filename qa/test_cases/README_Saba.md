# qa/test_cases/ — Saba

The pytest framework lives in a tests/ folder at the root of the repo.
Create it if it does not exist yet. Structure it like this:

tests/
├── conftest.py          # shared fixtures, mock clients for LLM + Qdrant + Sybol API
├── unit/                # test individual components in isolation
├── integration/         # test components working together
└── e2e/                 # full FastAPI workflow end to end

Six test cases to implement using Youssef's dataset:
- TC-001: authentic image → score 0.8–1.0, status compliant
- TC-002: AI-generated image → score 0.0–0.3, status non-compliant
- TC-003: edited image → score 0.3–0.7, status review
- TC-004: corrupted file → clean error, no crash
- TC-005: RAG query → relevant regulation refs, no hallucinated laws
- TC-006: VC output → valid W3C VC Data Model 2.0 schema, all fields present

Acceptance thresholds to wire as automated assertions:
- RAG Precision ≥ 80%
- RAG Recall ≥ 75%
- Hallucination Rate ≤ 5%
- Scoring Accuracy ≥ 85%
- False Positive Rate ≤ 10%
- False Negative Rate ≤ 10%
- VC Schema Validation Pass Rate: 100%
- VC Issuance Success Rate ≥ 95%
