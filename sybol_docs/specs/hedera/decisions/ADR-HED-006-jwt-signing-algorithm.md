# ADR-HED-006: JWT Signing Algorithm Mapping (Centralized Table)
**Status:** Accepted
**Date:** 2026-04-15 (revised 2026-04-16)
**Issue:** #199
**Deciders:** Engineering team

## Context
The platform issues every signed JWT (Verifiable Credentials, Presentations, Presentation Requests, SD-JWTs, admin tokens) by calling AWS KMS Sign, then embedding the signature in a JWT with a JOSE `alg` header. Three distinct algorithm identifiers must stay in lockstep across the pipeline:

1. **KMS KeySpec** — returned by KMS GetPublicKey and stored in DID documents as `verificationMethod.algorithm` (e.g. `ECC_NIST_EDWARDS25519`, `ECC_NIST_P256`).
2. **JOSE alg** — goes into JWT `header.alg` per RFC 7518 §3.1 (e.g. `EdDSA`, `ES256`, `RS256`).
3. **KMS SigningAlgorithm** — the identifier passed to AWS KMS SignCommand (e.g. `ED25519_SHA_512`, `ECDSA_SHA_256`). Note: `EDDSA` is NOT a valid AWS KMS identifier; Ed25519 keys require `ED25519_SHA_512`.

Signature processing also varies by family: EdDSA returns raw 64-byte signatures (base64url directly); ECDSA returns DER-encoded r|s that must be extracted into fixed-length concatenation; RSA returns raw signatures.

Prior to consolidation this mapping was duplicated in four places (jwtCommon, jwtCredentialManager, selectiveDisclosureManager, tenantKmsService) with inconsistencies — including a latent bug where the Ed25519 branch passed `SigningAlgorithm: 'EDDSA'` which AWS KMS rejects with `ValidationException`.

## Decision
All algorithm mapping is centralized in `services/businessLogic/src/utils/keyAlgorithms.js`:

```js
fromKeySpec('ECC_NIST_EDWARDS25519')
  → { jose: 'EdDSA',  kmsSigningAlgorithm: 'ED25519_SHA_512',
      kmsMessageType: 'RAW',    hashBeforeSign: false, signatureEncoding: 'raw' }

fromJoseAlg('ES256')
  → { jose: 'ES256',  kmsSigningAlgorithm: 'ECDSA_SHA_256',
      kmsMessageType: 'DIGEST', hashBeforeSign: true,  hashAlgorithm: 'sha256',
      signatureEncoding: 'ecdsa-der' }
```

Complete mapping:

| KMS KeySpec | JOSE alg | KMS SigningAlgorithm | MessageType | Hash before sign | Signature encoding |
|---|---|---|---|---|---|
| `ECC_NIST_EDWARDS25519` | `EdDSA` | `ED25519_SHA_512` | `RAW` | no (KMS applies SHA-512) | raw |
| `ECC_NIST_P256` | `ES256` | `ECDSA_SHA_256` | `DIGEST` | yes (SHA-256) | ecdsa-der → r\|s |
| `ECC_SECG_P256K1` | `ES256K` | `ECDSA_SHA_256` | `DIGEST` | yes (SHA-256) | ecdsa-der → r\|s |
| `RSA_2048` / `RSA_4096` | `RS256` | `RSASSA_PKCS1_V1_5_SHA_256` | `DIGEST` | yes (SHA-256) | raw |

Legacy aliases (`Ed25519VerificationKey2020`, `Ed25519VerificationKey2018`) are normalized to `ECC_NIST_EDWARDS25519` before the main lookup, preserving backward compatibility with DID documents that embed W3C type names as `algorithm`.

Consumers:
- `utils/jwkUtils.getJwtAlgorithm()` → delegates to `fromKeySpec().jose` (used by header builders)
- `utils/jwtCommon.buildJWTHeader()` → uses JWKUtils (covers Credentials, Presentations, Presentation Requests)
- `utils/selectiveDisclosureManager` → uses JWKUtils (covers SD-JWTs)
- `lib/tenantKmsService.signJWTWithKeyId()` → uses `fromJoseAlg()` to drive Sign API + encoding
- `lib/tenantKmsService.signJWT()` → same (covers admin-jwt alias path)
- `utils/didValidationUtils.resolveSigningMetadataFromKms()` → uses `fromKeySpec()` to validate KeySpec returned by KMS GetPublicKey

## Options Evaluated

| Option | Description | Pros | Cons |
|---|---|---|---|
| **A) Centralized table (selected)** | Single module exposes KeySpec↔JOSE↔KMS mappings; every signing path delegates | Single source of truth; adding algorithms is one edit; eliminates duplicates and bugs from drift | Small runtime indirection (negligible) |
| B) Duplicated mapping in each consumer | Each module keeps its own switch/map | Minimal up-front effort | Prior state — caused the EDDSA bug; adding algorithms requires multiple edits |
| C) Hardcode branch on header.alg | `if (alg === 'EdDSA') {…} else {…}` | Very simple | Does not scale beyond 2 algorithms; couples SigningAlgorithm to the JOSE branch |

## Consequences
- Adding a new algorithm (e.g. `ML-DSA`, `RS384`) requires a single row in `ALGORITHM_TABLE` — all signers pick it up automatically.
- The signing pipeline is deterministic: `header.alg` and `SigningAlgorithm` can never drift.
- Unit tests must cover every row of the table (round-trip `KeySpec → JOSE → KMS` plus signature encoding).
- Tokens emitted before this ADR with `alg: 'EdDSA'` produced by the broken path never reached KMS successfully, so there is no back-compat concern for signatures in the wild.
- Integration tests must exercise at least one credential per DID method (`did:web` ES256 and `did:hedera` EdDSA) to catch any future regression.
