# Component Architecture

## Purpose

This document maps the implemented service boundaries in the current repository. It replaces earlier speculative endpoint inventories with the route groups and responsibilities that can be verified from source.

## Frontend to Backend Shape

```mermaid
graph LR
    WWC[WWC] --> BO[/api/bo]
    WWC --> BL[/api/bl]
    WWC --> CAT[/api/catalog]
    WWC --> PS[/api/ps]

    OnBoard[OnBoardingWeb] --> BO
    OnBoard --> Sumsub[Sumsub]
    OnBoard --> Chain[Blockchain helpers]
```

## Service Summary

| Service | Prefix | Current responsibility | Notes |
| ------- | ------ | ---------------------- | ----- |
| Backoffice | `/api/bo` | KYB, DID document management, email helpers | Current source does not expose the broader auth, billing, or tenant-admin routes previously documented |
| BusinessLogic | `/api/bl` | Credentials, requests, presentations, activity, contacts, delegation trees | Uses DID document lookups and tenant-aware database access |
| Catalog | `/api/catalog` | Documents, claims, forms, fields, compliance regions | Public reads and authenticated writes |
| Propagate | `/api/ps` | JWT delivery, receipt, and EventBridge publication | EventBridge also invokes dedicated handlers directly |

## Backoffice

### Backoffice Route Groups

- `/api/bo/health`
- `/api/bo/kyb/*`
- `/api/bo/did-document/*`
- `/api/bo/email/*`

### Backoffice Responsibilities

- Generate Sumsub access tokens and track KYB status
- Receive and process Sumsub webhook updates
- Create, read, update, list, and delete DID documents
- Support email-related helper endpoints

### Backoffice Scope Correction

The current backoffice service is not a general tenant administration API in source. Earlier documentation mentioned platform-admin, billing, audit-log, and tenant CRUD routes that are not present in the reviewed `src/routes` tree.

## BusinessLogic

### BusinessLogic Route Groups

- `/api/bl/health`
- `/api/bl/credentials/*`
- `/api/bl/credential-requests/*`
- `/api/bl/presentations/*`
- `/api/bl/presentation-requests/*`
- `/api/bl/activity/*`
- `/api/bl/contacts/*`
- `/api/bl/delegate/*`

### BusinessLogic Responsibilities

- CRUD-style credential and credential-request flows
- Presentation and presentation-request flows
- Contact network and contact request handling
- Delegation tree creation and listing
- Activity and alert endpoints

### Key Dependencies

- Tenant-scoped PostgreSQL access
- Backoffice DID document endpoints for issuer and subject validation
- AWS KMS and signing helpers
- Catalog data for form and claim driven flows

## Catalog

### Catalog Route Groups

- `/api/catalog/health`
- `/api/catalog/documents/*`
- `/api/catalog/claims/*`
- `/api/catalog/forms/*`
- `/api/catalog/fields/*`
- `/api/catalog/compliance-regions/*`

### Catalog Responsibilities

- Versioned document definitions
- Reusable claims with validation rules
- Form composition with sections and fields
- Compliance region hierarchy

### Access Model

- GET requests may use a public connection path
- Writes require authenticated access and tenant context
- Certain modifying operations are restricted to the Sybol tenant logic described in the service README

## Propagate

### Propagate Route Groups

- `/api/ps/send`
- `/api/ps/send/event`
- `/api/ps/receive`

### Propagate Responsibilities

- Send verifiable payloads between tenants
- Publish propagation events to EventBridge
- Receive propagated JWT payloads
- Process EventBridge events outside HTTP through a dedicated handler path

### Propagate Scope Correction

The service README and changelog confirm that EventBridge is the current asynchronous mechanism. Earlier architecture docs that centered the platform on SQS-based propagation are outdated for the present repo state.

## Supporting Services and Utilities

### `services/svault`

- KMS-backed cryptographic operations for JWT and blockchain contexts
- README shows create, sign, verify, and key-deletion style operations

### `lambdas/PAdES`

- PDF signing workflows used by credential-related flows

### `lambdas/signEth`

- Ethereum signing helpers and blockchain-related operations

### Additional service directories

- `services/iom`
- `services/bm`

These appear in the repository and are referenced by `CoreInfra` API routes, but they were not the focus of this documentation correction pass.

## Deployment Notes

- Each primary service is an Express application with a standalone server entrypoint and a Lambda handler.
- `CoreInfra` currently wires API Gateway routes for catalog, iom, vault, bm, entity, and users.
- The changelog records pending API Gateway updates for newer `businessLogic` and `propagate` routes.

## References

- [System Overview](system-overview.md)
- [Repository Structure](../development/repository-structure.md)
- [Current State Audit](../current-state-audit.md)
