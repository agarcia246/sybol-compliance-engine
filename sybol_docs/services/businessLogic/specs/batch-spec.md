# Batch Credential Import — Specification

**Status:** ✅ Accepted  
**Version:** 1.0  
**Date:** 2026-03-19  
**Authors:** Engineering Team  
**Capability code:** `batch`  

---

## 1. Purpose

This document specifies the **Batch Credential Import** capability: a pipeline that allows an authenticated tenant user to upload an Excel file containing up to ~3000 rows of subject data and trigger the creation of one or more Verifiable Credentials per row, fully asynchronously, with per-row error tracking and a completion notification.

The capability extends the `businessLogic` service. No new service is created.

---

## 2. Goals

- Allow a tenant to issue credentials in bulk from a structured Excel file without manual row-by-row interaction.
- Preserve strict multi-tenant isolation: no cross-tenant data access at any point in the pipeline.
- Reuse the existing `CredentialModel.create()` logic without duplication.
- Provide real-time process tracking (progress, errors, completion status).
- Notify the issuing user when processing completes, including which rows failed.

---

## 3. Non-Goals

- This capability does **not** implement a new microservice. All code lives within `businessLogic`.
- This capability does **not** support CSV or other file formats — only `.xlsx`.
- This capability does **not** support resuming a partially-failed process by re-uploading the same file — a new process must be created.
- This capability does **not** modify the existing `POST /api/bl/credentials` endpoint.
- Frontend implementation of progress polling UI is out of scope for the backend spec.

---

## 4. Callers

| Caller | Interaction |
|--------|-------------|
| `wwc` (frontend) | `POST /api/bl/batch` to create process; `CognitoService.uploadToS3()` to upload the Excel; `GET /api/bl/batch/:id` to poll progress |
| S3 Event Notification | Triggers `s3ParserHandler` in `businessLogic` Lambda on `PUT` to `{tenantId}/batch-imports/*.xlsx` |
| Amazon SQS | Triggers `sqsBatchHandler` in `businessLogic` Lambda per message |
| SQS DLQ | Triggers `sqsBatchHandler` (DLQ branch) for messages exhausting retries |

---

## 5. Dependencies

| Dependency | Purpose |
|------------|---------|
| Amazon S3 (`sybol-data-{env}`) | Stores uploaded Excel files, segregated by tenant prefix |
| Amazon SQS (batch queue + DLQ) | Decouples parsing from credential creation |
| `businessLogic` RDS (per-tenant DB) | Stores `batch_processes`, `batch_process_log`, `credentials`, `alerts` |
| `catalog` service | Resolves `documentId` and claim definitions (via existing `CredentialModel.create()` calls) |
| AWS STS | Issues per-tenant credentials for async workers (no JWT available) |
| `tenantStsCredentials` library | Provides `getTenantStsSessionByTenantId()` — see [ADR-0005](decisions/0005-async-auth-propagation.md) |
| `exceljs` | Excel parsing (streaming) and generation |

---

## 6. Key Entities

| Entity | Description |
|--------|-------------|
| `BatchProcess` | Represents one upload+processing job. Tracks status, row counts, and links to the row log. |
| `BatchProcessLog` | Records every processed row with its outcome (`PROCESSING`, `OK`, `ERROR`). Acts as the idempotency gate via `UNIQUE(process_id, row_index)`. |
| `Credential` | Pre-existing entity created by `CredentialModel.create()`. One credential per `(row, documentId)` pair. |

---

