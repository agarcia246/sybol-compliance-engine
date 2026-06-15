# ADR-0010: Wallet Metrics Trend and Change Baseline Strategy

**Date:** 2026-04-02
**Status:** Proposed
**Authors:** TBD
**Deciders:** TBD

---

## Context and Problem Statement

The wallet-metrics KPI response shape (FR-16, §9.1) requires each non-placeholder KPI to carry a `trend` field ("up" | "down" | "neutral") and a `change` field (integer delta compared to the same 30-day window in the prior period). For example, if the tenant had 39 credentials last month and 42 today, `change = 3` and `trend = "up"`.

Computing these values requires a baseline — a count of the same entity at a prior point in time. The `credentials`, `presentation_requests`, and `contacts` tables contain `is_deleted` flags and status tables with timestamps, but do not carry a created-at timestamp on the main credential row that is universally available and reliable for windowed counting.

A strategy must be chosen that is both accurate and compatible with the P95 < 200ms latency target (NFR-01), given that the metrics endpoint already issues four parallel queries.

---

## Decision Drivers

- NFR-01: P95 < 200ms for the full metrics response.
- FR-16: `trend` and `change` must reflect a 30-day delta vs the prior 30-day period.
- FR-18: All KPI queries run in parallel; the baseline query must not add a serial step.
- The feature must not require infrastructure changes (NFR: no new Lambda or infra).
- Accuracy: the baseline approach should reflect real business state, not an approximation.

---

## Considered Options

### Option A — Two-Window COUNT in a Single SQL Query per KPI

For each KPI, issue a single SQL query that computes both the current-period count and the prior-period count in one statement using conditional aggregation or CTEs with time-window filters (e.g., `CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END`).

This requires a `created_at` timestamp on the main tables (`credentials.created_at`, etc.) or on the status tables. The `credential_status.created_at` and `presentation_request_status.created_at` columns already exist.

**Pros:**
- No additional tables or infrastructure.
- Single query per KPI; fits within the existing parallel `Promise.all` structure.
- Accurate if timestamp columns are reliable.

**Cons:**
- Increases query complexity; each KPI query becomes a multi-CTE statement.
- The `credentials` table schema as provided does not show a `created_at` column on the main row; the baseline would need to be derived from the earliest `credential_status` entry, which may not equal creation time.
- May approach or exceed the latency budget on large datasets.

---

### Option B — Defer Trend/Change to a Future Iteration (Return Null for Now)

For the initial delivery, return `"trend": "neutral"` and `"change": null` for all non-placeholder KPIs, and ship the `value` counts as the primary deliverable. Document trend/change as a planned enhancement and address the baseline strategy separately.

**Pros:**
- Eliminates all baseline complexity from the initial delivery.
- Guarantees the P95 latency target (simpler queries).
- Unblocks the frontend from consuming real `value` data immediately.

**Cons:**
- Dashboard UI that depends on trend arrows will show "neutral" for all KPIs at launch.
- Requires a follow-up ADR and implementation sprint to add trend/change later.
- Does not fully satisfy FR-16 as written.

---

### Option C — Snapshot Table with Scheduled Capture

Introduce a `metrics_snapshot` table (per-tenant) that stores the KPI counts at regular intervals (e.g., every 24 hours via an EventBridge + Lambda scheduler). The metrics endpoint reads the most recent snapshot for the "prior period" baseline and computes `change = current - snapshot_value`.

**Pros:**
- Baseline lookup is a trivial indexed SELECT; near-zero latency impact.
- No complex window queries; current-period count remains the simple queries already designed.
- Supports arbitrary lookback windows without query complexity.

**Cons:**
- Requires a new scheduled Lambda and a new table — contradicts the "no new Lambda or infrastructure" delivery constraint.
- Introduces eventual consistency: the baseline is at most 24 hours stale.
- More moving parts to operate and monitor.

---

## Decision

> **Not yet decided.** This ADR is open. Evaluate the options above and record the decision here.

---

## Consequences

> To be completed once the decision is recorded.

---

## References

- Service Spec §4.1 (FR-16 — trend and change requirement)
- Service Spec §9.1 (response shape with trend/change fields)
- Service Spec §15 (edge cases: Promise.allSettled recommendation)
- Service Spec §2 (Scope: no new Lambda or infrastructure changes)
