# ADR-0004: SQS + Lambda Handlers within businessLogic Service

**Status:** ✅ Accepted  
**Date:** 2026-03-19  
**Deciders:** Engineering Team  
**SPEC sections:** FR-20–FR-37, Architecture §9  

---

## Context and Problem Statement

The batch pipeline requires two asynchronous processing components:

1. A **parser** that reads the uploaded Excel and decomposes it into work items.
2. A **worker** that processes each work item and creates credentials.

The question is: **where should these components live, and how should they be packaged?**

The system already has a `businessLogic` Lambda that handles all credential lifecycle operations. The worker needs to call `CredentialModel.create()` — the core credential creation logic that already lives in `businessLogic`. The parser needs to produce messages for the worker.

---

## Decision Drivers

- The worker must call `CredentialModel.create()` directly (not via HTTP) to avoid managing user tokens in a background context.
- Duplicating `CredentialModel` in a separate service would violate DRY and create maintenance risk.
- A new microservice requires a new Docker image, ECR repository, CDK stack, and CI/CD pipeline — significant overhead for components that are logically part of the credential domain.
- Lambda supports multiple handler entry points from a single container image.
- The parser does not need DB access or heavy dependencies; it only needs `exceljs` and the AWS SDK (already present).

---

## Considered Options

### Option A — New standalone microservice (`batchProcessor`)
- New Docker image, new Lambda function(s), separate deployment.
- **Pros:** Clean separation of concerns; independent scaling.
- **Cons:** Requires duplicating `CredentialModel` or calling it via HTTP (creating an internal API dependency); new image, ECR repo, CDK stack, CI/CD pipeline to maintain; misaligned with the "no new service" constraint.

### Option B — Additional handlers within `businessLogic` Lambda (chosen)
- Add `exports.s3ParserHandler` and `exports.sqsBatchHandler` to `services/businessLogic/src/lambda.js`.
- Both handlers are new entry points in the same container image.
- The worker handler calls `CredentialModel.create()` directly with no HTTP round-trip.
- **Pros:** No new service, no new image, no new deployment pipeline; `CredentialModel` is shared by reference; existing `requireIdToken` middleware pattern is parallel (auth context built differently but from same library).
- **Cons:** The Lambda container image grows slightly; cold start time may increase marginally — acceptable given the async nature of batch processing.

### Option C — `businessLogic` HTTP API invoking itself
- Worker calls `POST /api/bl/credentials` internally with a service token.
- **Pros:** Clean HTTP interface; no handler co-location.
- **Cons:** Requires generating and managing a service-level JWT (no user token available); adds unnecessary network hop and serialization overhead; brittle if the HTTP API contract changes.

---

## Decision

**Option B** — both handlers are added to the existing `businessLogic` Lambda as additional export entry points.

```js
// services/businessLogic/src/lambda.js
exports.handler          = /* existing HTTP handler — unchanged */
exports.s3ParserHandler  = require('./handlers/s3ParserHandler');
exports.sqsBatchHandler  = require('./handlers/sqsBatchHandler');
```

The handler files live in `services/businessLogic/src/handlers/`. The worker calls `CredentialModel.create()` directly, using STS credentials built for the target tenant (see ADR-0005).

The existing `exports.handler` and all HTTP routes are **not modified** by this change.

---

## Consequences

- **Positive:** No duplication of credential logic; `CredentialModel.create()` is the single implementation.
- **Positive:** No new infrastructure resources (no new Lambda function, no ECR repo, no CDK changes beyond SQS queue and S3 event notification wiring).
- **Positive:** The `businessLogic` deployment pipeline remains the single pipeline to update.
- **Negative:** The Lambda container image carries exceljs and streaming dependencies even for non-batch HTTP invocations. This is acceptable: the dependencies are loaded lazily and do not affect response time for HTTP routes.
- **Negative:** If the worker handler has a bug that causes Lambda to crash, it affects the same container as the HTTP handler. Mitigated by separate Lambda function configurations pointing to different handlers from the same image.

---

## References

- [Batch Import SPEC §9](../batch_spec.md#9-architecture-overview)
- [Batch Import SPEC §16](../batch_spec.md#16-files-to-create--modify)
- ADR-0005 — auth context for the worker handler
