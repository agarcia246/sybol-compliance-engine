# ADR-HED-011: Identity Object Payload Builders — Isolated Payload Construction
**Status:** Proposed
**Date:** 2026-04-16
**Issue:** #199
**Deciders:** Engineering team

## Context
JWT payload construction for identity objects (Verifiable Credentials, Verifiable Presentations, Presentation Requests) is currently embedded inside manager classes (`jwtCredentialManager`, `jwtPresentationManager`, etc.) interleaved with signing logic, KMS calls, and database operations. This makes it difficult to:

- **Read** — the complete JSON structure of a VC or VP is not visible at a glance; fields are scattered across conditionals and helper calls.
- **Test** — testing the payload shape requires mocking KMS, DB, and other side effects.
- **Reuse** — the same payload structure cannot be used with a different signing backend without duplicating the construction code.

This ADR does NOT re-decide any previously accepted ADR. It is a refactoring decision to separate payload construction from signing.

## Decision
Extract payload construction into pure-function builders, each in its own file:

| Builder | File | Input → Output |
|---------|------|----------------|
| `createCredentialPayload` | `utils/payloads/credentialPayload.js` | `(issuerDid, subjectDid, claims, metadata)` → W3C VC 2.0 JSON |
| `createPresentationPayload` | `utils/payloads/presentationPayload.js` | `(holderDid, credentials, metadata)` → W3C VP 2.0 JSON |
| `createPresentationRequestPayload` | `utils/payloads/presentationRequestPayload.js` | `(verifierDid, requestedClaims, metadata)` → JSON |

**Key design principles:**
- **Pure functions** — no side effects, no KMS, no DB, no network. Input in, JSON out.
- **Self-documenting** — opening the file shows the complete JSON structure at a glance with all fields and their sources.
- **Signing stays in the service layer** — managers call the builder to get the payload, then pass it to `jwtCommon.signJWTPayload()` or equivalent.
- **W3C compliance** — VC and VP payloads conform to W3C Verifiable Credentials Data Model 2.0.

**Location:** `services/businessLogic/src/utils/payloads/` directory.

## Options Evaluated

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A) Isolated builder files (selected)** | One pure function per payload type in its own file | Maximum readability; trivially testable; clean separation of concerns | More files to navigate (acceptable — each is small and focused) |
| B) Keep construction in managers | Current state — payload built inline with signing | Fewer files | Hard to read, test, or reuse; payload shape buried in control flow |
| C) Single payloadBuilder module with multiple exports | One file with all builders | Fewer files than Option A | File grows large; harder to review in PRs; less focused |

## Consequences
- Each builder file serves as living documentation of the payload format — new developers can read the structure without tracing through manager code.
- Unit tests for payload shape require zero mocks — just call the function and assert on the output.
- Manager classes become thinner: build payload → sign → persist/return.
- Existing tests that assert on credential/presentation structure are migrated to test the builders directly.
- No behavioral change to API consumers — the signed JWTs contain the same payloads as before.
