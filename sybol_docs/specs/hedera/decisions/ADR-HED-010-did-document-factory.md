# ADR-HED-010: DID Document Factory — Centralized DID Document Assembly
**Status:** Proposed
**Date:** 2026-04-16
**Issue:** #199
**Deciders:** Engineering team

## Context
DID document building logic is currently scattered across two services with no shared structure:

- **backoffice** — `services/backoffice/src/services/did-document.service.js` → `createDidDocumentStructure()` builds documents for `did:web`. Includes Sybol-internal fields (`algorithm`, `publicKey` PEM) but does NOT include service endpoints.
- **businessLogic** — `services/businessLogic/src/hedera/hederaDid.service.js` → `buildDidDocument()` builds documents for `did:hedera`. Produces W3C-pure documents with `publicKeyBase58` only.

Neither builder includes `SybolPropagateService` or `EntityProfileService` as service endpoints in the DID document, despite these being part of the platform's identity profile.

This duplication means:
- Adding a new DID method requires writing yet another builder.
- Adding or changing a service endpoint requires edits in multiple places.
- The two builders produce structurally inconsistent documents.

This ADR does NOT re-decide any previously accepted ADR. ADRs 001-003 (method selection, key management, service placement) remain as-is. This is a refactoring decision to consolidate existing, already-implemented logic.

## Decision
Centralize DID document assembly in a `DidDocumentFactory` utility that accepts structured inputs and returns a complete W3C DID document.

**Interface:**

```js
DidDocumentFactory.build({
  method,          // 'did:web' | 'did:hedera'
  did,             // full DID string
  publicKey,       // { type, encoding, value, fragment }
  tenantContext,   // { tenantId, tenantDomain, ... }
  environment,     // 'dev' | 'sta' | 'pro'
  serviceEndpoints // optional override; defaults include SybolPropagateService + EntityProfileService
})
// → W3C DID Document JSON
```

**Key behaviors:**
- Verification method format varies by method: `did:web` includes Sybol-internal fields (`algorithm`, PEM `publicKey`); `did:hedera` emits W3C-pure fields only (`publicKeyBase58`). This preserves ADR-HED-008's design (KMS fallback for W3C-pure docs).
- Service endpoints (`SybolPropagateService`, `EntityProfileService`) are included by default for both methods.
- The factory is a pure function — no signing, no KMS calls, no network I/O.

**Location:** `services/businessLogic/src/utils/didDocumentFactory.js` as an interim placement. May move to a shared library if backoffice also needs it.

## Options Evaluated

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A) Centralized factory in businessLogic utils (selected)** | Single module builds DID docs for all methods | Single source of truth; consistent service endpoints; trivial to add methods | businessLogic dependency for backoffice (acceptable as interim; backoffice can call the API or import the util) |
| B) Keep separate builders per service | Each service maintains its own builder | No cross-service dependency | Current state — duplication, inconsistent docs, no service endpoints in either |
| C) Abstract base class with method-specific subclasses | OO pattern with inheritance | Clean extension point | Over-engineered for two methods; JS class hierarchies add complexity |

## Consequences
- A single module owns the DID document shape — adding `did:key` or any future method is one function addition.
- Service endpoints are guaranteed present in all DID documents.
- Existing `createDidDocumentStructure()` and `buildDidDocument()` are replaced by calls to the factory. Their tests are migrated.
- The factory does not handle signing or publishing — those remain in `did-document.service.js` (backoffice) and `hederaDid.service.js` (businessLogic) respectively.
