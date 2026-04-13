# sybol-compliance-engine

AI compliance engine for media authenticity scoring and verifiable credential issuance.
Built by IEU Labs in collaboration with [Sybol](https://sybol.id).

---

## What it does

Takes a media asset, scores it on a spectrum from fully AI-generated (deepfake) to fully authentic, and issues a cryptographically signed **Verifiable Credential** (W3C VC Data Model 2.0) encoding that score — compliant with the EU AI Act, GDPR, and Spanish regulation.

---

## Team

| Name | Role | Team |
|---|---|---|
| Javier Cruz | Team Lead | Technical |
| Maxim Heller | Developer | Technical |
| Darius-Luca Petruti | Developer | Technical |
| Alex Garcia Perdriau | Developer | Technical |
| Jana Eltoni | Researcher | Research |
| Youssef Ayman | Researcher | Research |
| Saba Zarandia | QA Engineer | QA |

---

## Repo structure

```
sybol-compliance-engine/
├── src/
│   ├── rag/            # RAG pipeline — regulation ingestion & retrieval
│   ├── scoring/        # Media authenticity scoring module
│   └── credentials/    # Verifiable Credential generation
├── research/
│   └── regulations/    # EU AI Act, GDPR, DPP, Spanish law notes
├── qa/
│   └── test_cases/     # Test cases and evaluation results
├── paper/              # Research paper drafts
└── docs/               # Architecture diagrams and technical docs
```

---

## Timeline

| | |
|---|---|
| Start | April 6, 2026 |
| End | May 15, 2026 |
| Primary deliverable | Research paper |
| Secondary | Demo |

---

## Stack

| Layer | Tool |
|---|---|
| RAG Pipeline | TBD |
| LLM | TBD |
| Vector DB | TBD |
| VC Schema | W3C VC Data Model 2.0 |
| Backend | TBD |

---

## References

- [W3C DID 1.0](https://www.w3.org/TR/did-1.0/#identifier)
- [W3C VC Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [EU Digital Product Passport](https://data.europa.eu/en/news-events/news/eus-digital-product-passport-advancing-transparency-and-sustainability)
- [RAG Pipeline reference](https://stormap.ai/post/building-a-rag-pipeline-with-openclaw)

---

*IEU Labs × Sybol — 2026*
