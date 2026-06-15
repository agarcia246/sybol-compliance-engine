# Business Logic API

## Purpose

The Business Logic API provides endpoints for managing the complete lifecycle of W3C Verifiable Credentials (VCs) and Verifiable Presentations (VPs), including issuance, verification, revocation, and presentation workflows.

## Context

This service implements the core credential management functionality of the Sybol platform. All credential operations are tenant-isolated and follow W3C Verifiable Credentials Data Model 1.1 specification.

**Base Path**: `/api/bl/*`

## Authentication

All Business Logic API endpoints require authentication via `x-id-token` header (tenant-specific database access).

**Required Headers**:
```http
Authorization: Bearer <access_token>
x-id-token: <id_token>
Content-Type: application/json
```

## Endpoints

### Credentials

#### POST /api/bl/credentials

Create a new verifiable credential.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "credentialSubject": {
    "id": "did:sybol:tenant123:user456",
    "name": "John Doe",
    "dateOfBirth": "1990-01-01"
  },
  "type": ["VerifiableCredential", "PersonalIDCredential"],
  "issuanceDate": "2026-03-10T12:00:00Z",
  "expirationDate": "2027-03-10T12:00:00Z"
}
```

**Response**

```json
{
  "success": true,
  "data": {
    "id": "credential-uuid",
    "@context": [
      "https://www.w3.org/2018/credentials/v1"
    ],
    "type": ["VerifiableCredential", "PersonalIDCredential"],
    "issuer": "did:sybol:tenant123:issuer",
    "issuanceDate": "2026-03-10T12:00:00Z",
    "expirationDate": "2027-03-10T12:00:00Z",
    "credentialSubject": {
      "id": "did:sybol:tenant123:user456",
      "name": "John Doe",
      "dateOfBirth": "1990-01-01"
    },
    "proof": {
      "type": "EcdsaSecp256k1Signature2019",
      "created": "2026-03-10T12:00:00Z",
      "verificationMethod": "did:sybol:tenant123:issuer#keys-1",
      "proofPurpose": "assertionMethod",
      "jws": "eyJhbGc..."
    }
  }
}
```

**HTTP Status Codes**

| Code | Description |
|------|-------------|
| `201` | Credential created successfully |
| `400` | Invalid credential format |
| `401` | Authentication required |
| `422` | Validation failed |

**cURL Example**

```bash
curl -X POST https://api.sybol.io/api/bl/credentials \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "x-id-token: ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "credentialSubject": {
      "id": "did:sybol:tenant123:user456",
      "name": "John Doe"
    },
    "type": ["VerifiableCredential", "PersonalIDCredential"]
  }'
