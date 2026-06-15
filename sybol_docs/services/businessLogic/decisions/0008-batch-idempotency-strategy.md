# ADR-0008: Batch Row Idempotency Strategy

**Status:** ✅ Accepted  
**Date:** 2026-03-19  
**Deciders:** Engineering Team  
**SPEC sections:** NFR-05, §10 Error Handling  

---

## Context and Problem Statement

Amazon SQS Standard queues guarantee **at-least-once delivery**: under rare network or Lambda execution failure conditions, the same SQS message may be delivered more than once. If the worker Lambda is re-invoked with the same row message (e.g., after a Lambda crash mid-processing), it could create duplicate credentials for the same row.

Idempotency at the **Verifiable Credential level** is not possible by definition: each credential creation generates a unique on-chain record, a unique DID-bound JWT, and a new DB entry. There is no natural content-addressable key across credential types.

However, idempotency **at the batch row level** (within a single file upload) is achievable and desirable: given a `(processId, rowIndex)` pair, the system should guarantee that credentials are created exactly once per row per process execution, regardless of SQS redelivery.

---

## Decision Drivers

- `CredentialModel.create()` performs a DB insert + blockchain transaction — both are non-idempotent by nature.
- A duplicate credential creates a second, independent on-chain record. This is visible to the credential holder and the issuer.
- The `batch_process_log` table already exists and has `(process_id, row_index)` as a de-facto identifier for each row within a process.
- No new tables should be introduced if avoidable.
- The solution must work correctly under concurrent worker Lambda executions (SQS Standard, multiple simultaneous invocations).
- The expected scale is 1,000–5,000 rows per batch import. Not high-frequency streaming.

---

## Considered Options

### Option A — Claim-value-based deduplication
- Before creating a credential, query the DB for an existing credential with the same `documentId + recipientDid + claims hash`.
- If found, skip creation.
- **Pros:** True content-level duplicate prevention.
- **Cons:** Claims are stored as JSONB (`subject_data` column) — hashing and comparing variable JSON structures is expensive. The claim schema is dynamic (differs per catalog document). Not trivially correct for all credential types.

### Option B — SQS FIFO with `MessageDeduplicationId`
- Use SQS FIFO queue instead of Standard, with `MessageDeduplicationId = MD5(processId + rowIndex)`.
- SQS FIFO deduplicates within a 5-minute window.
- **Pros:** SQS handles deduplication transparently.
- **Cons:** FIFO queues limit parallelism within the same `MessageGroupId`. To retain parallelism, one group per batch is needed, which limits concurrent Lambda invocations. Adds operational complexity. ADR-0004 already decided SQS Standard.

### Option C — Dedicated idempotency table
- Before processing each row, atomically INSERT a record into `batch_row_idempotency(processId, rowIndex)`. On unique constraint violation: skip.
- **Pros:** Correct, fast, atomic.
- **Cons:** Requires a new table. Table must be cleaned up after each process.

### Option D — Extend `batch_process_log` as a general row execution log (chosen)

Repurpose `batch_process_log` as a complete row execution log — renaming it conceptually to a **row log** that records both errors and successful rows. A `UNIQUE(process_id, row_index)` constraint makes it the idempotency gate.

**Mechanism:**
1. Before any processing, the worker attempts:
   ```sql
   INSERT INTO batch_process_log (process_id, row_index, status, row_data, error_msg)
   VALUES ($processId, $rowIndex, 'PROCESSING', $rowData, NULL)
   ON CONFLICT (process_id, row_index) DO NOTHING
   RETURNING id
   ```
2. If `RETURNING` returns no row → this `(processId, rowIndex)` is already being processed or was completed. **Skip immediately.**
3. If `RETURNING` returns an `id` → this worker owns the row. Proceed with credential creation.
4. On success: `UPDATE batch_process_log SET status = 'OK' WHERE process_id = $p AND row_index = $r`
5. On failure: `UPDATE batch_process_log SET status = 'ERROR', error_msg = $msg WHERE ...`

