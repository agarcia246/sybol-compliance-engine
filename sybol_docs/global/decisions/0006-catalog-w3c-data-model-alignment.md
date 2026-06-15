# ADR-0006: Catalog Service W3C Data Model Alignment

**Status:** Proposed

**Date:** 2024-Q1

**Authors:** @architect, @data-lead, @product-owner

**Deciders:** @cto, @architect, @security-lead

**Related:** [ADR-0004 – W3C Verifiable Credentials Standard](0004-w3c-verifiable-credentials.md)  
**Implements:** [Catalog Data Model Specification v2.0](../../services/catalog/docs/DATA_MODEL_SPEC.md)

---

## 1. Context and Problem Statement

The Sybol Catalog Service manages the *structural vocabulary* of the platform: it defines what credential types exist (**Documents**), what data points they contain (**Claims**), and how data is requested from holders (**Forms**).

**ADR-0004** established that Sybol uses the **W3C Verifiable Credentials Data Model v1.1** as its credential format. However, the Catalog Service v1 data model was designed before that decision was fully operationalized, resulting in a semantic gap: the catalog stores credential templates and presentation templates without explicitly mapping them to their W3C VC counterparts.

This creates the following concrete problems:

1. **Document entities have no `vc_type` or `@context`**: the blockchainManager service cannot derive a valid, schema-compliant VC from a document record without hardcoded mappings.
2. **Claims have no `semantic_id`**: cross-system credential exchange is limited because claims cannot be correlated with standard vocabularies (schema.org, EBSI, etc.).
3. **Forms have no `purpose` or `credential_requirements`**: they cannot generate standards-compliant Verifiable Presentation Requests (DIF Presentation Exchange 2.0).
4. **No selective disclosure metadata**: the catalog cannot declare which claims support BBS+ / SD-JWT selective disclosure, blocking privacy-preserving flows.
5. **Translations are incomplete**: Form sections and form field overrides are stored as plain strings, preventing full multilingual support.
6. **No lifecycle formalism**: the state machine for Documents and Forms lacks the `deprecated` state needed to manage retiring schemas while preserving historical audit records.

**Question:** How should we evolve the Catalog data model to become a first-class participant in the W3C VC ecosystem while maintaining backward compatibility?

---

## 2. Decision Drivers

- **W3C VC Alignment** (ADR-0004): The catalog must speak W3C VC vocabulary natively.
- **Interoperability**: Issued VCs must reference catalog-defined credential schemas (`credentialSchema` field).
- **Selective Disclosure**: Support BBS+ and SD-JWT flows by encoding disclosure policy per-claim.
- **DIF Presentation Exchange**: Forms must map to PE 2.0 `presentation_definition` structures.
- **eIDAS 2.0 Compliance**: EU ARF requires VC types to declare their JSON-LD context and schema URL.
- **Multilingual support**: All human-readable fields must support translations (JSONB maps).
- **Backward compatibility**: v1 records must remain queryable; migration must be non-destructive.
- **Auditability**: Deprecated schemes must be preserved for verification of historical credentials.
- **Developer ergonomics**: New fields must have sensible defaults so that v1-style API calls continue to work.

---

## 3. Considered Options

### Option A: Minimal Annotation Layer (Add metadata without schema changes)

Store W3C-specific metadata (vc_type, context, semantic_id, etc.) as a denormalized `metadata` JSONB column on existing tables.

**Pros:**
- ✅ No schema migration for existing columns
- ✅ Lowest deployment risk
- ✅ Fast to implement

**Cons:**
- ❌ No query indexing on metadata fields (poor performance for filter-by-vc-type)
- ❌ No database-level constraints on W3C fields (invalid contexts accepted silently)
- ❌ JSON Schemas cannot be auto-generated from DB schema
- ❌ Semantic coupling leaks into application code
- ❌ Does not solve the form/section translation problem

**Verdict:** Rejected. Provides insufficient structure and introduces implicit contracts.

---

### Option B: Full Schema Extension — New Columns on Existing Tables (CHOSEN)

