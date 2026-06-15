# ADR-0009: Company DID Resolution from Authenticated Request Context

**Date:** 2026-04-02
**Status:** Proposed
**Authors:** TBD
**Deciders:** TBD

---

## Context and Problem Statement

The wallet-metrics feature requires knowing the set of DID(s) that belong to the calling tenant's company in order to compute two KPIs: the count of credentials where the company acts as holder (`payload->>'sub'` IN company DIDs) and the count of pending presentation requests where the company acts as issuer (`payload->>'iss'` IN company DIDs).

The current `req.auth` object — populated by `requireIdToken` middleware in `businessLogic` — contains `tenantId`, `userRole`, and AWS STS credentials, but no DID field. The Cognito ID token's verified payload includes `custom:tenant_id`, `custom:role`, and `sub` (Cognito user UUID), but no DID claim.

There is therefore a gap between what the authentication context provides and what the KPI queries require. A mechanism must be chosen to bridge this gap without violating the P95 < 200ms latency requirement (NFR-01) or the tenant isolation invariant (BR-03).

---

## Decision Drivers

- FR-12 and FR-13 require an array of the company's DIDs before SQL queries can execute.
- NFR-01 requires P95 < 200ms for `GET /api/bl/activity/metrics`; the DID resolution step must be fast.
- BR-03 prohibits substring matching — only exact DID equality is permitted.
- NFR-40 requires per-tenant DB access via `tenantDatabase.getTenantDbConfig`.
- The resolution must not cross tenant boundaries.
- Cognito custom attributes are the only claim source available at JWT verification time without an additional network call.

---

## Considered Options

### Option A — Add a `custom:did` Cognito Custom Attribute to the ID Token

Configure Cognito to include the tenant's primary DID as a custom attribute (`custom:did`) on the ID token. The `requireIdToken` middleware or `authHelper.verifyJwtSignature` extracts it and adds it to `req.auth.did`. The metrics model uses `[req.auth.did]` as the DID array.

**Pros:**
- Zero additional latency at request time (DID is already in the validated token).
- Cryptographically bound to the token; cannot be spoofed.
- No additional database call required in the metrics flow.
- Simple implementation: extract claim, pass to query.

**Cons:**
- Only provides a single primary DID. If a tenant has multiple DIDs, the token must carry all of them (multivalue custom attribute or a delimited string), which may hit Cognito token size limits.
- Requires a Cognito User Pool attribute change and a re-login cycle for existing users.
- The DID stored in Cognito may become stale if the tenant rotates or adds DIDs without updating the token claim.

---

### Option B — Resolve DIDs from the Per-Tenant Database at Query Time

Add a `tenant_dids` (or equivalent) table or a `did` column to an existing tenant-scoped table. At the start of `getMetrics()`, execute a single `SELECT did FROM tenant_dids WHERE tenant_id = $1` query against the tenant's database, then use the resulting array for the KPI queries.

**Pros:**
- Supports multiple DIDs per tenant without token size constraints.
- DID data is always current (reflects the latest registered DIDs).
- No Cognito schema change required.
- Consistent with the existing per-tenant database pattern.

**Cons:**
- Adds one serial database round-trip before the parallel KPI queries can start, increasing latency.
- Requires defining or identifying which table holds tenant DID registrations (this table may already exist, e.g. as part of DID management, but is not documented in the input spec).
- If the DID table does not yet exist, a new migration is needed.

---

### Option C — Derive DIDs from the `credentials` Table Itself (Issuer Inference)

Infer the company's DID(s) by querying the credentials table for the set of distinct `payload->>'iss'` values present in the tenant's credential records, on the assumption that the company's own issued credentials always carry the company DID as issuer.

**Pros:**
- No additional table or Cognito attribute needed.
- Works within the existing schema.

**Cons:**
- Semantically incorrect: `payload->>'iss'` in the `credentials` table is the issuer DID, which may belong to a different entity (the company might hold credentials issued by third parties).
- Returns an empty set for new tenants with no issued credentials, making KPIs unavailable at onboarding.
- Does not provide the holder DID needed for FR-12 (`payload->>'sub'` matching).
- Fragile: any credential imported from an external issuer would pollute the inferred DID set.

---

## Decision

> **Not yet decided.** This ADR is open. Evaluate the options above and record the decision here.

---

## Consequences

> To be completed once the decision is recorded.

---

## References

- Service Spec §4.1 (FR-11 — Company DID resolution requirement)
- Service Spec §9.1 (Metrics endpoint, DID-dependent queries)
- Service Spec §10.4 (SQL query sketches for FR-12 and FR-13)
- Service Spec §11.5 (DID resolution security note)
- `services/businessLogic/src/utils/authHelper.js` — `verifyJwtSignature()` — shows current JWT claims extracted into `req.auth`