## 7. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-10 | The system MUST expose `POST /api/bl/batch` (authenticated) that creates a `BatchProcess` record with status `PENDING`, generates an S3 key following the pattern `{tenantId}/batch-imports/{processId}.xlsx`, and returns `{ processId, s3Key, bucket }`. |
| FR-11 | The system MUST expose `GET /api/bl/batch` (authenticated) that returns a paginated list of `BatchProcess` records for the authenticated tenant. |
| FR-12 | The system MUST expose `GET /api/bl/batch/:id` (authenticated) that returns the full `BatchProcess` record including current status, row counts, and the array of `batch_process_log` entries with `status = 'ERROR'`. |
| FR-13 | The system MUST expose `POST /api/bl/batch/:id` (authenticated) that allows updating process fields (reserved for internal and administrative use). |
| FR-20 | The `s3ParserHandler` MUST be triggered by an S3 `PUT` event for objects matching prefix `*/batch-imports/*.xlsx` in the `sybol-data-{env}` bucket. |
| FR-21 | The `s3ParserHandler` MUST extract `tenantId` from the S3 object key prefix (`key.split('/')[0]`) and `processId` from the filename. |
| FR-22 | The `s3ParserHandler` MUST read the hidden Row 3 of the Excel to build a column-to-claimKey+documentId mapping. See [ADR-0007](decisions/0007-excel-hidden-key-row.md). |
| FR-23 | The `s3ParserHandler` MUST publish one SQS message of type `row` per data row (rows 6+), containing `{ type, processId, tenantId, rowIndex, rowData }`. |
| FR-24 | The `s3ParserHandler` MUST publish one SQS sentinel message after all row messages, containing `{ type:'sentinel', processId, tenantId, totalRows }`. See [ADR-0006](decisions/0006-sentinel-message-total-rows.md). |
| FR-25 | The `s3ParserHandler` MUST NOT access the database or perform STS credential exchange. |
| FR-30 | The `sqsBatchHandler` MUST process messages of type `sentinel` by updating `batch_processes.total_rows` and evaluating whether the process is complete (see FR-36). |
| FR-31 | The `sqsBatchHandler` MUST process messages of type `row` by obtaining tenant STS credentials via `getTenantStsSessionByTenantId({ tenantId, role:'admin' })`. |
| FR-31b | Before processing any row, the `sqsBatchHandler` MUST execute `INSERT INTO batch_process_log(process_id, row_index, status, row_data) VALUES(...) ON CONFLICT (process_id, row_index) DO NOTHING RETURNING id`. If the result is empty, the row MUST be skipped immediately (idempotency gate). See [ADR-0008](decisions/0008-batch-idempotency-strategy.md). |
| FR-32 | The `sqsBatchHandler` MUST group `rowData` claims by `documentId` and call `CredentialModel.create()` once per distinct `documentId` present in the row. |
| FR-33 | The `sqsBatchHandler` MUST, on credential creation failure, update the `batch_process_log` entry to `status='ERROR'` and increment `failed_rows` atomically. |
| FR-34 | The `sqsBatchHandler` MUST, on credential creation success, update the `batch_process_log` entry to `status='OK'` and increment `processed_rows` atomically. |
| FR-35 | The SQS DLQ handler MUST insert or update a `batch_process_log` record with `status='ERROR'`, `error_msg='max retries exceeded'` for any message that exhausts SQS retries, and increment `failed_rows`. |
| FR-36 | The system MUST detect process completion via an atomic PostgreSQL `UPDATE … RETURNING` that sets `status = 'DONE'` when `processed_rows + failed_rows >= total_rows AND total_rows > 0`. If `failed_rows > 0`, status MUST be set to `PARTIAL_FAILURE` instead of `DONE`. |
| FR-37 | The handler that detects `DONE` or `PARTIAL_FAILURE` in the `RETURNING` result MUST call `ActivityModel.createAlert()` with a message listing the number of successes, failures, and referencing the `processId`. |
| FR-40 | The Excel template generator (`excelGenerator.js`) MUST write technical claim keys and document IDs in Row 3 (hidden) in the same column order as the visible labels in Row 4. |
| FR-41 | The Excel template generator MUST set `worksheet.getRow(3).hidden = true` so the key row is not visible to users. |

---

## 8. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | The pipeline MUST tolerate individual row failures without aborting the entire process. |
| NFR-02 | The `sqsBatchHandler` MUST retry failed messages up to a configurable maximum (default: 3) before routing to DLQ. |
| NFR-05 | The system MUST guarantee that each `(processId, rowIndex)` pair produces credentials at most once per batch process execution, even under SQS at-least-once delivery. See [ADR-0008](decisions/0008-batch-idempotency-strategy.md). |
| NFR-11 | SQS visibility timeout MUST be set to at least 300 seconds to accommodate credential creation including blockchain calls. |
| NFR-12 | SQS message retention MUST be set to 14 days. |
| NFR-20 | The S3 bucket MUST have `BlockPublicAccess` fully enabled. |
| NFR-21 | Tenant IAM roles MUST have `s3:PutObject` restricted to their own prefix `{tenantId}/batch-imports/*`. No cross-tenant writes are possible by IAM policy. See [ADR-0003](decisions/0003-s3-tenant-data-bucket.md). |
| NFR-22 | The `s3ParserHandler` execution role MUST have `s3:GetObject` on the full bucket (system actor, not tenant actor). |
| NFR-23 | `tenantId` in SQS messages is trusted only to the extent that the S3 key prefix is trusted — enforced by IAM at upload time. |
| NFR-31 | The `sqsBatchHandler` MUST be stateless. Tenant context MUST be derived entirely from the SQS message and STS, not from Lambda environment variables. |
| NFR-41 | All per-tenant DB operations in the async handlers MUST use STS credentials obtained via `getTenantStsSessionByTenantId()`. No cross-tenant credential use is possible. See [ADR-0005](decisions/0005-async-auth-propagation.md). |
| NFR-51 | All handlers MUST emit structured JSON logs including `processId`, `tenantId`, `rowIndex` (where applicable), and error details. |
| NFR-52 | The `batch_processes` table MUST have `updated_at` automatically maintained via PostgreSQL trigger. |