Add new first-class columns to the existing tables:
- `documents`: `vc_type`, `context`, `schema_url`, `version`, `compliance_regions`, `issuer_requirements`, `revocation`, `expiry_policy`, `selective_disclosure`, `display`
- `claims`: `semantic_id`, `path`, `constraints`, `regex_flags`, `essential`, `selective_disclosure_policy`, `source_type`, `display`
- `forms`: `version`, `purpose`, `compliance_regions`, `credential_requirements`, `format_preferences`, `response_expiry_seconds`
- `form_sections`: Replace `title`/`description` plain strings with `translations` JSONB
- `form_fields`: Replace `label_override`/`help_text` plain strings with `label_override_translations`/`help_text_translations` JSONB

**Pros:**
- ✅ Full database constraint enforcement (CHECK, NOT NULL, GIN indexes)
- ✅ Direct SQL queries on W3C fields (filter by vc_type, compliance_region, etc.)
- ✅ JSON Schemas accurately reflect the database structure
- ✅ Enables auto-generation of `presentation_definition` from form records
- ✅ Aligns catalog as the authoritative schema registry for blockchainManager
- ✅ All new columns are nullable / have defaults → non-breaking for existing records
- ✅ Section/field translations enable full i18n without language fallback hacks

**Cons:**
- ❌ Requires a database migration
- ❌ Breaking change for `form_sections.title` and `form_fields.label_override` (application-layer migration needed)
- ❌ Higher implementation effort than Option A

**Verdict:** ✅ Chosen. The structural benefits justify the migration cost.

---

### Option C: Separate Credential Schema Registry Service

Extract credential type definitions (Documents + Claims) into a dedicated **Schema Registry** microservice, leaving the Catalog only with Forms.

**Pros:**
- ✅ Clean separation of concerns
- ✅ Schema Registry can be independently versioned and exposed as a public endpoint
- ✅ Aligns with EBSI Trusted Schema Registry architecture

**Cons:**
- ❌ High coordination overhead between two services for every form/document operation
- ❌ Doubles the deployment surface for a concern currently cohesive in one service
- ❌ Premature decomposition — current traffic and team size do not justify it
- ❌ Does not solve the migration problem; defers it while adding complexity

**Verdict:** Deferred to a future ADR. May be revisited at scale.

---

## 4. Decision Outcome

**Chosen option: Option B — Full Schema Extension**

Evolve the Catalog Service to v2 by adding first-class W3C VC fields to the existing PostgreSQL tables. All new columns are nullable or have sensible defaults to ensure backward compatibility with v1 API clients. The breaking changes (`form_sections.translations`, `form_fields.label_override_translations`) require a migration script and a coordinated API version bump.

---

## 5. Implementation Decisions

### 5.1 Document → Verifiable Credential Mapping

| Document field | VC field | Notes |
|---|---|---|
| `vc_type[]` | `@type` | First element is always `"VerifiableCredential"` |
| `context[]` | `@context` | First element is always the W3C VC base context |
| `schema_url` | `credentialSchema.id` | Points to published JSON Schema |
| `revocation.method` | `credentialStatus.type` | Defaults to `StatusList2021` |
| `expiry_policy.default_validity_days` | `expirationDate` (computed) | blockchainManager adds days from issuanceDate |
| `issuer_requirements.did_methods` | Verified against `issuer` DID | During VC verification |

### 5.2 Form → Verifiable Presentation Request Mapping

| Form field | VP Request / DIF PE field | Notes |
|---|---|---|
| `code` | `presentation_definition.id` | |
| `purpose` | `presentation_definition.purpose` | English canonical statement |
| `credential_requirements[].document_code` | `input_descriptor.id` | |
| `credential_requirements[].group` | `submission_requirements[*].from_nested` | OR logic groups |
| `format_preferences[]` | `format` object | Ordered list |
| `response_expiry_seconds` | `exp` claim in VP JWT | |
| `sections[].fields[].claim_id → claim.key` | `input_descriptor.constraints.fields[].path` | JSONPath in credentialSubject |

### 5.3 Selective Disclosure Policy Enforcement

When `document.selective_disclosure = true`, claims are processed via SD-JWT or BBS+:
- `always_disclosed` claims → included in the mandatory disclosure set
- `selectable` claims → included in the selective disclosure set (holder chooses at presentation)
- `never_disclosed` claims → excluded from presentation; stored only in the VC (holder internal)

### 5.4 Compliance — Two Orthogonal Fields

The data model distinguishes two semantically different compliance dimensions with dedicated fields:

| Field | Semantic | Cardinality | Example |
|---|---|---|---|
| `compliance_path` | **Issuing authority** — who officially defines/produces this credential type | 1 (unique) | `pub.es.policiaNacional` |
| `compliance_regions[]` | **Recognition scope** — where the credential is legally accepted | 0..N | `[eu, eu.es, eu.de]` |

