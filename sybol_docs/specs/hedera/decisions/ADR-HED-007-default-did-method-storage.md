# ADR-HED-007: Default DID Method Storage
**Status:** Accepted (revised — storage location changed from backoffice entities to tenant DB settings)
**Date:** 2026-04-15 (revised 2026-04-16)
**Issue:** #199
**Deciders:** Engineering team

## Context
With multiple DID methods available (`did:web`, `did:hedera`), the system needs a way to determine which method to use when the caller does not explicitly specify an `issuerKey` in a credential or presentation request. Each tenant should be able to configure their preferred default method.

The storage location for this preference must be:
- Easy to query at credential-issuance time (low latency, no extra service calls).
- Consistent with existing tenant configuration patterns.
- Modifiable by backoffice administrators.

**Update (2026-04-16):** The original decision placed the setting in `backoffice.entities` as a new column. During implementation it was moved to `tenant_settings` in the tenant database, exposed via `GET/POST /api/bl/settings`. This is more consistent with other tenant-level preferences already stored there and avoids coupling identity configuration to the backoffice entities table. The setting is read/written through the existing settings API (`/api/bl/settings`), not a dedicated endpoint.

## Decision
~~Store the tenant's default DID method in the existing `backoffice.entities` table as a new column.~~

**Revised decision:** Store the tenant's default DID method in the `tenant_settings` table within the tenant's own database, accessible via `/api/bl/settings`.

When `issuerKey` is not explicitly provided in a credential or presentation request, the system:

1. Reads `default_did_method` from `tenant_settings` via `/api/bl/settings`.
2. Resolves the tenant's DID document for that method.
3. Uses the first `verificationMethod` from the resolved document as the signing key.

This preserves full backward compatibility: existing tenants default to `did:web` with no action required.

## Options Evaluated

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A) Column in entities table | Add `default_did_method` to `backoffice.entities` | Already queried during issuance; single migration | Couples DID config to a general-purpose backoffice table; mixes concerns |
| **B) tenant_settings in tenant DB (selected)** | Store as a key-value pair in `tenant_settings`, exposed via `/api/bl/settings` | Consistent with existing tenant preferences pattern; no cross-DB dependency; uses existing settings API | Requires tenant DB to be available at issuance time (already the case) |
| C) Cognito custom attribute | Store the preference as a custom attribute on the Cognito user pool | No database migration needed | Token size limits (per ADR-0009 analysis); stale until token refresh; not tenant-level (user-level); requires Cognito admin API call to update |

## Consequences
- The `default_did_method` setting lives in `tenant_settings` alongside other tenant preferences — no backoffice schema change needed.
- Read/write via `GET/POST /api/bl/settings` — the same API tenants already use for other configuration.
- Credential issuance logic adds a fallback path: if no `issuerKey` is provided, resolve via the default method.
- Existing API contracts are unaffected; `issuerKey` remains an optional explicit override.
- Default value is `'did:web'` — existing tenants with no explicit setting behave identically to before.
