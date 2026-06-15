# ADR-006: Smart Contract Registry & ABI Management

**Date:** 2026-03-16  
**Status:** Accepted  
**Authors:** IGM  
**Deciders:** IGM

---

## Context and Problem Statement

The bm service interacts with smart contracts by encoding/decoding function calls and event logs using ABI (Application Binary Interface) definitions. Callers reference contracts via a logical identifier (`contractRef`) rather than passing raw ABI and address on every request.

This requires a **contract registry**: a store that maps `contractRef` → `{ address, chainId, ABI, version }`.

Design challenges:
- Multiple tenants may deploy the same contract type at different addresses on different chains.
- Contract ABIs may be versioned (proxy upgrades, multi-version support).
- Contracts may be added or updated without code redeployment.
- ABI parsing must be correct and safe (malformed ABIs could cause encoding errors or unexpected calls).

---

## Decision Drivers

- Ability to register new contracts and update addresses without Lambda redeployment
- Tenant isolation: a tenant's contract registry must not be accessible or modifiable by another tenant
- ABI versioning: support concurrent access to different ABI versions for upgrade scenarios
- Cold-start performance: contract registry lookups must not significantly increase Lambda startup time
- Storage cost and query simplicity
- Auditability of contract registration changes

---

## Considered Options

### Option A — In-code contract registry (bundled JSON)

ABIs and addresses are committed to the Lambda package as JSON files. New contracts or address changes require a code deployment.

- Zero runtime latency (in-bundle)
- Every address or ABI change triggers a full deployment
- Tenant-specific contract deployments cannot be registered dynamically
- Suitable only for a fixed, small set of platform-wide contracts

### Option B — RDS PostgreSQL contract registry table (global Sybol DB)

A `bm_contracts` table in Sybol's **global** PostgreSQL database (not per-tenant). Contains the canonical, versioned catalog of all smart contracts the platform interacts with. Tenants do not hold a local copy; they consume this registry exclusively via the bm service API, which resolves and returns the latest enabled version for a given `contractRef` and `chainId`.

- Fully dynamic: contracts registered or updated centrally without Lambda redeployment
- Single source of truth: all tenants always receive the same, up-to-date ABI and address
- Tenant access controlled at API layer (auth token + tenant context in request), not at DB level
- JSONB stores arbitrarily large ABIs with no item-size constraints
- ABI versioning via the `version` column; `latest` resolved at query time via a DB view
- In-Lambda caching with TTL ensures low-latency repeat lookups
- No per-tenant DB migration required for contract additions or upgrades

### Option C — AWS S3 + metadata in DynamoDB

Contract metadata (address, chainId, version) stored in DynamoDB; ABI JSONs stored as S3 objects. Registry lookup fetches metadata from DynamoDB and retrieves ABI from S3 on cache miss.

- Handles arbitrarily large ABIs without DynamoDB size constraints
- Two-step fetch on cache miss (DynamoDB + S3) adds cold-path latency
- S3 versioning provides built-in ABI history
- More complex implementation than pure DynamoDB

### Option D — SSM Parameter Store (JSON per contract)

One SSM parameter per `contractRef` containing a JSON blob with address, chainId, and ABI.

- Operational simplicity if contract set is small
- Parameter size limited to 8 KB (standard tier) or 8 KB–100 KB (advanced)
- Not designed for tenant-scoped or structured querying
- Difficult to list/enumerate contracts for a given tenant

### Option E — Smart contract registry contract (on-chain)

Deploy a registry smart contract on each chain that stores contract addresses by name. The bm service resolves addresses by calling this registry contract.

- On-chain registry is verifiable and decentralised
- Bootstrap problem: bm must know the registry contract address to query it
- On-chain lookup adds a round-trip RPC call to every operation
- ABI definitions still need an off-chain store
- Suitable only for address resolution, not full ABI management

---

## Decision

Adopt **Option B — RDS PostgreSQL contract registry table (global Sybol DB)**.

