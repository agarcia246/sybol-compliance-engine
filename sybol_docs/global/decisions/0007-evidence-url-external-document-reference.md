# ADR-0006: Evidence URL — External Document Reference on Credentials (v0)

**Status:** Accepted

**Date:** 2026-03-30

**Authors:** @inigoSybol

**Deciders:** @inigoSybol

**Linked issue:** [#8 — Gestor documental con acceso privado](https://github.com/Sybolid/sybolRelases/issues/8)

---

## Context and Problem Statement

Tenants need to associate evidence documents (contracts, certificates, licenses) with issued credentials in the Sybol platform. Implementing a full private document store with S3 storage and access control (v1) requires significant effort. Meanwhile, tenants already host their evidence in external systems (Google Drive, SharePoint, Notion, their own S3) and need a lightweight way to reference them.

The natural place for evidence is **the credential itself** — a credential is the digital assertion that a fact is true, and the evidence URL is the pointer to the source that backs it up.

**Question:** Where should `evidence_url` live, and how do we attach it to a credential without breaking cryptographic integrity?

---

## Decision

Add `evidence_url` as a **metadata column** on the `credentials` table in the `businessLogic` service.

The field lives **outside the signed JWT** — it does not alter `signed_token` or `payload`, preserving full W3C VC compliance and cryptographic integrity. It is a platform-level annotation: "this credential is backed by this external document."

---

## Rationale: Why credentials, not catalog documents

| Option | Rejected? | Reason |
|--------|-----------|--------|
| Column on `documents` (catalog service) | ✅ Rejected | Catalog documents are templates — they define *types* of credentials, not instances. Evidence is tied to a specific issued credential, not to the template. |
| Field inside the JWT payload | ✅ Rejected | Would require re-signing — breaking immutability of the VC. |
| New `evidence` microservice | ✅ Rejected for v0 | Over-engineering for a single URL field. |
| Column on `credentials` (businessLogic) | ✅ **Accepted** | Credentials are the issuance records. Evidence supports a specific issuance. Stored as metadata outside the JWT, preserving integrity. |

---

## Implementation Spec

### Target service
`services/businessLogic`

### Database

**`credentials` table** — add column:
```sql
ALTER TABLE credentials
  ADD COLUMN IF NOT EXISTS evidence_url VARCHAR(2048) DEFAULT NULL;
```

**New `evidence_url_traces` audit table:**
```sql
CREATE TABLE evidence_url_traces (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  credential_jti  UUID NOT NULL REFERENCES credentials(jti) ON DELETE CASCADE,
  evidence_url    VARCHAR(2048),
  state           VARCHAR(50) NOT NULL DEFAULT 'active',  -- active | archived
  updated_by      VARCHAR(255) NOT NULL,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT valid_evidence_url_trace_state CHECK (state IN ('active', 'archived'))
);
```

### API

`evidence_url` is updated via the existing credential update endpoint. No new routes.

```http
POST /api/bl/credentials/{jti}
Authorization: Bearer <access_token>
x-id-token: <id_token>

{ "evidence_url": "https://drive.google.com/file/d/1ABC..." }
```

To clear:
```http
POST /api/bl/credentials/{jti}

{ "evidence_url": null }
```

Every change triggers an insert into `evidence_url_traces` (automatic in repository layer).

### Response

The credential response includes `evidence_url` as a top-level field alongside `jti`, `payload`, etc.:
```json
{
  "jti": "550e8400-...",
  "payload": { "iss": "...", "sub": "...", "vc": { ... } },
  "evidence_url": "https://drive.google.com/file/d/1ABC...",
  "created_at": "2026-03-30T10:00:00Z"
}
```

> ℹ️ `evidence_url` is **never** injected into `signed_token` or `payload`. It is metadata only.

---

## Consequences

### Positive
- Zero new infrastructure.
- Cryptographic integrity of the JWT is preserved.
- Tenants can reference their evidence immediately.
- Consistent with `credential_requests.evidence` JSONB pattern already present in the schema.
- Full audit trail via `evidence_url_traces`.

### Negative / Trade-offs
- Sybol has no control over access to the external document (by design for v0).
- Single `evidence_url` per credential — multiple evidence links require v1.
- No validation that the URL is accessible or the document exists.

### Neutral
- v1 (full private document store with S3 and per-credential access control) remains on the roadmap. This decision does not block or conflict with it.

---

## Pending

- [ ] Revert `evidence_url` addition from `services/catalog` (wrong service — added during initial implementation)
- [ ] Implement migration and repository changes in `services/businessLogic`
- [ ] Update `businesslogic-api.md` with credential update field documentation