```

#### GET /api/bl/credentials

Retrieve all credentials with optional filters.

**Authentication**: Required (`x-id-token`)

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `active`, `revoked`, `expired` |
| `type` | string | Filter by credential type |
| `subject` | string | Filter by subject DID |
| `issuer` | string | Filter by issuer DID |
| `limit` | integer | Results per page (max 100) |
| `cursor` | string | Pagination cursor |
| `sort` | string | Sort field (prefix with `-` for descending) |

**Response**

```json
{
  "success": true,
  "data": [
    {
      "id": "credential-uuid",
      "type": ["VerifiableCredential", "PersonalIDCredential"],
      "issuer": "did:sybol:tenant123:issuer",
      "credentialSubject": {
        "id": "did:sybol:tenant123:user456"
      },
      "status": "active",
      "issuanceDate": "2026-03-10T12:00:00Z",
      "expirationDate": "2027-03-10T12:00:00Z"
    }
  ],
  "pagination": {
    "limit": 20,
    "hasMore": true,
    "nextCursor": "eyJpZCI6MTIzfQ=="
  }
}
```

**cURL Example**

```bash
curl -X GET "https://api.sybol.io/api/bl/credentials?status=active&limit=20" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "x-id-token: ID_TOKEN"
```

#### GET /api/bl/credentials/:id

Retrieve a specific credential by ID.

**Authentication**: Required (`x-id-token`)

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Credential UUID |

**Response**

```json
{
  "success": true,
  "data": {
    "@context": [
      "https://www.w3.org/2018/credentials/v1"
    ],
    "id": "credential-uuid",
    "type": ["VerifiableCredential", "PersonalIDCredential"],
    "issuer": "did:sybol:tenant123:issuer",
    "issuanceDate": "2026-03-10T12:00:00Z",
    "credentialSubject": {
      "id": "did:sybol:tenant123:user456",
      "name": "John Doe",
      "dateOfBirth": "1990-01-01"
    },
    "proof": {
      "type": "EcdsaSecp256k1Signature2019",
      "created": "2026-03-10T12:00:00Z",
      "verificationMethod": "did:sybol:tenant123:issuer#keys-1",
      "proofPurpose": "assertionMethod",
      "jws": "eyJhbGc..."
    }
  }
}
```

**HTTP Status Codes**

| Code | Description |
|------|-------------|
| `200` | Credential found |
| `404` | Credential not found |

#### POST /api/bl/credentials/:id

Update credential metadata. This is the single mutation entry point — all field updates and lifecycle transitions go through this endpoint.

> ⚠️ **JWT immutability:** `signed_token` and `payload` (the W3C VC) are never modified by this endpoint. Only metadata columns outside the JWT can be updated.

**Authentication**: Required (`x-id-token`)

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Credential `jti` (UUID) |

**Updatable Fields**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Lifecycle status: `draft` \| `issued` \| `active` \| `revoked` \| `expired` \| `suspended` |
| `evidence_url` | string \| null | External URL of the source document backing this credential (see below) |

**Evidence URL**

`evidence_url` is a free-form URI pointing to the source document that backs this credential (Google Drive, SharePoint, Notion, S3, etc.). It is stored as metadata **outside** the signed JWT — the credential's cryptographic integrity is preserved. Access control over the document remains with the external system.

Every change to `evidence_url` is automatically recorded in the `evidence_url_traces` audit table (credential_jti, evidence_url, updated_by, updated_at).

See [ADR-0006](../decisions/0006-evidence-url-external-document-reference.md) for the full design rationale.

**Request Body**

```json
{
  "status": "revoked",
  "revocationReason": "Credential compromised"
}
```

Setting evidence URL:
```json
{ "evidence_url": "https://drive.google.com/file/d/1ABC..." }
```

Clearing evidence URL:
```json
{ "evidence_url": null }
```

**Response**

```json
{
  "success": true,
  "data": {
    "id": "credential-uuid",
    "status": "revoked",
    "revocationDate": "2026-03-10T13:00:00Z",
    "revocationReason": "Credential compromised"
  }
}
```

---

### Credential Requests

#### POST /api/bl/credential-requests

Create a credential request (holder initiates).

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "catalogEntryId": "catalog-entry-uuid",
  "requesterId": "did:sybol:tenant123:user456",
  "issuerId": "did:sybol:tenant123:issuer",
  "claims": {
    "name": "John Doe",
    "dateOfBirth": "1990-01-01"
  },
  "justification": "Required for employment verification"
}
```

**Response**

```json
{
  "success": true,
  "data": {
    "id": "request-uuid",
    "catalogEntryId": "catalog-entry-uuid",
    "requesterId": "did:sybol:tenant123:user456",
    "issuerId": "did:sybol:tenant123:issuer",
    "status": "pending",
    "createdAt": "2026-03-10T12:00:00Z"
  }
}
```

**Status Values**

| Status | Description |
|--------|-------------|
| `pending` | Awaiting issuer approval |
| `approved` | Request approved, credential issued |
| `rejected` | Request rejected by issuer |
| `cancelled` | Request cancelled by requester |

#### GET /api/bl/credential-requests

List all credential requests with filters.

**Authentication**: Required (`x-id-token`)

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status |
| `requesterId` | string | Filter by requester DID |
| `issuerId` | string | Filter by issuer DID |
| `limit` | integer | Results per page |
| `cursor` | string | Pagination cursor |

**Response**

```json
{
  "success": true,
  "data": [
    {
      "id": "request-uuid",
      "catalogEntryId": "catalog-entry-uuid",
      "requesterId": "did:sybol:tenant123:user456",
      "issuerId": "did:sybol:tenant123:issuer",
      "status": "pending",
      "createdAt": "2026-03-10T12:00:00Z"
    }
  ],
  "pagination": {
    "limit": 20,
    "hasMore": false
  }
}
```

#### GET /api/bl/credential-requests/:id

Retrieve a specific credential request.

**Authentication**: Required (`x-id-token`)

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Request UUID |

#### POST /api/bl/credential-requests/:id

Update a credential request.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "status": "approved",
  "additionalClaims": {
    "verifiedBy": "Verification Team"
  }
}
```

#### PATCH /api/bl/credential-requests/:id/approve

Approve a credential request and issue credential.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "issuer_id": "did:sybol:tenant123:issuer",
  "additional_claims": {
    "verifiedBy": "Verification Team"
  }
}
```

**Response**

