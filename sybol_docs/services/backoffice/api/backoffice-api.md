# Backoffice API

## Purpose

The Backoffice API provides endpoints for user authentication, KYB (Know Your Business) verification via Sumsub, billing management, and DID document operations.

## Context

The Backoffice service handles platform administration, tenant onboarding, and identity verification workflows. All endpoints are prefixed with `/api/bo/`.

**Base Path**: `/api/bo/*`

## Authentication Requirements

| Endpoint | Authentication Mode | Description |
|----------|---------------------|-------------|
| Health check | None | Public endpoint |
| KYB endpoints | Optional | Uses tenant DB if `x-id-token` provided |
| DID document GET | Optional | Uses tenant DB if `x-id-token` provided |
| DID document POST/DELETE | Required | Always uses tenant DB |
| KYB webhook | None | Sumsub callback endpoint |

## Endpoints

### Health Check

#### GET /api/bo/health

Check service health status.

**Authentication**: None

**Response**

```json
{
  "success": true,
  "service": "backoffice",
  "status": "healthy",
  "timestamp": "2026-03-10T12:00:00Z"
}
```

---

### Authentication

Note: Authentication endpoints are currently not exposed in the Backoffice API routes. Auth operations are handled directly via AWS Cognito SDK in client applications.

For authentication flows, see [Authentication Documentation](authentication.md).

---

### KYB (Know Your Business)

#### POST /api/bo/kyb

Generate Sumsub verification token for a user.

**Authentication**: Optional (`x-id-token`)

**Request Body**

```json
{
  "userId": "user-uuid",
  "level": "basic"
}
```

**Response**

```json
{
  "success": true,
  "data": {
    "token": "sbx:TOKEN_STRING",
    "userId": "user-uuid",
    "expiresAt": "2026-03-10T13:00:00Z"
  }
}
```

**cURL Example**

```bash
curl -X POST https://api.sybol.io/api/bo/kyb \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "x-id-token: ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "level": "basic"
  }'
```

#### GET /api/bo/kyb

Retrieve KYB verification status for a user.

**Authentication**: Optional (`x-id-token`)

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userId` | string | Yes | User UUID |

**Response**

```json
{
  "success": true,
  "data": {
    "userId": "user-uuid",
    "status": "approved",
    "reviewStatus": "completed",
    "updatedAt": "2026-03-10T12:00:00Z"
  }
}
```

**Status Values**

| Status | Description |
|--------|-------------|
| `pending` | Verification in progress |
| `approved` | Verification successful |
| `rejected` | Verification failed |
| `init` | Not started |

**cURL Example**

```bash
curl -X GET "https://api.sybol.io/api/bo/kyb?userId=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "x-id-token: ID_TOKEN"
```

#### POST /api/bo/kyb/webhook

Receive KYB status updates from Sumsub.

**Authentication**: None (Sumsub callback)

**Request Body**

```json
{
  "applicantId": "user-uuid",
  "reviewStatus": "completed",
  "reviewResult": {
    "reviewAnswer": "GREEN"
  },
  "type": "applicantReviewed"
}
```

**Response**

```json
{
  "success": true,
  "message": "Webhook processed"
}
```

**Note**: This endpoint validates Sumsub webhook signatures. Configure webhook URL in Sumsub dashboard.

---

### Billing

Note: Billing endpoints are referenced in README but not currently implemented in routes. Implementation pending.

Expected endpoints:

#### POST /api/bo/billing

Store billing information for a user.

**Request Body**

```json
{
  "userId": "user-uuid",
  "billingData": {
    "companyName": "Example Corp",
    "taxId": "12345678",
    "address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "country": "US",
      "postalCode": "94105"
    }
  }
}
```

#### GET /api/bo/billing

Retrieve billing information.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userId` | string | Yes | User UUID |

---

### DID Documents

#### POST /api/bo/did-document