These answer different questions:
- `compliance_path` answers *"who issues this?"* — static, tied to the official authority, immutable after activation.
- `compliance_regions` answers *"where is this recognized?"* — dynamic, can be extended as new jurisdictions adopt the credential type.

**Rationale for keeping both:**
- A credential type has exactly one issuing authority (one `compliance_path`), but recognition is multi-jurisdictional.
- Using `compliance_path` alone would force replicating the document for each jurisdiction.
- Using only `compliance_regions` would lose the authoritative origin information needed for issuer validation.

**Example — Spanish DNI:**
```json
{
  "code": "DNI_ES",
  "compliance_path": "pub.es.policiaNacional",
  "compliance_regions": ["eu", "eu.es", "eu.de", "eu.fr", "eu.it", "sectoral.eidas"]
}
```

We retain `compliance_path` (existing, unique, indexed) for backward compatibility. The `compliance_path` pattern is extended to support a three-level `{sector}.{country}.{authority}` notation (was `{sector}.{country}`).

### 5.5 Section and Field Translation Migration

The migration from plain `title`/`description` to `translations` JSONB in `form_sections` follows this pattern:

```sql
UPDATE form_sections
SET translations = jsonb_build_object(
    COALESCE(
        (SELECT default_lang_code FROM forms WHERE forms.id = form_sections.form_id),
        'es'
    ),
    jsonb_build_object(
        'title', title,
        'description', description
    )
)
WHERE translations IS NULL OR translations = '{}'::jsonb;
```

After migration, the old `title` and `description` columns can be dropped in a subsequent release.

Similarly for `form_fields.label_override` → `label_override_translations`.

---

## 6. Consequences

### Positive

- The blockchainManager can derive all required VC fields directly from catalog records — no hardcoded type mappings.
- Forms can generate valid DIF PE 2.0 `presentation_definition` objects programmatically.
- Credentials issued against a catalog Document version are fully traceable via `schema_url` → `credentialSchema`.
- All human-facing strings are translatable — enables multi-language onboarding flows.
- Selective disclosure is declared at catalog level, not scattered across the issuance service.
- The `deprecated` state enables managing credential type retirement without destroying historical records.

### Negative / Risks

- **Migration complexity**: Form section and field translation migration requires a coordinated deploy with the blockchainManager and frontend services.
- **API versioning**: The breaking changes in section and field models require incrementing the catalog API minor version (v2.1) with a deprecation notice for v2.0 clients.
- **JSON-LD complexity**: Adding `context[]` to documents means the team must manage JSON-LD context publishing at `schema_url` endpoints.

### Neutral

- No changes to the authentication or authorization model.
- No changes to the compliance_regions table structure.
- The blockchainManager service will consume the new Document fields in a separate task.

---

## 7. Related Decisions

| ADR | Relationship |
|---|---|
| [ADR-0003](0003-multi-tenant-database-design.md) | Tenant isolation mechanisms apply unchanged to v2 schema |
| [ADR-0004](0004-w3c-verifiable-credentials.md) | This ADR operationalizes ADR-0004 at the catalog schema level |
| [ADR-0005](0005-lambda-vpc-blockchain-connectivity.md) | blockchainManager VC issuance will consume new Document fields |

---

## 8. References

- [W3C Verifiable Credentials Data Model v1.1](https://www.w3.org/TR/vc-data-model/)
- [DIF Presentation Exchange 2.0](https://identity.foundation/presentation-exchange/spec/v2.0.0/)
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [OpenID for Verifiable Credential Issuance (OID4VCI)](https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html)
- [W3C Status List 2021](https://www.w3.org/TR/vc-status-list/)
- [EBSI Trusted Schema Registry](https://ec.europa.eu/digital-building-blocks/wikis/display/EBSI/Trusted+Schemas+Registry)
- [SD-JWT — Selective Disclosure for JWTs](https://www.ietf.org/archive/id/draft-ietf-oauth-selective-disclosure-jwt-07.txt)
- [BBS+ Signatures](https://identity.foundation/bbs-signature/draft-irtf-cfrg-bbs-signatures.html)
- [EU ARF — Architecture Reference Framework](https://digital-strategy.ec.europa.eu/en/policies/eudi-wallet-implementation)
