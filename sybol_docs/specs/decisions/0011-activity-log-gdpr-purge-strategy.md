# ADR-0011: Activity Log GDPR Purge Strategy

**Date:** 2026-04-02
**Status:** Proposed
**Authors:** TBD
**Deciders:** TBD

---

## Context and Problem Statement

The `activity_log` table (FR-20) stores structured audit events per-tenant indefinitely by default. GDPR Article 5(1)(e) (storage limitation) and the Sybol platform's 24-month data retention policy (NFR-60) require that entries older than 24 months be purgeable without manual SQL intervention by an engineer.

The purge strategy choice has a direct impact on the `activity_log` DDL: a TTL column approach requires an additional column; a partitioning approach requires `PARTITION BY RANGE (created_at)` in the `CREATE TABLE` statement; an external job approach requires no schema change but relies on operational discipline.

Because the migration must be additive and idempotent (BR-08), and because the table DDL cannot easily be changed after it is deployed across all tenant databases, the purge strategy must be decided before the migration is merged.

---

## Decision Drivers

- NFR-60: Entries older than 24 months must be purgeable without manual SQL.
- NFR-61: The mechanism must not expose PII beyond the audit minimum.
- BR-08: The migration must be additive and idempotent; the DDL cannot be destructively modified after deployment.
- Delivery constraint: no new Lambda functions or infrastructure in this feature's scope — however, a scheduled purge Lambda could be introduced as a companion operation if the team accepts the scope expansion.
- The number of `activity_log` rows per tenant may grow significantly if auto-logging hooks (FR-27) fire on every credential, presentation, contact, and request operation.

---

## Considered Options

### Option A — Scheduled Lambda with a `purge_after` TTL Column

Add a `purge_after TIMESTAMPTZ` column to `activity_log` (defaulting to `NOW() + INTERVAL '24 months'`). A scheduled EventBridge rule triggers a Lambda function (or the existing `businessLogic` Lambda via a management route) that executes `DELETE FROM activity_log WHERE purge_after < NOW()` across all tenant databases.

**Pros:**
- Fine-grained control: individual entries can have custom retention periods.
- The purge job can be rate-limited to avoid heavy DB load.
- Clear audit trail: `purge_after` is visible and queryable.

**Cons:**
- Adds a column to the DDL that must be included in the migration before the first deployment.
- Requires a scheduled Lambda (or equivalent trigger), which is a scope expansion from the current delivery constraint.
- DELETE on large tables can be slow and locks rows; requires batching logic.

---

### Option B — Table Range Partitioning by Month (`PARTITION BY RANGE (created_at)`)

Create `activity_log` as a partitioned table with monthly child partitions. Purging is done by `DROP TABLE activity_log_YYYY_MM` for partitions older than 24 months, which is instantaneous and lock-free.

**Pros:**
- Purge is instant and lock-free (partition drop vs. row-level DELETE).
- Query performance benefits from partition pruning when `created_at` filters are applied.
- No purge-specific column needed in the DDL.

**Cons:**
- Partitioned tables require PostgreSQL 10+ and specific DDL syntax; child partitions must be created in advance or via a partition management extension (e.g., `pg_partman`).
- The initial `CREATE TABLE` syntax changes significantly; this is a harder migration to write correctly.
- Each tenant database needs partition management, adding operational complexity.
- `pg_partman` or equivalent must be available in all tenant database environments.

---

### Option C — External DBA/Infrastructure-Managed Purge Job (No Schema Change)

Accept the existing schema as-is (no TTL column, no partitioning). Document the 24-month retention requirement and rely on a periodic DBA-executed or infrastructure-managed script (e.g., AWS RDS scheduled maintenance, a one-off DBA job, or a Terraform-managed scheduled query). The SPEC flags the obligation; enforcement is an operational process.

**Pros:**
- Zero schema impact; the migration file is simpler.
- No scope expansion in the current delivery.
- Flexibility to choose the purge mechanism later when operational patterns are better understood.

**Cons:**
- Does not satisfy NFR-60 ("without manual SQL intervention") if the process requires a DBA each time.
- Operational discipline risk: if the scheduled process is not set up correctly, data accumulates indefinitely.
- Leaves GDPR compliance dependent on a process rather than a technical control.

---

## Decision

> **Not yet decided.** This ADR is open. Evaluate the options above and record the decision here.

---

## Consequences

> To be completed once the decision is recorded. Note that the decision will directly influence the `activity_log` DDL in the migration file. If Option A is chosen, the `purge_after` column must be added to the migration before it is applied to any tenant database. If Option B is chosen, the `CREATE TABLE` statement must be rewritten with `PARTITION BY RANGE`. If Option C is chosen, the migration remains as written in §10.1 of the SPEC and a separate operational runbook must be produced.

---

## References

- Service Spec §4.2 (FR-20 — activity_log table definition)
- Service Spec §6.7 (NFR-60, NFR-61 — GDPR compliance requirements)
- Service Spec §10.1 (DDL for activity_log including current schema without purge column)
- Service Spec §10.5 (migration strategy — additive, idempotent)