Create a new DID document.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "did": "did:sybol:tenant123:user456",
  "document": {
    "@context": [
      "https://www.w3.org/ns/did/v1"
    ],
    "id": "did:sybol:tenant123:user456",
    "verificationMethod": [{
      "id": "did:sybol:tenant123:user456#keys-1",
      "type": "EcdsaSecp256k1VerificationKey2019",
      "controller": "did:sybol:tenant123:user456",
      "publicKeyJwk": {
        "kty": "EC",
        "crv": "secp256k1",
        "x": "...",
        "y": "..."
      }
    }]
  }
}
```

**Response**

```json
{
  "success": true,
  "data": {
    "did": "did:sybol:tenant123:user456",
    "created_at": "2026-03-10T12:00:00Z"
  }
}
```

**HTTP Status Codes**

| Code | Description |
|------|-------------|
| `201` | DID document created |
| `400` | Invalid DID format or document structure |
| `409` | DID already exists |

**cURL Example**

```bash
curl -X POST https://api.sybol.io/api/bo/did-document \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "x-id-token: ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "did": "did:sybol:tenant123:user456",
    "document": {
      "@context": ["https://www.w3.org/ns/did/v1"],
      "id": "did:sybol:tenant123:user456"
    }
  }'
```

#### GET /api/bo/did-document/:did

Retrieve a DID document by identifier.

**Authentication**: Optional (`x-id-token`)

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `did` | string | Fully qualified DID (URL encoded) |

**Response**

```json
{
  "success": true,
  "data": {
    "did": "did:sybol:tenant123:user456",
    "document": {
      "@context": ["https://www.w3.org/ns/did/v1"],
      "id": "did:sybol:tenant123:user456",
      "verificationMethod": [...]
    },
    "created_at": "2026-03-10T12:00:00Z",
    "updated_at": "2026-03-10T12:00:00Z"
  }
}
```

**cURL Example**

```bash
curl -X GET "https://api.sybol.io/api/bo/did-document/did%3Asymbol%3Atenant123%3Auser456" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

#### GET /api/bo/did-document

List all DID documents with optional filters.

**Authentication**: Optional (`x-id-token`)

**Query Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `tenant_id` | string | Filter by tenant |
| `limit` | integer | Results per page (max 100) |
| `cursor` | string | Pagination cursor |

**Response**

```json
{
  "success": true,
  "data": [
    {
      "did": "did:sybol:tenant123:user456",
      "created_at": "2026-03-10T12:00:00Z"
    }
  ],
  "pagination": {
    "limit": 20,
    "hasMore": true,
    "nextCursor": "eyJpZCI6MTIzfQ=="
  }
}
```

#### POST /api/bo/did-document/:did

Update an existing DID document.

**Authentication**: Required (`x-id-token`)

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `did` | string | Fully qualified DID (URL encoded) |

**Request Body**

```json
{
  "document": {
    "@context": ["https://www.w3.org/ns/did/v1"],
    "id": "did:sybol:tenant123:user456",
    "verificationMethod": [...]
  }
}
```

**Response**

```json
{
  "success": true,
  "data": {
    "did": "did:sybol:tenant123:user456",
    "updated_at": "2026-03-10T12:30:00Z"
  }
}
```

#### DELETE /api/bo/did-document/:did

Delete a DID document.

**Authentication**: Required (`x-id-token`)

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `did` | string | Fully qualified DID (URL encoded) |

**Response**

```json
{
  "success": true,
  "message": "DID document deleted"
}
```

**HTTP Status Codes**

| Code | Description |
|------|-------------|
| `200` | DID document deleted |
| `404` | DID document not found |
| `403` | Insufficient permissions |

---

### Email

#### POST /api/bo/email

Send email via service.

**Authentication**: Required (`x-id-token`)

**Request Body**

```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email content",
  "template": "welcome"
}
```

**Response**

```json
{
  "success": true,
  "messageId": "message-id-123"
}
```

---

## Error Responses

See [Error Handling](error-handling.md) for complete error reference.

Common errors:

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_TOKEN` | 401 | Invalid or expired authentication token |
| `MISSING_TENANT_ID` | 400 | `x-id-token` missing required `custom:tenant_id` claim |
| `DID_ALREADY_EXISTS` | 409 | DID document already exists |
| `DID_NOT_FOUND` | 404 | DID document not found |
| `SUMSUB_ERROR` | 500 | Sumsub service error |

## Related Documentation

- [Authentication](authentication.md)
- [Security Architecture](../architecture/security-architecture.md)
- [Multi-Tenancy](../architecture/multi-tenancy.md)