The `bm_contracts` table lives in Sybol's global PostgreSQL database. It is the single, authoritative catalog of smart contracts and ABI versions used by the platform. Tenants consume it exclusively through the bm service API — no per-tenant copy exists, and no per-tenant migration is required when a new contract or ABI version is published. This guarantees every tenant always resolves the same canonical address and ABI for a given `contractRef` and `chainId`, eliminating version drift across tenants.

---

## Decision Outcome

**Option B (global Sybol DB, API-consumed) chosen** over the alternatives:

- **Option A rejected**: bundled JSON cannot support runtime registration or address updates; every change requires a full Lambda redeployment and would diverge across deployments.
- **Option C rejected**: S3 + DynamoDB introduces two additional AWS services and a two-step fetch on cache miss. The problem it solves (large ABIs) is already handled by PostgreSQL JSONB.
- **Option D rejected**: SSM Parameter Store has an 8 KB size limit (standard tier), lacks structured querying, and is not designed for versioned enumeration.
- **Option E rejected**: on-chain registry solves only address resolution; ABI definitions still require an off-chain store. The on-chain round-trip adds latency to every operation.

> **Note:** Unlike `bm_chains`, `bm_chain_config`, and `bm_event_subscriptions` (which are per-tenant), the contract registry intentionally lives in the global Sybol DB. Smart contract definitions are platform-managed artefacts, not tenant-owned data. Tenant isolation is enforced at the API layer.

---

## Consequences

### Positive

- Single source of truth: publishing a new contract version propagates to all tenants immediately on the next API call — no per-tenant migration or deployment required.
- Eliminates ABI version drift: every tenant resolves the same `latest` for a given `(contractRef, chainId)`.
- Centralised auditability: all contract registrations, updates, and deprecations are in one place with full history.
- JSONB enables ABI validation, field-level indexing, and future introspection queries.
- In-Lambda cache (TTL-based) keeps hot-path lookups at near-zero latency without DB round-trips per request.
- No per-tenant DB migration needed when adding or upgrading a contract.

### Negative

- Tenant access control moves to the API layer (auth token + tenant context) rather than being implicit from DB isolation; this must be enforced consistently.
- The global DB becomes a dependency for all tenants; a global DB outage affects contract resolution across the platform (mitigated by Lambda in-memory cache covering most read traffic).
- Platform-specific (Sybol-deployed) and tenant-specific contract deployments are not co-located — if a tenant needs a private contract not in the global registry, a separate mechanism is required (out of scope for this ADR).

---

## Implementation Notes

### Schema (PostgreSQL — global Sybol DB)

> This table lives in Sybol's **global** database, separate from the per-tenant tables (`bm_chains`, `bm_chain_config`, `bm_event_subscriptions`). It is managed exclusively by platform engineers; tenants interact with it only through the bm API.

```sql
CREATE TABLE bm_contracts (
  contract_ref  TEXT NOT NULL,             -- logical identifier, e.g. 'SybolCredential'
  version       TEXT NOT NULL,             -- semver string, e.g. '1.0.0'
  chain_id      INTEGER NOT NULL,          -- EVM chain ID (references bm_chains in tenant DBs)
  address       TEXT NOT NULL,             -- checksummed EVM address (EIP-55)
  abi           JSONB NOT NULL,            -- parsed ABI array
  is_proxy      BOOLEAN NOT NULL DEFAULT FALSE,  -- EIP-1967 transparent/UUPS proxy
  impl_ref      TEXT,                      -- contractRef of implementation (if is_proxy)
  deployed_at   BIGINT,                    -- deployment block number (optional)
  enabled       BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (contract_ref, version, chain_id)
);

CREATE INDEX idx_bm_contracts_chain
  ON bm_contracts(chain_id, enabled);

-- Resolves 'latest' as the highest semver-ordered enabled version per (contract_ref, chain_id).
CREATE VIEW bm_contracts_latest AS
  SELECT DISTINCT ON (contract_ref, chain_id)
    contract_ref, version, chain_id, address, abi, is_proxy, impl_ref, deployed_at
  FROM bm_contracts
  WHERE enabled = TRUE
  ORDER BY contract_ref, chain_id, string_to_array(version, '.')::int[] DESC;
```

