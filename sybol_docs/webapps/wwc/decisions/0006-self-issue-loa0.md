# ADR-0006: Self-Issue LoA 0 Decisions

**Status:** Accepted

**Date:** 2026-03-30

**Authors:** dispatcher-agent

**Deciders:** @architect, @tech-lead

---

## Context and Problem Statement

Companies using the WWC webapp can issue credentials to other entities (third-party issuance) or to themselves ("Autoalegar" / self-issuance), where the issuer and the recipient share the same DID and wallet.

Two design decisions needed to be made for the self-issuance path:

1. **What Level of Assurance (LoA) should self-issued credentials carry?**
2. **Should self-issued credentials be propagated to the central node?**

Currently, `levelOfAssurance` is hardcoded to `2` for all credentials, and `propagate()` is called unconditionally — both incorrect for self-issuance.

---

## Decision Drivers

- **Standards compliance**: Self-asserted credentials have LoA 0 by definition in eIDAS / W3C VC trust frameworks.
- **Data integrity**: A credential where issuer === subject cannot be independently verified by a third party, so LoA > 0 would be misleading.
- **Network efficiency**: Propagating a credential to a central node when issuer and recipient share the same wallet is redundant and wastes network resources.
- **Consistency**: The presentation request flow already skips propagation when `iss === sub` (engine.js lines 451-460). Credential issuance must follow the same pattern.
- **Minimal change surface**: The fix must touch only `engine.js`. No backend changes, no new routes, no new dependencies.

---

## Decision 1: Force LoA to 0 for Self-Issued Credentials

### Considered Options

| Option | Description | Verdict |
|--------|-------------|---------|
| A | Keep LoA 2 for all credentials | Rejected — self-asserted credentials cannot be LoA 2; misleads relying parties |
| B | Let the user choose LoA in the UI | Rejected — LoA 0 is not a user preference; it is a structural property of self-assertion |
| C (Chosen) | Force LoA 0 when `isSelf === true` | Accepted — correct by definition; zero UI friction; single-line change |

### Decision

**Chosen: Option C — Force `levelOfAssurance: 0` when `subject.isSelf === true`**

The `isSelf` flag is already set by `useSubjectManager` for the self-issue entry and is available on the subject object. It must be spread into each `claimsToIssue` entry during the subject-crossing loop, and `levelOfAssurance` must be resolved per-entry:

```js
claimsToIssue.push({
  ...entry,
  'recipientDid': subject.did,
  'isSelf': subject.isSelf || false,
  'levelOfAssurance': subject.isSelf ? 0 : 2
});
```

Note: `levelOfAssurance` must be removed from `claimsToIssuePerCustomer` (where it was previously hardcoded to `2`) because it is now subject-dependent.

---

## Decision 2: Skip Propagation for Self-Issued Credentials

### Considered Options

| Option | Description | Verdict |
|--------|-------------|---------|
| A | Always propagate (current behavior) | Rejected — issuer and recipient share the same wallet; propagation is a no-op at best, incorrect at worst |
| B | Propagate but mark as self-issued | Rejected — adds complexity in the central node for no benefit; the credential is already in the local wallet |
| C (Chosen) | Skip `propagate()` when `credentialData.isSelf === true` | Accepted — same pattern as presentation requests; zero backend impact |

### Decision

**Chosen: Option C — Skip `propagate()` when `credentialData.isSelf === true`**

```js
if (!credentialData.isSelf) {
  await propagate(cResponse.signed_token);
}
```

This mirrors the existing self-issuance guard in `createPresentationRequest` (engine.js lines 451-460), which already uses `prResponse.payload.iss !== prResponse.payload.sub` as the propagation gate.

---

## Consequences

### Positive

- Self-issued credentials are correctly tagged as LoA 0, ensuring relying parties are not misled about the trust level.
- No redundant network call to the propagation service for self-issued credentials.
- The implementation is consistent with the existing self-issuance guard in the presentation request path.

### Negative

- Self-issued credentials will never appear in the central node's index. This is intentional, but operators must be aware that these credentials are wallet-local only.

### Neutral

- The backend schema already accepts LoA 0 — no backend changes required.
- The `isSelf` flag was already part of the subject object — no new data structures required.

---

## Implementation

**Only one file changes: `webApps/wwc/src/pages/Catalog/engine.js`**

No new routes, no database migrations, no new dependencies, no backend changes.

Two atomic commits:

1. `feat(wwc): force LoA 0 for self-issued credentials (closes #139 pt.1)` — moves `levelOfAssurance` resolution to the subject-crossing loop and sets it to 0 when `isSelf`.
2. `feat(wwc): skip propagation for self-issued credentials (closes #139 pt.2)` — guards the `propagate()` call with `!credentialData.isSelf`.

---

## Related Decisions

- ADR-0001: AWS Cognito Authentication — session context that provides `myDid` used in self-entry detection
- ADR-0002: W3C / VEIA Dual Standards — LoA 0 aligns with self-asserted tier in the W3C VC trust model
