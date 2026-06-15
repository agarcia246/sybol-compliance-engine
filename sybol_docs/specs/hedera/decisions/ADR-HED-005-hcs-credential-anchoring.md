# ADR-HED-005: HCS Credential Anchoring (Topic-per-Credential)
**Status:** Accepted (implemented in POC; refactoring only — no re-decision needed)
**Date:** 2026-04-15 (accepted 2026-04-16)
**Issue:** #199
**Deciders:** Engineering team

## Context
Credentials issued with `did:hedera` benefit from on-ledger anchoring: an immutable, publicly verifiable proof that a specific credential existed at a given point in time. Hedera Consensus Service (HCS) provides ordered, timestamped message streams via topics, making it a natural fit for publishing credential hashes without storing the credential payload on-chain.

The design must balance verifiability, cost, and simplicity. The anchoring strategy also determines how external verifiers locate and check the proof.

## Decision
After issuing a credential with `did:hedera`, publish the SHA-256 hash of the signed JWT to a newly created HCS topic. Each credential gets its own topic; the topic ID serves as the external evidence reference (e.g., in the credential's `evidence` or `termsOfUse` field).

The anchor record is persisted in a new `hedera_credential_anchors` table with the following key columns:

| Column | Type | Description |
|--------|------|-------------|
| `credential_jti` | UUID | JTI of the issued credential |
| `topic_id` | VARCHAR | Hedera topic ID (e.g., `0.0.12345`) |
| `hash` | VARCHAR | SHA-256 hex digest of the signed JWT |
| `sequence_number` | BIGINT | HCS message sequence number |
| `consensus_timestamp` | TIMESTAMP | Hedera consensus timestamp |

## Options Evaluated

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A) Topic per credential (selected)** | Create one HCS topic per issued credential, publish hash as the first message | Individual verification is simple (read one topic, one message); topic ID is a clean external reference; no parsing needed | Higher topic creation cost (~$0.01 per topic); more Hedera entities to manage |
| B) Single topic per tenant | All credential hashes for a tenant go into one shared topic | Fewer topics; lower creation overhead | Verifier must scan all messages to find the right hash; topic grows unbounded; privacy concern (activity volume visible) |
| C) No anchoring (just DID) | Rely solely on the DID document and JWT signature | Simplest implementation; no HCS cost | No on-ledger proof of issuance time; no tamper-evident audit trail; loses a key Hedera value proposition |

## Consequences
- Each `did:hedera` credential issuance incurs one HCS topic creation and one message submission (two Hedera transactions).
- Verifiers can independently confirm a credential's integrity by hashing the JWT and comparing it to the message on the topic.
- The `hedera_credential_anchors` table must be included in the tenant database migration.
- `did:web` credentials are unaffected; anchoring is method-specific and only triggered for `did:hedera`.
- Topic IDs can be included in the credential's metadata, enabling end-to-end verification without contacting the issuer.
