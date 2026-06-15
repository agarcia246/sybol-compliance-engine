# ADR-0006: Sentinel SQS Message for `total_rows` Tracking

**Status:** ✅ Accepted  
**Date:** 2026-03-19  
**Deciders:** Engineering Team  
**SPEC sections:** FR-24, FR-30, FR-36  

---

## Context and Problem Statement

The `batch_processes` table tracks `total_rows`, `processed_rows`, and `failed_rows` to report progress and detect completion. The worker detects completion via an atomic `UPDATE … RETURNING` when `processed_rows + failed_rows >= total_rows`.

This requires `total_rows` to be known and stored in the database **before** or **at the same time** that workers start decrementing towards it. The parser generates the row messages, so it is the only component that knows the final count. However, the question is: **how and when should `total_rows` be communicated to the system?**

---

## Decision Drivers

- The parser uses streaming mode to avoid loading the entire Excel into memory — it emits row messages as it reads, so it does not know `total_rows` until the stream ends.
- By the time the stream ends, row messages have already been published to SQS and workers may have already started processing them.
- The system must handle the race condition where some workers finish before `total_rows` is set.
- The parser must not access the database (decided: the parser is stateless, no DB, no STS).
- Introducing a dependency on message ordering (FIFO) would eliminate parallelism — unacceptable for 3000 rows.

---

## Considered Options

### Option A — Frontend counts rows and passes `totalRows` in `POST /api/bl/batch`
- The frontend reads the Excel file using the existing `parseClaimsFromExcel()` function before uploading, counts rows, and sends the count in the request body.
- `batch_processes.total_rows` is set at creation time, before the parser runs.
- **Pros:** Simplest worker logic (no special case needed); `total_rows` always available before any worker runs.
- **Cons:** The frontend reads the file twice (once to count, once to upload via S3). While `parseClaimsFromExcel()` exists, adding this logic couples the upload flow to file parsing. If a user uploads a file generated externally (not via the template), the count must still be accurate.

### Option B — Each row message carries `totalRows` (known only after stream ends)
- The parser buffers all messages, waits for stream end, then adds `totalRows` to each message and sends them all.
- **Pros:** `totalRows` is in every message; first worker can set it on first DB write.
- **Cons:** Negates the benefits of streaming (must buffer all rows in Lambda memory before sending any); 3000 rows × message payload ≈ non-trivial memory; violates the intent of streaming.

### Option C — Sentinel message at end of stream (chosen)
- The parser streams row messages normally. When the stream ends, it sends one additional sentinel message: `{ type: 'sentinel', processId, tenantId, totalRows }`.
- The worker, on receiving a sentinel, updates `batch_processes.total_rows` and checks if already complete.
- Each row worker uses `CASE WHEN total_rows > 0 AND processed_rows + failed_rows + 1 >= total_rows THEN 'DONE'` — the `total_rows > 0` guard prevents false completion before the sentinel arrives.
- **Pros:** No memory buffering in parser; no frontend file pre-reading; single source of truth for count.
- **Cons:** Race condition must be handled: if sentinel arrives after all row workers have completed, the sentinel's `UPDATE` must detect and set `DONE`. This is handled by the same atomic `UPDATE … RETURNING`.

**Race condition analysis for Option C:**

- **Sentinel arrives before all row workers finish:** Sentinel sets `total_rows`. Row workers check completion normally. ✅
- **Sentinel arrives after all row workers finish:** `processed_rows + failed_rows` already equals the count. The sentinel's `UPDATE` sets `total_rows` and evaluates `CASE WHEN total_rows > 0 AND processed_rows + failed_rows >= total_rows THEN 'DONE'`. ✅
- **Sentinel is delayed in SQS but row workers haven't all finished:** No issue — `total_rows = 0` prevents false completion. ✅
- **Sentinel is lost / fails / goes to DLQ:** The DLQ handler must detect sentinel type and retry the `UPDATE total_rows`. If the DLQ is also exhausted, the process remains in `PROCESSING` indefinitely — requires manual recovery. This is an acceptable edge case given SQS's delivery guarantees.

---

## Decision

**Option C** — sentinel message published after stream completion.

The sentinel message schema:
```json
{
  "type": "sentinel",
  "processId": "uuid",
  "tenantId": "repsol",
  "totalRows": 3000
}
```

The worker handles it with a branch:
```js
if (message.type === 'sentinel') {
  const result = await BatchProcess.update(message.processId,
    { total_rows: message.totalRows }, auth);
  if (['DONE', 'PARTIAL_FAILURE'].includes(result.status)) {
    await ActivityModel.createAlert(auth, { processId, ... });
  }
  return;
}
```

The atomic SQL for completion detection (used by both row workers and sentinel):
```sql
UPDATE batch_processes SET
  total_rows     = CASE WHEN $isSentinel THEN $totalRows ELSE total_rows END,
  processed_rows = CASE WHEN $isSentinel THEN processed_rows ELSE processed_rows + 1 END,
  failed_rows    = CASE WHEN $isFailed   THEN failed_rows + 1 ELSE failed_rows END,
  status = CASE
    WHEN total_rows > 0
     AND (processed_rows + failed_rows + ...) >= (CASE WHEN $isSentinel THEN $totalRows ELSE total_rows END)
    THEN CASE WHEN failed_rows > 0 THEN 'PARTIAL_FAILURE' ELSE 'DONE' END
    ELSE status
  END
WHERE id = $processId
RETURNING status;
```

---

## Consequences

- **Positive:** Parser remains stateless and streaming — no memory accumulation.
- **Positive:** No frontend changes required to count rows.
- **Positive:** Works correctly regardless of SQS message delivery order (SQS Standard).
- **Negative:** The DLQ must explicitly handle sentinel messages to avoid processes stuck in `PROCESSING`. This adds a small branch to the DLQ handler.
- **Negative:** If the sentinel is permanently lost (DLQ also fails), the process must be manually recovered. Probability is extremely low with SQS Standard + DLQ configured.

---

## References

- [Batch Import SPEC FR-24, FR-30, FR-36](../batch_spec.md#7-functional-requirements)
- ADR-0004 — handler placement (parser and worker co-located in businessLogic)
- ADR-0005 — auth context for the worker (needed to execute the DB update)