### API Resolution Model

When a tenant calls `GET /api/bm/contracts/:contractRef/:chainId` (or passes a `contractRef` in a transaction request):

1. Lambda checks the in-memory cache (`contractRef:version:chainId`).
2. On cache miss, queries `bm_contracts_latest` in the global Sybol DB via a **read-only** connection (separate RDS Proxy endpoint from the tenant DB connection).
3. Caches the result for `CONTRACT_CACHE_TTL_SECONDS` (default: 300 s).
4. Returns `{ address, abi, version, chainId }` to the caller.

The Lambda holds **two** DB connections: one to the tenant DB (chain config, event subscriptions) and one read-only connection to the global Sybol DB (contract registry). RDS Proxy is used for both.

### ABI Validation on Registration

Contract registration is a **backoffice platform operation** — write endpoints live in the `backoffice` service (`/api/bo/contracts/...`), consistent with how backoffice already manages other global Sybol DB artefacts (DID documents, billing, KYB). When a contract is published:

1. Parse `abi` with `ethers.Interface.from(abi)` — throws on malformed input.
2. Verify `address` is a valid checksummed EVM address using `ethers.isAddress()`.
3. Reject duplicate `(contract_ref, version, chain_id)` with HTTP 409.
4. Deprecations: set `enabled = FALSE` on old version (soft delete; preserves ABI history).

> `bm` holds no write path to `bm_contracts`. All mutations go through `backoffice`. `bm` only ever performs `SELECT` on this table.

### Proxy Contract Handling (EIP-1967)

- If `is_proxy = TRUE`, set `impl_ref` to the `contract_ref` of the implementation contract.
- At call time, bm resolves the ABI from the implementation (`impl_ref`) but sends the transaction to the proxy `address`.
- Proxy upgrades register a new version on the implementation `contractRef`; the proxy row's `address` remains unchanged.

### Lambda Caching Strategy

- Cache key: `${contractRef}:${version}:${chainId}` (or `latest` in place of version).
- TTL: `CONTRACT_CACHE_TTL_SECONDS` (default: 300 s).
- Cache flush: `POST /api/bm/admin/cache/flush` (IAM-authorised) — shared with ADR-004 flush endpoint.
- Since the registry is global, a flush on any tenant's Lambda instance will refresh its local cache from the same global source.

### Read API — `bm` service (tenant-facing)

```
GET /api/bm/contracts/:contractRef/:chainId          → resolves 'latest' enabled version
GET /api/bm/contracts/:contractRef/:version/:chainId → specific version lookup
GET /api/bm/contracts                                → list all enabled contracts (global catalog)
```

### Write API — `backoffice` service (platform/internal only)

> These endpoints are **not** part of the `bm` service. They are implemented in `services/backoffice`, alongside other global Sybol DB admin operations (DID documents, KYB, billing).

```
POST   /api/bo/contracts
Body:  { contractRef, version, chainId, address, abi, isProxy?, implRef? }
Auth:  platform service token (Cognito admin group or internal IAM)

PATCH  /api/bo/contracts/:contractRef/:version/:chainId
Body:  { enabled }           → deprecate or re-enable a version

GET    /api/bo/contracts     → list all versions including disabled (audit view)
```

---

## References

- [Ethereum ABI Specification](https://docs.soliditylang.org/en/latest/abi-spec.html)
- [AWS DynamoDB item size limits](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ServiceQuotas.html)
- [EIP-1967: Transparent Proxy Standard](https://eips.ethereum.org/EIPS/eip-1967)
- Service Spec §4.4 (Smart Contract Interaction — FR-30 through FR-33), §7.3, §7.4
