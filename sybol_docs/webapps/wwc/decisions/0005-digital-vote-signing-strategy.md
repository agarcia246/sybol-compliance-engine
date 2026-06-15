# ADR-0005: Digital Vote Signing Strategy

**Status:** Proposed

**Date:** 2026-03-12

**Authors:** frontend-architect-agent

**Deciders:** @architect, @security-lead, @tech-lead

> ⚠️ `TEMPORARY-NONSTANDARD` — This ADR was authored manually because the `create_adr_file` tool was not available in the current environment. Replace with tool-generated artifact when available.

---

## Context and Problem Statement

The voting system requires that each vote be digitally signed before submission to guarantee non-repudiation and authenticity. The signed vote payload must be attributable to the voter's digital identity and verifiable by the backend.

The application already has a mechanism for digital signing: `blockchain.helper.sign(credentials, verification)`, which:
- Uses `sessionStorage.privateKey` or `sessionStorage.jwk` (P-256 ECDSA key pair)
- Signs a VP (Verifiable Presentation) JWT using ES256
- Returns a signed JWT string

**Question:** Should the voting module reuse the existing `blockchain.helper.sign()` mechanism for vote signing, or introduce a dedicated signing implementation?

---

## Decision Drivers

- **Consistency**: The application already has an established signing mechanism used for credential presentations
- **Non-repudiation**: Each vote must be attributable to a specific DID and verifiable independently
- **Security**: Unsigned votes must be rejected; the signing step must be a blocking gate before submission
- **No new dependencies**: Introducing a new signing library requires security review, adding time and risk
- **Private key availability**: The existing signing mechanism depends on keys in `sessionStorage`, which are set during the identity verification / credential flow

---

## Considered Options

### Option A: Create a Dedicated Vote Signing Utility

Implement a new signing function specifically for votes, separate from `blockchain.helper.sign()`.

**Pros:**
- ✅ Could be designed specifically for vote payload structure
- ✅ Decoupled from credential signing

**Cons:**
- ❌ Introduces a new signing implementation requiring independent security review
- ❌ Duplicates cryptographic logic already vetted in `blockchain.helper.js`
- ❌ Two signing implementations for the same key pair increases maintenance burden
- ❌ No clear benefit over reusing the existing implementation

### Option B: Submit Unsigned Votes and Rely on Backend Signature Verification Only

Skip frontend signing. Send the raw vote payload. Backend verifies via its own mechanisms.

**Pros:**
- ✅ Simpler frontend implementation
- ✅ No dependency on `sessionStorage` key availability

**Cons:**
- ❌ Violates the stated business requirement: "votes must be digitally signed before submission"
- ❌ Eliminates non-repudiation at the frontend layer
- ❌ A vote could technically be submitted by any authenticated session, not only the key holder
- ❌ Backend cannot distinguish a signed vote from an unsigned one without an additional challenge mechanism

### Option C (Chosen): Reuse `blockchain.helper.sign()` Without Modification

Use the existing `blockchain.helper.sign()` function as-is to sign the vote payload before submission. Gate the transition from `CONFIRMING_VOTE` to `SIGNING_VOTE` on key availability. Only proceed to `SUBMITTING_VOTE` if signing succeeds.

**Pros:**
- ✅ No new signing library or cryptographic implementation required
- ✅ Same key pair used for identity and voting — consistent identity model
- ✅ Already tested in the application context
- ✅ Backend already knows how to verify ES256 VP JWTs from this mechanism
- ✅ Error path is well-understood: if `sign()` throws, enter `VOTE_ERROR`

**Cons:**
- ❌ Depends on `sessionStorage.privateKey/jwk` being available — if not populated, voting fails at signing step
- ❌ The signing function was designed for credential presentations, not votes — payload structure may need adaptation

---

## Decision

**Chosen: Option C — Reuse `blockchain.helper.sign()` Without Modification**

The existing signing mechanism is production-capable, security-reviewed, and uses the same cryptographic identity that was verified during the identity verification step. Introducing a new signing implementation for votes provides no security benefit and adds unnecessary complexity.

The signed vote is submitted as `signedVoteJwt` in the `VoteSubmission` payload. The backend must verify this signature independently.

---

## Implementation Constraints

1. **Key availability gate**: Before entering `SIGNING_VOTE` phase, `useVotingBooth` must verify that `sessionStorage.privateKey` or `sessionStorage.jwk` is truthy. If neither is present, enter `VOTE_ERROR` with error code `KEY_NOT_AVAILABLE` and a friendly message directing the user to re-authenticate.

2. **No pre-signing**: The vote payload (containing `optionId`, `electionId`, `voterDid`, and timestamp) must NOT be signed until the user has explicitly confirmed their choice in the `CONFIRMING_VOTE` phase.

3. **No persistence of signed payload**: The `signedVoteJwt` must live only in the `useVotingBooth` state during the `SUBMITTING_VOTE` phase. It must not be written to `localStorage`, `sessionStorage`, or any external store.

4. **Submission gate**: `submitVote()` in `voting.js` must never be called if `signedVoteJwt` is null or empty.

5. **Backend responsibility**: Frontend signing does not replace backend signature verification. The backend must independently verify the `signedVoteJwt` before recording the vote.

---

## Assumptions Pending Confirmation

- `A-001`: `sessionStorage.privateKey` or `sessionStorage.jwk` is reliably populated after identity verification. If this is not the case, a key provisioning step must be added to the voting flow before `SIGNING_VOTE`.

---

## Related Decisions

- ADR-0001: AWS Cognito Authentication — session context that provides user identity
- ADR-0002: W3C / VEIA Dual Standards — credential resolution used in identity verification step upstream of signing
- ADR-0004: Voting Module Two-Track Architecture — companion ADR
