# ADR-HED-008: KMS Fallback in DID Validation for W3C-Pure DID Documents
**Status:** Accepted
**Date:** 2026-04-16
**Issue:** #199
**Deciders:** Engineering team

## Context
The Sybol platform introduced two DID documents with slightly different structures:

- `did:web` — served over HTTPS from backoffice. Each `verificationMethod` carries W3C standard fields (`type`, `controller`) plus Sybol-internal fields: `algorithm` (KMS KeySpec, e.g. `ECC_NIST_P256`) and `publicKey` (PEM-encoded SPKI). The Sybol fields feed `JWTCommon.buildJWTHeader()` → `JWKUtils.pemToJwk()` so the JWT header can carry a JWK for self-verifiable credentials.

- `did:hedera` — published as HCS topic messages. The POC implementation embedded only W3C-standard fields (`type`, `publicKeyBase58`) — no `algorithm`, no `publicKey` PEM. Consequently `didValidationUtils.validateIssuerKey()` rejected every `did:hedera` issuer with *"Algorithm not found in verification method"*, blocking credential/presentation signing.

Embedding Sybol-internal fields into HCS-published DID documents was considered and rejected: the documents are immutable once written to HCS consensus, and anchoring internal implementation details on an immutable public ledger couples the on-chain format to a specific server implementation. It also diverges from the `did:hedera` canonical W3C shape.

## Decision
`validateIssuerKey()` treats the Sybol fields as **optional** and resolves them lazily from AWS KMS when missing:

1. If the resolved verification method has `algorithm` and `publicKey` → use them unchanged (did:web backward compatibility — zero behavior change).
2. If either is missing → call `kms:GetPublicKey({ KeyId: fragment })` where `fragment` is the `#fragment` portion of the issuer key:
   - `pkResult.KeySpec` → canonical Sybol algorithm (validated via `keyAlgorithms.fromKeySpec`)
   - `pkResult.PublicKey` (SPKI DER) → PEM encoding (wraps DER base64 in BEGIN/END PUBLIC KEY)

This leans on the Hedera integration's convention that the verification method fragment IS the AWS KMS Key UUID (see commit 8485cb56 "use KMS keyId as DID verificationMethod fragment"). External JWK (Option 2, `publicKeyJwk`) is unaffected because its VM already carries the key material and a self-generated fragment.

## Options Evaluated

| Option | Description | Pros | Cons |
|---|---|---|---|
| **A) Fallback at validation time (selected)** | Keep DID doc W3C-pure; enrich at resolve | Canonical on-chain doc; fixes already-published DIDs without re-publishing HCS messages; KMS is single source of truth for algorithm and key material | Adds one KMS call per validation (cached inside the KMS SDK for the Lambda lifetime) |
| B) Embed Sybol fields in the HCS DID doc | Publish `algorithm` + PEM `publicKey` alongside `publicKeyBase58` | No runtime KMS call | Pollutes the W3C canonical format with implementation details; commits metadata to an immutable log; inconsistent with `did:hedera` spec; any algorithm rotation would require re-publishing every DID |
| C) Tag the KMS key with `jwtAlgorithm: EdDSA` and read the tag | Rely on a KMS tag | Cheap lookup | Duplicates info already in KeySpec; tags can drift from actual KeySpec; does not solve the PEM public key need |
| D) Enrich at resolve time inside `hederaDid.service.resolveDid()` | Return an already-enriched DID doc to every caller | Transparent to downstream code | Couples resolver to KMS semantics; costs a KMS call on every resolution even for read-only callers that don't sign |

Option A balances purity on-chain with cost at the point of need (sign path only).

## Consequences
- `services/businessLogic/src/utils/didValidationUtils.js` depends on `@aws-sdk/client-kms` and the Lambda runtime's default credentials. The IAM role needs `kms:GetPublicKey` (already granted for Hedera signing).
- If the verification method fragment is not a valid KMS Key UUID (e.g., external JWK with a random `kid`), the fallback surfaces a descriptive error: *"Verification method is missing algorithm and publicKey and KMS fallback failed for key {keyId}: {kms error}"*. Callers who bring their own keys must embed `algorithm` + `publicKey` in the VM themselves.
- Already-published `did:hedera` DIDs (e.g. the POC ones) validate correctly after this change without any on-chain re-publish.
- Adds ~50ms to the first sign per cold Lambda (KMS GetPublicKey); subsequent calls are cached by the SDK.
- Unit tests must cover both paths: VM with all fields (did:web) and VM missing fields (did:hedera).

## References
- `services/businessLogic/src/utils/didValidationUtils.js` — implementation
- `services/businessLogic/src/utils/keyAlgorithms.js` — KeySpec validation table (see ADR-HED-006)
- `services/backoffice/src/services/did-document.service.js:130` — did:web DID document builder (reference for the full-featured VM shape)