---

## 9. Architecture Overview

```
wwc (frontend)
  │
  ├─ POST /api/bl/batch ──────────────────────► businessLogic Lambda (HTTP)
  │    returns { processId, s3Key, bucket }          └─ INSERT batch_processes (PENDING)
  │
  ├─ CognitoService.uploadToS3(bucket, s3Key, file)
  │    └─ Direct PUT to S3 using Cognito Identity Pool credentials
  │         (IAM policy restricts to {tenantId}/batch-imports/* only)
  │
S3 PUT event ──────────────────────────────────► businessLogic Lambda (s3ParserHandler)
  sybol-data-{env}                                   ├─ Extract tenantId from key prefix
  {tenantId}/batch-imports/{processId}.xlsx          ├─ Read Row 3 (hidden keys)
                                                     ├─ Stream Excel rows → SQS messages (type:row)
                                                     └─ Send sentinel message (type:sentinel)

SQS queue ─────────────────────────────────────► businessLogic Lambda (sqsBatchHandler)
  (batch-worker-{env})                               ├─ type:sentinel → UPDATE total_rows, check DONE
                                                     └─ type:row
                                                          ├─ Idempotency gate: INSERT batch_process_log
                                                          │   ON CONFLICT (process_id, row_index) DO NOTHING
                                                          │   → if empty result: skip (already processed)
                                                          ├─ STS AssumeRole (tenantId, role=admin)
                                                          ├─ Group claims by documentId
                                                          ├─ CredentialModel.create() × N documents
                                                          ├─ UPDATE batch_process_log (OK | ERROR)
                                                          ├─ Atomic UPDATE processed_rows / failed_rows
                                                          └─ If DONE/PARTIAL_FAILURE → createAlert()

SQS DLQ ───────────────────────────────────────► businessLogic Lambda (sqsBatchHandler / DLQ branch)
  (batch-worker-dlq-{env})                           ├─ INSERT OR UPDATE batch_process_log (status=ERROR, max retries exceeded)
                                                     └─ Atomic UPDATE failed_rows, check DONE
```

---

## 10. API Contract

### `POST /api/bl/batch`

**Auth:** `requireIdToken`

**Request body:**
```json
{
  "issuerKey": "did:sybol:issuer#key-1"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "processId": "uuid",
    "s3Key": "{tenantId}/batch-imports/{processId}.xlsx",
    "bucket": "sybol-data-{env}"
  }
}
```

---

### `GET /api/bl/batch`

**Auth:** `requireIdToken`

**Query params:** `status`, `page`, `limit`

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "status": "PROCESSING",
      "totalRows": 3000,
      "processedRows": 1450,
      "failedRows": 2,
      "s3Key": "repsol/batch-imports/uuid.xlsx",
      "initiatedBy": "sub-cognito-uuid",
      "createdAt": "2026-03-19T10:00:00Z",
      "updatedAt": "2026-03-19T10:05:23Z"
    }
  ]
}
```

---

### `GET /api/bl/batch/:id`

**Auth:** `requireIdToken`

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "status": "PARTIAL_FAILURE",
    "totalRows": 3000,
    "processedRows": 2995,
    "failedRows": 5,
    "s3Key": "repsol/batch-imports/uuid.xlsx",
    "initiatedBy": "sub-cognito-uuid",
    "createdAt": "2026-03-19T10:00:00Z",
    "updatedAt": "2026-03-19T10:12:00Z",
    "errors": [
      {
        "rowIndex": 12,
        "rowData": { "subject_did": "did:sybol:abc", "sybol.pub.travel.passportNumber": { "value": "X", "documentId": "doc-passport" } },
        "errorMsg": "DID not found in registry",
        "createdAt": "2026-03-19T10:08:45Z"
      }
    ]
  }
}
```

