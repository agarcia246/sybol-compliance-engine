# ADR-004: Multi-Chain Abstraction & Chain Registry Design

**Date:** 2026-03-16  
**Status:** Accepted  
**Authors:** IGM  
**Deciders:** IGM

---

## Context and Problem Statement

The bm service must support multiple EVM-compatible chains (e.g. Ethereum, Polygon, Base, Sepolia testnet) and route each operation to the correct chain at runtime. Different tenants may operate on different chains, and the set of supported chains may grow over time.

This decision defines how chain metadata and per-chain configuration is stored, accessed, and updated without code deployments — the **Chain Registry** pattern.

Chain configuration includes: chain ID, RPC endpoint(s), native currency, block time, EIP-1559 support flag, confirmation threshold, and explorer URL.

The choice affects:
- How new chains are onboarded without redeployment
- How tenant-to-chain mappings are managed
- The operational path for changing RPC URLs (e.g. rotating API keys)
- Startup latency in Lambda (config loading on cold start)

---

## Decision Drivers

- Add new chains without Lambda redeployment or code changes
- Operational ease of rotating RPC URLs or API keys
- Lambda cold start performance (config loading must be fast)
- Tenant-level chain scoping (a tenant may only operate on a subset of chains)
- Consistency: all Lambda instances must see the same chain config at a given time
- Auditability of config changes

---

## Considered Options

### Option A — Environment variables + Lambda redeployment

Chain configs are hardcoded as environment variables or bundled JSON in the Lambda package. Adding or modifying a chain requires a code/deployment change.

- Zero runtime overhead (no external config fetch)
- Cannot add chains without a deployment pipeline run
- Operational change (RPC key rotation) requires a full deployment lifecycle
- Not suitable for dynamic multi-tenant use cases

### Option B — AWS Systems Manager Parameter Store

Chain configs stored as SSM parameters (JSON objects per chain). Lambda loads on cold start with in-memory caching.

- Config changes without code deployments (SSM console or API)
- Fine-grained IAM access control per parameter
- Low cost; well-integrated with Lambda
- SSM SDK calls add cold-start latency (mitigated by caching)
- No versioning beyond SSM's built-in history

### Option C — AWS RDS PostgreSQL chain registry

A PostgreSQL table (on the existing Sybol RDS instance) stores chain configurations and tenant-to-chain mappings. Lambda queries on cold start with TTL-based in-memory cache, reusing the existing database connection layer shared with other services.

- Relational schema allows rich querying: tenant-to-chain mappings, chain metadata, RPC endpoints, and signer references can be joined in a single query
- Reuses the existing RDS infrastructure and connection pool already in use by other Sybol services — no new data store to operate
- Full SQL versioning and migration tooling (consistent with the rest of the platform)
- Supports transactional updates: atomically add a chain and its tenant mappings in one operation
- Lambda cold start requires a DB connection (mitigated by RDS Proxy and in-memory caching after first load)
- RDS Proxy recommended to manage connection pooling under Lambda concurrency
- Slightly higher cold-start latency than SSM on cache miss, but acceptable with RDS Proxy and warm Lambda instances

### Option D — Dedicated config service / API

A separate internal HTTP service provides chain configuration. bm fetches and caches it at startup.

- Centralised config management across all services
- Adds a network dependency on the critical path for cold starts
- Introduces another service to operate and monitor
- Overkill unless config is shared across many services

### Option E — AWS AppConfig

Stores chain config as AppConfig hosted configurations with deployment strategies, rollback, and validators.

- Built-in deployment/rollback for config changes
- Suitable for config that changes rarely but must be managed carefully
- More operational overhead to set up than SSM or DynamoDB
- Integrates with Lambda Extensions for low-latency access

---

## Decision

Adopt **Option C — AWS RDS PostgreSQL** as the chain registry and tenant-to-chain mapping store.

Chain configurations, RPC endpoint references, and tenant-to-chain mappings are stored in the existing Sybol RDS PostgreSQL instance, reusing the shared database infrastructure already in place. Lambda loads and caches the full registry on cold start; cache entries are refreshed on a configurable TTL or on an explicit cache-bust signal.

---

## Decision Outcome

Option C is selected for the following reasons:

- **Option A** was rejected because every chain addition or RPC URL rotation requires a code deployment, which is operationally unacceptable for a multi-tenant platform that must onboard chains dynamically.
- **Option B (SSM)** is suitable for simple key-value config but lacks relational querying, making it awkward to model tenant-to-chain mappings and cross-reference signer records. It also requires a separate store for the signer registry (ADR-003), increasing operational surface.
- **Option D** introduces a new service dependency on the cold-start critical path with no benefit at current scale.
- **Option E (AppConfig)** adds deployment strategy overhead that is disproportionate for configuration that changes infrequently and does not need staged rollout.
- Option C reuses the existing RDS instance already operated by the platform, avoiding a new data store. PostgreSQL's relational model naturally handles chain configs, tenant-to-chain scoping, RPC endpoints (primary + fallback per ADR-002), and signer references (per ADR-003) in a single, queryable schema. SQL migrations ensure all changes are versioned and auditable, consistent with the rest of the Sybol services.

