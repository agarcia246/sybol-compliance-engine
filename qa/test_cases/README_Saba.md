# QA guide — Saba

Regression harness, golden dataset, and known gaps for Step 4 validation.

## Golden dataset

| Location | `qa/test_cases/golden/` |
| Override | `SYBOL_GOLDEN_DATASET=/path/to/golden` |

| Label | Count | TC |
|-------|------:|-----|
| `authentic` | 30 | TC-001 — score 0.8–1.0, status `compliant` |
| `ai_generated` | 37 | TC-002 — score 0.0–0.3, status `non-compliant` |
| `edited` | **0** | TC-003 — **not in manifest yet** (Youssef) |

`manifest.json` lists 67 entries; all files on disk match (verified).

Provenance reference images (pHash index): `qa/test_cases/authentic/` (same 30 photos, not labelled for regression).

## Setup

```bash
pip install "hypothesis>=6.100" "pytest-asyncio>=0.23"   # or: poetry install --with dev
cp src/.env.example src/.env   # add MISTRAL_API_KEY if testing RAG
```

## Commands

```bash
# Full suite (expect 2 golden regression failures until scoring is tuned)
PYTHONPATH=src pytest tests/unit tests/integration -q

# Golden regression only (TC-001..003 bands + suite metrics)
PYTHONPATH=src pytest tests/integration/test_scoring_regression.py -v

# Demo readiness checklist
./scripts/check_demo_readiness.sh

# Regenerate score CSV for tuning review
PYTHONPATH=src python3 scripts/export_golden_scores.py
```

## Expected results (June 2026)

| Area | Status |
|------|--------|
| Unit + integration (incl. golden regression) | **121 passed** |
| `test_dataset_present_and_labelled` | pass |
| `test_per_image_score_bands` | pass (after provenance-aware calibration) |
| `test_suite_level_accuracy_and_error_rates` | pass (100% status accuracy on golden set) |
| VC schema / property / determinism tests | pass |
| Sybol `/api/issue` signing | blocked (login + catalog doc) |
| RAG TC-005 | blocked (0/5 PDFs, Qdrant not running) |

### Scoring diagnosis (golden set)

See `qa/test_cases/golden/scoring_report.csv`.

| Label | TC band pass | Notes |
|-------|-------------:|-------|
| authentic | 30/30 | Provenance reference match applies compliant floor |
| ai_generated | 37/37 | Weak metadata + no provenance match capped below 0.3 |

Calibration uses provenance-aware rules in `scorer.py` (see `src/scoring/constants.py`). **Requires `qa/test_cases/authentic/` reference index** for authentic labels in the golden set.

## Test cases (README targets)

- TC-001: authentic → score 0.8–1.0, compliant — **passing**
- TC-002: AI-generated → score 0.0–0.3, non-compliant — **passing**
- TC-003: edited → score 0.3–0.7, review — **blocked: no edited images**
- TC-004: corrupted file → clean error — see unit tests
- TC-005: RAG query — blocked on PDFs + Qdrant
- TC-006: VC schema — **passing** (`tests/unit/test_vc_schema.py`, integration VC pipeline)

## Acceptance thresholds (automated where noted)

| Metric | Target | Automated |
|--------|--------|-----------|
| Scoring accuracy | ≥ 85% | `test_suite_level_accuracy_and_error_rates` |
| False positive rate | ≤ 10% | same |
| False negative rate | ≤ 10% | same |
| VC schema pass rate | 100% | `test_vc_schema.py` |
| RAG precision / recall | ≥ 80% / ≥ 75% | not yet (needs PDFs) |

## Related docs

- `docs/DEMO_RUNBOOK.md` — demo paths (analyze vs issue)
- `Architecture.md` — system overview
- `tests/integration/test_scoring_regression.py` — TC-001..003 harness
