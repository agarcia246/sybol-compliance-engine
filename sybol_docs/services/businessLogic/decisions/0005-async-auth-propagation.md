# ADR-0005: Auth Context Propagation for Async Workers (STS without JWT)

**Status:** ✅ Accepted  
**Date:** 2026-03-19  
**Deciders:** Engineering Team  
**SPEC sections:** NFR-41, FR-31  

---

## Context and Problem Statement

The `sqsBatchHandler` worker must call `CredentialModel.create(data, auth)`, which requires an `auth` context containing `tenantId`, `userRole`, and `awsCredentials` (temporary STS credentials for the tenant's IAM role). These credentials are used to connect to the tenant's RDS database and access its KMS key.

In the HTTP flow, this `auth` context is built by `requireIdToken` middleware: it validates the user's Cognito JWT, extracts `tenantId` and `userRole`, then calls `tenantStsCredentials.getTenantStsSession({ idToken })` to perform `AssumeRole`.

However, **the worker runs in an asynchronous Lambda triggered by SQS**. There is no HTTP request and no current user session. The question is: **how should the worker obtain valid tenant-scoped AWS credentials?**

---

## Decision Drivers

- Cognito ID tokens expire after 1 hour (configured in `SybolCoreStack`). A batch of 3000 rows processing at scale may take longer than 1 hour end-to-end.
- Propagating the JWT in the SQS message would mean it could be expired by the time the worker processes it.
- STS `AssumeRole` sessions can be requested freshly per message with no dependency on a user session.
- The tenant's IAM role ARN follows a deterministic naming convention: `arn:aws:iam::{accountId}:role/Sybol-{tenantId}-{role}` — already established by `tenantStsCredentials/index.js` when `custom:role_arn` is absent from the JWT.
- Strict tenant isolation requires that each worker call uses credentials scoped to the correct tenant, not the Lambda's execution role.

---

## Considered Options

### Option A — Include the Cognito JWT in the SQS message
- The `POST /api/bl/batch` handler saves the user's JWT in each SQS message.
- The worker re-uses it to call `getTenantStsSession({ idToken })`.
- **Pros:** No changes to `tenantStsCredentials` library.
- **Cons:** JWT expires in 1 hour; messages processed after expiry will fail authentication. No refresh mechanism is available in a background Lambda. Embedding user tokens in queue messages is a security anti-pattern (tokens are longer-lived than needed for the operation and are stored at rest).

### Option B — Add `getTenantStsSessionByTenantId()` to `tenantStsCredentials` (chosen)
- Add a new function that constructs the `roleArn` from `tenantId` + `role` (same convention already used as fallback in `getTenantStsSession`), then calls `AssumeRole` directly.
- The worker calls this function per message, obtaining fresh STS credentials valid for 1 hour per credential.
- `tenantId` comes from the SQS message (trusted because it is derived from the S3 key prefix, which is IAM-controlled). `role` defaults to `admin`, configurable via `BATCH_DEFAULT_ROLE` env var.
- **Pros:** No JWT expiry issue; no user tokens in queue messages; consistent with existing `AssumeRole` pattern; one small addition to an existing library.
- **Cons:** One additional STS API call per row message. Acceptable: STS calls are fast (<100ms) and the multi-tenant pattern already requires them in every HTTP request.

### Option C — Use the Lambda execution role directly for DB access
- Grant the `businessLogic` Lambda execution role direct access to all tenant RDS databases.
- **Pros:** No STS call needed; simpler.
- **Cons:** Violates multi-tenant isolation. The Lambda's execution role would have access to all tenants' data simultaneously. This is the exact security boundary the `Sybol-{tenantId}-{role}` IAM roles are designed to enforce. **Rejected as a security violation.**

---

## Decision

**Option B** — add `getTenantStsSessionByTenantId({ tenantId, role })` to `services/businessLogic/src/lib/tenantStsCredentials/index.js`.

```js
async function getTenantStsSessionByTenantId({ tenantId, role }) {
  const roleArn = `arn:aws:iam::${config.aws.accountId}:role/Sybol-${tenantId}-${role}`;
  const sts = new STSClient();
  const shortTimestamp = Date.now().toString().slice(-8);
  const sessionName = `batch-${tenantId}-${shortTimestamp}`.substring(0, 64);
  const response = await sts.send(new AssumeRoleCommand({
    RoleArn: roleArn,
    RoleSessionName: sessionName
  }));
  return response.Credentials;
}
```

The worker builds the `auth` context as:
```js
const creds = await getTenantStsSessionByTenantId({ tenantId: msg.tenantId, role: process.env.BATCH_DEFAULT_ROLE || 'admin' });
const auth = {
  tenantId: msg.tenantId,
  userRole: process.env.BATCH_DEFAULT_ROLE || 'admin',
  awsCredentials: {
    accessKeyId: creds.AccessKeyId,
    secretAccessKey: creds.SecretAccessKey,
    sessionToken: creds.SessionToken
  }
};
```

**Why is `tenantId` from the SQS message trustworthy?**

The message originates from the `s3ParserHandler`, which derives `tenantId` from the S3 object key prefix (`key.split('/')[0]`). That prefix is constrained by IAM: the frontend can only write to `{their tenantId}/batch-imports/*`. No tenant can write to another tenant's prefix. Therefore, the `tenantId` in the key — and by extension in the message — is controlled by AWS IAM, not by user-supplied data.

---

## Consequences

- **Positive:** No JWT expiry issues for long-running batches.
- **Positive:** No user tokens stored in SQS messages or DLQ payloads.
- **Positive:** Full tenant isolation maintained: each worker call uses credentials scoped to exactly the target tenant.
- **Positive:** The new function follows the identical pattern as the existing `getTenantStsSession` fallback logic — minimal cognitive overhead.
- **Negative:** One STS `AssumeRole` call per row message. At 3000 rows with concurrency of 10, this is ~300 STS calls in parallel — well within STS limits (no throttle below 1000 TPS).
- **Negative:** `BATCH_DEFAULT_ROLE` must be set correctly per environment. Wrong value → AssumeRole fails for that tenant → row errors.

---

## References

- [Batch Import SPEC §8 — Architecture](../batch_spec.md#8-architecture-overview)
- [Batch Import SPEC NFR-41](../batch_spec.md#8-non-functional-requirements)
- `services/businessLogic/src/lib/tenantStsCredentials/index.js` — existing implementation
- ADR-0001 — Cognito authentication (JWT structure and custom claims)