**Schema change required:**
```sql
-- Add status column and unique constraint to batch_process_log
ALTER TABLE batch_process_log
  ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'ERROR',
  ALTER COLUMN error_msg DROP NOT NULL;

ALTER TABLE batch_process_log
  ADD CONSTRAINT uq_batch_row UNIQUE (process_id, row_index);
```

The `INSERT … ON CONFLICT DO NOTHING` is atomic in PostgreSQL — no race condition is possible between two concurrent workers claiming the same row.

**Pros:**
- No new table.
- Atomic claim via PostgreSQL `ON CONFLICT DO NOTHING`.
- Full execution log per row (status: `PROCESSING | OK | ERROR`) — useful for progress APIs and post-mortem analysis.
- Works correctly under concurrent SQS Standard delivery (multiple Lambda invocations processing different rows simultaneously).
- Rows stuck in `PROCESSING` after a Lambda crash are detectable (no `OK`/`ERROR` final status) and can be retried manually or via DLQ reprocessing.

**Cons:**
- `batch_process_log` now stores successful rows too (3,000 rows for a fully successful process). Storage cost is negligible (each row is a few hundred bytes).
- The table name `batch_process_log` is slightly misleading for `OK` rows. Acceptable as an implementation detail — the API layer filters by `status = 'ERROR'` when exposing errors to users.

---

## Decision

**Option D** — extend `batch_process_log` with a `status` column and `UNIQUE(process_id, row_index)` constraint, using `INSERT … ON CONFLICT DO NOTHING RETURNING id` as the atomic idempotency gate before each row is processed.

This provides deterministic row-level idempotency within a single batch process without introducing new tables, without changing the SQS queue type, and without per-row content hashing.

**Worker pseudocode:**
```js
async function processBatchRow(message, auth) {
  const { processId, rowIndex, rowData } = message;

  // Atomic claim: returns null if already processed/in-progress
  const claimed = await db.query(`
    INSERT INTO batch_process_log (process_id, row_index, status, row_data)
    VALUES ($1, $2, 'PROCESSING', $3)
    ON CONFLICT (process_id, row_index) DO NOTHING
    RETURNING id
  `, [processId, rowIndex, rowData]);

  if (claimed.rowCount === 0) return; // already handled — skip

  try {
    await CredentialModel.create(rowData, auth);
    await db.query(
      `UPDATE batch_process_log SET status = 'OK' WHERE process_id = $1 AND row_index = $2`,
      [processId, rowIndex]
    );
  } catch (err) {
    await db.query(
      `UPDATE batch_process_log SET status = 'ERROR', error_msg = $3 WHERE process_id = $1 AND row_index = $2`,
      [processId, rowIndex, err.message]
    );
  } finally {
    // Update processed_rows / failed_rows counter and check completion
    await BatchProcess.incrementAndCheckDone(processId, isError);
  }
}
```

---

## Consequences

- **Positive:** Duplicate credential creation within a single batch process is prevented.
- **Positive:** No new DB table. Change is additive (one column + one constraint on existing table).
- **Positive:** Full row-level audit trail: `OK`, `ERROR`, and orphaned `PROCESSING` rows (Lambda crash indicator) are all visible.
- **Positive:** Compatible with SQS Standard and concurrent Lambda execution.
- **Negative:** `batch_process_log` stores all rows (not only errors). The name is slightly misleading but the API layer filters appropriately.
- **Operational note:** Rows left in `PROCESSING` status after a Lambda crash indicate mid-flight failures. The DLQ handler should detect these and either retry or mark as `ERROR`. This is a known, manageable edge case.

---

## References

- [Batch Import SPEC NFR-05, §10 Error Handling](../batch_spec.md#8-non-functional-requirements)
- ADR-0004 — SQS Standard queue confirmed (not FIFO)
- `services/businessLogic/src/models/Credential.js` — non-idempotent create at credential level
- `services/businessLogic/database/schema_v2.sql` — `batch_process_log` table to be altered