---

### `POST /api/bl/batch/:id`

**Auth:** `requireIdToken`

**Request body:** Partial update of allowed fields (`status`, `total_rows`, `processed_rows`, `failed_rows`).

**Response 200:** Updated `BatchProcess` object.

---

## 11. Data Model

### Table: `batch_processes`

```sql
CREATE TABLE batch_processes (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status         VARCHAR(50)  NOT NULL DEFAULT 'PENDING',
                 -- PENDING | PARSING | PROCESSING | DONE | PARTIAL_FAILURE | FAILED
  total_rows     INTEGER      NOT NULL DEFAULT 0,
  processed_rows INTEGER      NOT NULL DEFAULT 0,
  failed_rows    INTEGER      NOT NULL DEFAULT 0,
  s3_key         VARCHAR(500) NOT NULL,
  issuer_key     VARCHAR(500),
  initiated_by   VARCHAR(255),
  created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_batch_processes_status ON batch_processes(status);

CREATE TRIGGER update_batch_processes_updated_at
  BEFORE UPDATE ON batch_processes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Table: `batch_process_log`

This table serves as both an execution log and the **idempotency gate** for row processing. Every row attempted is recorded here; the `UNIQUE(process_id, row_index)` constraint prevents duplicate processing under SQS at-least-once delivery.

```sql
CREATE TABLE batch_process_log (
  id          SERIAL      PRIMARY KEY,
  process_id  UUID        NOT NULL REFERENCES batch_processes(id),
  row_index   INTEGER     NOT NULL,
  status      VARCHAR(20) NOT NULL DEFAULT 'PROCESSING',
              -- PROCESSING | OK | ERROR
  row_data    JSONB       NOT NULL,
  error_msg   TEXT        NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_batch_process_log UNIQUE (process_id, row_index)
);