---

## Consequences

### Positive

- No new data store: reuses the existing RDS PostgreSQL instance and connection tooling.
- Relational schema enables efficient joined queries: chain config + tenant mappings + RPC endpoints + signer refs in a single round-trip.
- SQL migrations (consistent with the platform) provide full auditability and rollback capability for config changes.
- Transactional writes: onboarding a new chain and its tenant mappings is atomic.
- RDS Proxy handles Lambda concurrency connection pooling, preventing connection exhaustion under high Lambda fan-out.
- In-memory caching in Lambda eliminates per-request DB round-trips after cold start.

### Negative

- Cold-start latency on cache miss requires a DB connection via RDS Proxy — slightly higher than SSM or AppConfig Extensions for pure config reads.
- RDS availability SLA applies: if RDS is unavailable and the Lambda cache has expired, chain config cannot be refreshed (mitigated by a generous TTL and warm Lambda instances).
- Schema migrations must be coordinated across the platform; chain registry schema changes go through the standard migration pipeline.
- Connection to RDS requires VPC configuration for Lambda (VPC-attached Lambda with appropriate security groups and subnet routing).

---

## Implementation Notes

### Schema (PostgreSQL)

> Each tenant database receives its own copy of these tables. There is no `tenant_id` column — isolation is achieved at the database level, consistent with Sybol's multi-tenant model (`docs/architecture/multi-tenancy.md`).

```sql
-- Global chain catalogue (seeded once per tenant DB via onboarding migration).
-- Contains immutable EVM chain specs and RPC routing config.
CREATE TABLE bm_chains (
  chain_id            INTEGER PRIMARY KEY,       -- EVM chain ID (e.g. 1, 137, 11155111)
  name                TEXT NOT NULL,             -- Human-readable name
  native_currency     TEXT NOT NULL,             -- e.g. 'ETH', 'MATIC'
  block_time_ms       INTEGER NOT NULL,          -- Approximate block time in ms
  eip1559             BOOLEAN NOT NULL DEFAULT TRUE,
  confirmation_blocks INTEGER NOT NULL DEFAULT 2,
  explorer_url        TEXT,
  critical            BOOLEAN NOT NULL DEFAULT FALSE, -- Drives RPC routing (ADR-002)
  rpc_primary         TEXT,                      -- Internal VPC RPC URL (self-hosted)
  rpc_fallback_ref    TEXT,                      -- Secrets Manager path for managed provider URL
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Per-tenant chain activation and signer assignment.
-- One row per chain the tenant has enabled; omission means the chain is inactive.
CREATE TABLE bm_chain_config (
  chain_id   INTEGER PRIMARY KEY REFERENCES bm_chains(chain_id),
  signer_ref TEXT NOT NULL,                   -- References signer registry (ADR-003)
  enabled    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Seeding strategy:** The `bm_chains` catalogue is populated by a shared seed migration applied during tenant onboarding (`infraestructure/ClientInfra`). Chain additions are distributed as new migration versions across all tenant DBs.

### Lambda Caching Strategy
- On cold start, JOIN `bm_chains` with `bm_chain_config` (enabled only) and load the result into a module-level in-memory map. Since the Lambda already connects to the tenant's own DB, no tenant filtering is needed.
- Cache TTL: configurable via `CHAIN_CACHE_TTL_SECONDS` environment variable (default: 300 seconds).
- Cache invalidation: a `POST /api/bm/admin/cache/flush` internal endpoint (IAM-authorised) forces a reload on the next request.
- RDS Proxy endpoint must be used for the Lambda DB connection string to avoid connection exhaustion under high concurrency.

### RPC URL Resolution
- `rpc_primary`: stored in plaintext (internal VPC URL, no secret material).
- `rpc_fallback_ref`: a Secrets Manager path; the actual URL is fetched at Lambda cold start and cached alongside chain config. RPC API keys never stored in the DB.

### Operational Notes
- Chain catalogue changes (add chain, rotate RPC URL) are SQL migrations distributed to all tenant DBs via the standard migration pipeline.
- Per-tenant activation (`bm_chain_config`) is managed through the tenant onboarding flow or backoffice API; no Lambda redeployment required.
- Cache flush after a config change takes effect within TTL on all warm Lambda instances.
- `critical` flag in `bm_chains` drives the RPC routing policy defined in ADR-002.

---

## References

- [AWS SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
- [AWS AppConfig](https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html)
- [EVM Chain IDs (chainlist.org)](https://chainlist.org/)
- Service Spec §4.1, §8, §11 (Configuration)
- `docs/architecture/multi-tenancy.md`