```json
{
  "success": true,
  "data": {
    "requestId": "request-uuid",
    "credentialId": "credential-uuid",
    "status": "approved"
  }
}
```

#### PATCH /api/bl/credential-requests/:id/reject

Reject a credential request.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "reason": "Insufficient documentation"
}
```

**Response**

```json
{
  "success": true,
  "data": {
    "requestId": "request-uuid",
    "status": "rejected",
    "reason": "Insufficient documentation"
  }
}
```

---

### Presentations

#### POST /api/bl/presentations

Create a verifiable presentation.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "holder": "did:sybol:tenant123:user456",
  "verifiableCredential": [
    "credential-uuid-1",
    "credential-uuid-2"
  ],
  "type": ["VerifiablePresentation"],
  "challenge": "challenge-string",
  "domain": "verifier.example.com"
}
```

**Response**

```json
{
  "success": true,
  "data": {
    "@context": [
      "https://www.w3.org/2018/credentials/v1"
    ],
    "type": ["VerifiablePresentation"],
    "id": "presentation-uuid",
    "holder": "did:sybol:tenant123:user456",
    "verifiableCredential": [
      {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "type": ["VerifiableCredential"],
        "issuer": "did:sybol:tenant123:issuer",
        "credentialSubject": { }
      }
    ],
    "proof": {
      "type": "EcdsaSecp256k1Signature2019",
      "created": "2026-03-10T12:00:00Z",
      "challenge": "challenge-string",
      "domain": "verifier.example.com",
      "verificationMethod": "did:sybol:tenant123:user456#keys-1",
      "proofPurpose": "authentication",
      "jws": "eyJhbGc..."
    }
  }
}
```

#### GET /api/bl/presentations

List all presentations with filters.

**Authentication**: Required (`x-id-token`)

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `holder` | string | Filter by holder DID |
| `verifier` | string | Filter by verifier DID |
| `status` | string | Filter by verification status |
| `limit` | integer | Results per page |
| `cursor` | string | Pagination cursor |

#### POST /api/bl/presentations/preview

Generate a presentation preview without signing.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "holder": "did:sybol:tenant123:user456",
  "verifiableCredential": ["credential-uuid-1"]
}
```

**Response**

Similar to POST response but without `proof` field.

#### GET /api/bl/presentations/:id

Retrieve a specific presentation.

**Authentication**: Required (`x-id-token`)

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Presentation UUID |

#### POST /api/bl/presentations/:id

Update a presentation (e.g., mark as verified).

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "verified": true,
  "verificationResult": "success"
}
```

#### DELETE /api/bl/presentations/:id

Delete a presentation.

**Authentication**: Required (`x-id-token`)

**Response**

```json
{
  "success": true,
  "message": "Presentation deleted"
}
```

---

### Presentation Requests

#### POST /api/bl/presentation-requests

Create a presentation request (verifier initiates).

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "verifier": "did:sybol:tenant123:verifier",
  "holder": "did:sybol:tenant123:user456",
  "requestedCredentials": [
    {
      "type": "PersonalIDCredential",
      "constraints": {
        "fields": ["name", "dateOfBirth"]
      }
    }
  ],
  "challenge": "unique-challenge-string",
  "domain": "verifier.example.com",
  "expiresAt": "2026-03-11T12:00:00Z"
}
```

**Response**

```json
{
  "success": true,
  "data": {
    "id": "presentation-request-uuid",
    "verifier": "did:sybol:tenant123:verifier",
    "holder": "did:sybol:tenant123:user456",
    "status": "pending",
    "createdAt": "2026-03-10T12:00:00Z",
    "expiresAt": "2026-03-11T12:00:00Z"
  }
}
```

#### GET /api/bl/presentation-requests

List all presentation requests.

**Authentication**: Required (`x-id-token`)

#### GET /api/bl/presentation-requests/:id

Retrieve a specific presentation request.

**Authentication**: Required (`x-id-token`)

#### POST /api/bl/presentation-requests/:id

Update a presentation request status.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "status": "fulfilled",
  "presentationId": "presentation-uuid"
}
```

#### DELETE /api/bl/presentation-requests/:id

Cancel a presentation request.

**Authentication**: Required (`x-id-token`)

---

### Contacts

#### GET /api/bl/contact

List all contacts for the authenticated user.

**Authentication**: Required (`x-id-token`)

**Response**

```json
{
  "success": true,
  "data": [
    {
      "id": "contact-uuid",
      "did": "did:sybol:tenant123:contact-user",
      "name": "Jane Smith",
      "relationship": "peer",
      "createdAt": "2026-03-10T12:00:00Z"
    }
  ]
}
```