CREATE INDEX idx_batch_process_log_process ON batch_process_log(process_id);
CREATE INDEX idx_batch_process_log_status  ON batch_process_log(process_id, status);
```

> **Note:** The `GET /api/bl/batch/:id` endpoint filters `status = 'ERROR'` when returning the `errors` array. `OK` and `PROCESSING` rows are not exposed in the API response. Rows remaining in `PROCESSING` after process completion indicate Lambda crashes and can be identified for manual remediation.

---

## 12. SQS Message Schemas

### Row message
```json
{
  "type": "row",
  "processId": "uuid",
  "tenantId": "repsol",
  "rowIndex": 6,
  "issuerKey": "did:sybol:issuer#key-1",
  "rowData": {
    "init_date": "2026-01-01",
    "expiration_date": "2027-01-01",
    "subject_did": "did:sybol:123",
    "sybol.pub.travel.passportNumber": { "value": "ABC123", "documentId": "doc-passport" },
    "sybol.pub.travel.nationality":    { "value": "ES",     "documentId": "doc-passport" },
    "sybol.pub.es.driver_license.num": { "value": "B-1234", "documentId": "doc-license" }
  }
}
```

### Sentinel message
```json
{
  "type": "sentinel",
  "processId": "uuid",
  "tenantId": "repsol",
  "totalRows": 3000
}
```

---

## 13. Error Handling

| Scenario | Behaviour |
|----------|-----------|
| SQS redelivers a row message (duplicate) | Idempotency gate: `INSERT … ON CONFLICT DO NOTHING RETURNING id` returns empty → row skipped immediately, no duplicate credential created |
| `CredentialModel.create()` throws | UPDATE `batch_process_log` to `status='ERROR'`, increment `failed_rows`, message deleted from queue |
| Lambda crashes after idempotency INSERT but before credential creation | Row stays in `PROCESSING` status; SQS redelivers → `ON CONFLICT DO NOTHING` returns empty → row skipped → will remain as orphaned `PROCESSING` entry |
| Lambda crashes before idempotency INSERT | SQS redelivers → idempotency INSERT succeeds → row processed normally |
| Message exhausts retries | Routed to DLQ → DLQ handler sets `batch_process_log` to `status='ERROR'` with "max retries exceeded", increments `failed_rows` |
| Sentinel message fails | Routed to DLQ → DLQ handler retries `UPDATE total_rows` |
| S3 key does not match expected pattern | `s3ParserHandler` logs error and exits without publishing messages; `batch_processes` remains `PENDING` indefinitely (manual intervention needed) |
| Excel has no data rows | Sentinel sent with `totalRows: 0` → process set to `DONE` immediately |

---

## 14. Observability

- All handlers emit structured JSON logs with `processId`, `tenantId` at minimum.
- Row-level logs include `rowIndex` and `documentId`.
- `batch_processes.updated_at` is automatically maintained and can be used to detect stalled processes.
- CloudWatch metric filters on `PARTIAL_FAILURE` and `FAILED` status log entries are recommended.

---

## 15. Infrastructure Requirements

| Resource | Configuration |
|----------|--------------|
| S3 bucket `sybol-data-{env}` | `BlockPublicAccess: ALL`, SSE-S3, lifecycle rule: delete `batch-imports/*` after 30 days |
| SQS queue `sybol-batch-worker-{env}` | Visibility timeout: 300s, message retention: 14 days, DLQ redrive: maxReceiveCount 3 |
| SQS DLQ `sybol-batch-worker-dlq-{env}` | Standard queue, retention: 14 days |
| Lambda `businessLogic` — `s3ParserHandler` | Execution role: `s3:GetObject` on `sybol-data-{env}/*`, `sqs:SendMessage` on batch queue |
| Lambda `businessLogic` — `sqsBatchHandler` | Execution role: `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sts:AssumeRole` on tenant roles |
| Tenant IAM roles | `s3:PutObject` on `arn:aws:s3:::sybol-data-{env}/{tenantId}/batch-imports/*` |

---

## 16. Files to Create / Modify

### New files
| File | Description |
|------|-------------|
| `services/businessLogic/src/models/BatchProcess.js` | `create`, `update`, `getById`, `getAll` |
| `services/businessLogic/src/controllers/batchController.js` | HTTP handlers for 4 endpoints |
| `services/businessLogic/src/routes/batch.js` | Route definitions |
| `services/businessLogic/src/handlers/s3ParserHandler.js` | S3 event handler |
| `services/businessLogic/src/handlers/sqsBatchHandler.js` | SQS + DLQ handler |

### Modified files
| File | Change |
|------|--------|
| `services/businessLogic/database/schema_v2.sql` | Add `batch_processes` table; add `batch_process_log` table with `status` column and `UNIQUE(process_id, row_index)` constraint |
| `services/businessLogic/src/lambda.js` | Export `s3ParserHandler`, `sqsBatchHandler` |
| `services/businessLogic/src/app.js` | Register `/api/bl/batch` routes |
| `services/businessLogic/src/lib/tenantStsCredentials/index.js` | Add `getTenantStsSessionByTenantId()` |
| `services/businessLogic/src/models/Activity.js` | Add `createAlert()` method |
| `webApps/wwc/src/utils/excelGenerator.js` | Add hidden Row 3 with technical keys |
| `webApps/wwc/src/pages/Catalog/Components/IssueModal.js` | Implement batch upload flow |
| `docs/CORE_SETUP.md` | Add S3 data bucket creation steps |
| `docs/GUIA_OPERATIVA_MULTI_TENANT.md` | Add Step 2.5: S3 data permissions + schema tables |

---

## 17. Open Questions

None. All architectural decisions have been resolved. See §18 for the decision log.

---

## 18. Decision Log

| ADR | Title | Status | Affects |
|-----|-------|--------|---------|
| [ADR-0003](decisions/0003-s3-tenant-data-bucket.md) | S3 data bucket with tenant prefix segregation | ✅ Accepted | NFR-20, NFR-21, NFR-22, FR-20 |
| [ADR-0004](decisions/0004-sqs-handlers-in-businesslogic.md) | SQS + Lambda handlers within businessLogic | ✅ Accepted | FR-20–FR-37, Architecture §9 |
| [ADR-0005](decisions/0005-async-auth-propagation.md) | Auth context propagation without JWT in async workers | ✅ Accepted | NFR-41, NFR-05, FR-31 |
| [ADR-0006](decisions/0006-sentinel-message-total-rows.md) | Sentinel SQS message for total_rows tracking | ✅ Accepted | FR-24, FR-30, FR-36 |
| [ADR-0007](decisions/0007-excel-hidden-key-row.md) | Excel hidden row for technical claim key encoding | ✅ Accepted | FR-22, FR-40, FR-41 |
| [ADR-0008](decisions/0008-batch-idempotency-strategy.md) | Row-level idempotency via `batch_process_log` ON CONFLICT gate | ✅ Accepted | NFR-05, FR-31b, FR-33, FR-34 |
