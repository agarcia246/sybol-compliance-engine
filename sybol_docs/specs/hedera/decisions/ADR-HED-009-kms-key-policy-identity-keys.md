# ADR-HED-009: KMS Key Policy for Tenant Identity Keys
**Status:** Accepted
**Date:** 2026-04-16
**Issue:** #199
**Deciders:** Engineering team

## Context
AWS KMS enforces access via two layers: the IAM policy of the caller AND the key policy attached to the KMS key itself. Both must grant the operation.

Before this ADR, the unified `sybol-kms-keys` Lambda created identity keys with the default AWS key policy — only root has access (`Principal: root`, `Action: kms:*`). Other principals (including any IAM role) cannot invoke `kms:Sign` on such a key without an explicit key policy grant.

The Sybol businessLogic service signs JWTs by assuming the per-tenant admin role (`TenantRole-{tenantId}-admin`) via STS based on the Cognito identity pool, then invoking KMS with those credentials. This worked for legacy did:web keys (e.g. `5a38b335-...` for repsol) because their key policy had a hand-crafted `TenantRoleAccess` statement granting `kms:Sign / kms:GetPublicKey / kms:DescribeKey` to the admin role. It failed for the first `did:hedera` key provisioned through the unified Lambda: `kms:Sign` returned `AccessDeniedException`, surfacing to the end user as *"Access denied to KMS key {id}. Verify tenant permissions."*.

## Decision
`lambdas/kms-keys/src/operations/create.js` now builds and attaches a key policy at creation time via a new `buildKeyPolicy({ accountId, tenantId, purpose })` helper:

```json
{
  "Version": "2012-10-17",
  "Id": "key-default-1",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::{accountId}:root" },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "TenantRoleAccess",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::{accountId}:role/TenantRole-{tenantId}-admin" },
      "Action": ["kms:Sign", "kms:GetPublicKey", "kms:DescribeKey"],
      "Resource": "*"
    }
  ]
}
```

`TenantRoleAccess` is included only when `purpose === 'identity'`. For `purpose === 'blockchain'` only the root statement is attached — the blockchain signing path is not yet implemented and the appropriate grantee will be decided when that flow is built.

Requires the `AWS_ACCOUNT_ID` environment variable on the Lambda (already present) so the ARNs can be constructed without a runtime STS call.

## Options Evaluated

| Option | Description | Pros | Cons |
|---|---|---|---|
| **A) Bake key policy at creation (selected)** | CreateKeyCommand includes the full policy | Atomic: new keys are signable from day one; no follow-up step | Policy logic lives in the KMS Lambda; changing grantees requires a Lambda deploy (acceptable — this is a platform decision, not a per-tenant one) |
| B) PutKeyPolicy post-creation | Create the key, then update the policy separately | Keeps CreateKey minimal | Non-atomic: a crash between the two calls leaves orphan keys with default policy; doubles API calls and failure modes |
| C) Rely solely on IAM identity-based policies | Grant `kms:Sign` on tagged resources via IAM | Fewer moving parts at key creation | KMS enforces *both* policies — the key policy must still allow the principal. Identity-based only is insufficient for non-root principals. |
| D) Use Grants instead of key policy | `CreateGrant` per role | Supports revocation without policy edits | Harder to audit; adds a per-key artefact; more operational complexity for no current benefit |

## Consequences
- All new identity keys created after this ADR are signable by their tenant's admin role without follow-up IAM or policy work.
- Legacy keys predating the change must have their key policy patched manually (one-off `PutKeyPolicy`). Applied retroactively to `9203b99b-8455-4fff-b653-92bec0d0d8d0` (repsol Hedera) on 2026-04-16.
- The tenant role ARN (`TenantRole-{tenantId}-admin`) is a naming contract. If this is ever renamed, the Lambda's `buildKeyPolicy` plus every legacy key needs updating.
- When multi-role signing is introduced (e.g. a `signer` role distinct from `admin`), extend `buildKeyPolicy` to include both principals. No schema change needed.
- When rotation lands (#206), the rotation path must either preserve the key policy when re-keying or call `buildKeyPolicy` again.
- KMS Key policies are capped at 32 KB — plenty of headroom for additional role grants.

## References
- `lambdas/kms-keys/src/operations/create.js` — `buildKeyPolicy` and `CreateKeyCommand` integration
- [AWS KMS — Access control overview](https://docs.aws.amazon.com/kms/latest/developerguide/control-access-overview.html)
- [AWS KMS — CreateKey Policy parameter](https://docs.aws.amazon.com/kms/latest/APIReference/API_CreateKey.html#KMS-CreateKey-request-Policy)
- ADR-HED-002 (Key Management) — background on Ed25519 in KMS for Hedera