#### GET /api/bl/contact/:id

Retrieve a specific contact.

**Authentication**: Required (`x-id-token`)

#### POST /api/bl/contact

Create a new contact.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "did": "did:sybol:tenant123:new-contact",
  "name": "Jane Smith",
  "relationship": "peer"
}
```

#### POST /api/bl/contact/connect

Initiate a connection request with another user.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "targetDid": "did:sybol:tenant123:target-user",
  "message": "Let's connect"
}
```

#### POST /api/bl/contact/:id

Update a contact.

**Authentication**: Required (`x-id-token`)

#### DELETE /api/bl/contact/:id

Delete a contact.

**Authentication**: Required (`x-id-token`)

---

### Delegates

#### POST /api/bl/delegates

Create a delegate (authorize another user to act on behalf).

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "delegator": "did:sybol:tenant123:user456",
  "delegate": "did:sybol:tenant123:delegate-user",
  "permissions": ["credentials:read", "credentials:issue"],
  "expiresAt": "2027-03-10T12:00:00Z"
}
```

#### GET /api/bl/delegates

List all delegates.

**Authentication**: Required (`x-id-token`)

---

### Activity

#### GET /api/bl/activity/system/status

Get system status and health metrics.

**Authentication**: Required (`x-id-token`)

**Response**

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "uptime": 86400,
    "activeUsers": 1523,
    "credentialsIssued24h": 342
  }
}
```

#### GET /api/bl/activity/metrics/:userId

Get activity metrics for a specific user.

**Authentication**: Required (`x-id-token`)

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `userId` | string | User DID or UUID |

**Response**

```json
{
  "success": true,
  "data": {
    "vc": 0,
    "prp": 0,
    "contacts": 0,
    "signatures": 0
  }
}
```

#### GET /api/bl/activity/alerts

Get system alerts and notifications.

**Authentication**: Required (`x-id-token`)

**Response**

```json
{
  "success": true,
  "data": [
    {
      "id": "alert-uuid",
      "type": "credential_expiring",
      "severity": "warning",
      "message": "3 credentials expiring in 7 days",
      "createdAt": "2026-03-10T12:00:00Z"
    }
  ]
}
```

#### POST /api/bl/activity/alerts/:id

Update alert status (mark as read/resolved).

**Authentication**: Required (`x-id-token`)

#### GET /api/bl/activity/recent

Get recent activity for the authenticated user.

**Authentication**: Required (`x-id-token`)

**Response**

```json
{
  "success": true,
  "data": [
    {
      "id": "activity-uuid",
      "type": "credential_issued",
      "credentialId": "credential-uuid",
      "timestamp": "2026-03-10T12:00:00Z"
    }
  ]
}
```

---

## W3C Verifiable Credentials Format

All credentials follow W3C VC Data Model 1.1:

```json
{
  "@context": [
    "https://www.w3.org/2018/credentials/v1",
    "https://www.w3.org/2018/credentials/examples/v1"
  ],
  "id": "http://example.edu/credentials/3732",
  "type": ["VerifiableCredential", "UniversityDegreeCredential"],
  "issuer": "did:sybol:tenant123:university",
  "issuanceDate": "2026-03-10T12:00:00Z",
  "expirationDate": "2027-03-10T12:00:00Z",
  "credentialSubject": {
    "id": "did:sybol:tenant123:student",
    "degree": {
      "type": "BachelorDegree",
      "name": "Bachelor of Science in Computer Science"
    }
  },
  "proof": {
    "type": "EcdsaSecp256k1Signature2019",
    "created": "2026-03-10T12:00:00Z",
    "verificationMethod": "did:sybol:tenant123:university#keys-1",
    "proofPurpose": "assertionMethod",
    "jws": "eyJhbGciOiJFUzI1NksifQ..."
  }
}
```

## Error Responses

See [Error Handling](error-handling.md) for complete error reference.

Common errors:

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `CREDENTIAL_NOT_FOUND` | 404 | Credential does not exist |
| `INVALID_CREDENTIAL_FORMAT` | 400 | Credential format does not conform to W3C spec |
| `CREDENTIAL_EXPIRED` | 422 | Credential has expired |
| `CREDENTIAL_REVOKED` | 422 | Credential has been revoked |
| `INVALID_PROOF` | 422 | Credential proof verification failed |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks permission for operation |

## Related Documentation

- [Authentication](authentication.md)
- [Catalog API](catalog-api.md)
- [W3C Verifiable Credentials Specification](https://www.w3.org/TR/vc-data-model/)
- [System Overview](../architecture/system-overview.md)
