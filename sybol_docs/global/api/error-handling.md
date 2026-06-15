# Error Handling

## Purpose

This document defines the standardized error response format, common error codes, HTTP status code usage, and debugging guidelines for the Sybol platform APIs.

## Context

Consistent error handling enables clients to programmatically handle errors, improves debugging efficiency, and provides clear user-facing error messages.

## Error Response Format

All API errors follow a standardized JSON structure:

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Human-readable error description",
  "details": {
    "field": "Additional error context",
    "validation": "Specific validation failure"
  },
  "timestamp": "2026-03-10T12:00:00Z",
  "requestId": "request-uuid",
  "path": "/api/bl/credentials"
}
```

### Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `success` | boolean | Yes | Always `false` for errors |
| `error` | string | Yes | Machine-readable error code (uppercase snake_case) |
| `message` | string | Yes | Human-readable error description |
| `details` | object | No | Additional error context (field-specific validation errors) |
| `timestamp` | string | Yes | Error timestamp (ISO 8601) |
| `requestId` | string | Yes | Unique request identifier for tracing |
| `path` | string | Yes | API endpoint path |

## HTTP Status Codes

The platform uses standard HTTP status codes consistently across all services.

### 2xx Success

| Code | Name | Usage |
|------|------|-------|
| `200` | OK | Successful GET, POST (update), or DELETE request |
| `201` | Created | Resource successfully created |
| `204` | No Content | Successful request with no response body |

### 4xx Client Errors

| Code | Name | Usage |
|------|------|-------|
| `400` | Bad Request | Invalid request format, missing required fields, malformed JSON |
| `401` | Unauthorized | Missing or invalid authentication token |
| `403` | Forbidden | Authenticated but insufficient permissions |
| `404` | Not Found | Requested resource does not exist |
| `405` | Method Not Allowed | HTTP method not supported for endpoint |
| `409` | Conflict | Resource already exists or version conflict |
| `413` | Payload Too Large | Request body exceeds size limit |
| `422` | Unprocessable Entity | Request format valid but semantic validation failed |
| `429` | Too Many Requests | Rate limit exceeded |

### 5xx Server Errors

| Code | Name | Usage |
|------|------|-------|
| `500` | Internal Server Error | Unexpected server-side error |
| `502` | Bad Gateway | Upstream service error |
| `503` | Service Unavailable | Service temporarily unavailable (maintenance, overload) |
| `504` | Gateway Timeout | Upstream service timeout |

## Error Categories

Errors are organized into logical categories by service and functionality.

### Authentication Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `AUTH_REQUIRED` | 401 | Authentication required but not provided |
| `INVALID_TOKEN` | 401 | JWT token is invalid or malformed |
| `TOKEN_EXPIRED` | 401 | JWT token has expired |
| `INVALID_SIGNATURE` | 401 | JWT signature verification failed |
| `MISSING_AUTHORIZATION` | 401 | `Authorization` header missing |
| `MISSING_ID_TOKEN` | 401 | `x-id-token` header required but missing |
| `MISSING_TENANT_ID` | 400 | Token missing required `custom:tenant_id` claim |
| `INVALID_TENANT` | 403 | Tenant ID in token does not match resource |
| `TENANT_SUSPENDED` | 403 | Tenant account is suspended |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions for operation |
| `NOT_SYBOL_TENANT` | 403 | Operation restricted to Sybol administrative tenant |

**Example**

```json
{
  "success": false,
  "error": "TOKEN_EXPIRED",
  "message": "Authentication token has expired. Please refresh your token.",
  "timestamp": "2026-03-10T12:00:00Z",
  "requestId": "req-12345",
  "path": "/api/bl/credentials"
}
```

---

### Validation Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `VALIDATION_FAILED` | 422 | Request validation failed |
| `MISSING_REQUIRED_FIELD` | 400 | Required field missing from request |
| `INVALID_FIELD_FORMAT` | 400 | Field format is invalid |
| `INVALID_FIELD_VALUE` | 400 | Field value is invalid or out of range |
| `FIELD_TOO_LONG` | 400 | Field exceeds maximum length |
| `FIELD_TOO_SHORT` | 400 | Field below minimum length |
| `INVALID_EMAIL` | 400 | Email format is invalid |
| `INVALID_DATE_FORMAT` | 400 | Date format is invalid (expected ISO 8601) |
| `INVALID_DID_FORMAT` | 400 | DID format is invalid |
| `INVALID_JSON` | 400 | Request body is not valid JSON |

**Example**

```json
{
  "success": false,
  "error": "VALIDATION_FAILED",
  "message": "Request validation failed",
  "details": {
    "credentialSubject.dateOfBirth": "Date format is invalid. Expected YYYY-MM-DD.",
    "credentialSubject.name": "Name is required and cannot be empty."
  },
  "timestamp": "2026-03-10T12:00:00Z",
  "requestId": "req-12345",
  "path": "/api/bl/credentials"
}
```

---

### Resource Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `RESOURCE_NOT_FOUND` | 404 | Requested resource does not exist |
| `CREDENTIAL_NOT_FOUND` | 404 | Credential not found |
| `PRESENTATION_NOT_FOUND` | 404 | Presentation not found |
| `DID_NOT_FOUND` | 404 | DID document not found |
| `CATALOG_ENTRY_NOT_FOUND` | 404 | Catalog entry not found |
| `TENANT_NOT_FOUND` | 404 | Tenant not found |
| `USER_NOT_FOUND` | 404 | User not found |
| `RESOURCE_ALREADY_EXISTS` | 409 | Resource with same identifier already exists |
| `DID_ALREADY_EXISTS` | 409 | DID document already exists |
| `DUPLICATE_ENTRY` | 409 | Duplicate entry conflicts with existing resource |

**Example**

```json
{
  "success": false,
  "error": "CREDENTIAL_NOT_FOUND",
  "message": "Credential with ID '550e8400-e29b-41d4-a716-446655440000' not found.",
  "details": {
    "credentialId": "550e8400-e29b-41d4-a716-446655440000"
  },
  "timestamp": "2026-03-10T12:00:00Z",
  "requestId": "req-12345",
  "path": "/api/bl/credentials/550e8400-e29b-41d4-a716-446655440000"
}
```

---

### Credential Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_CREDENTIAL_FORMAT` | 400 | Credential does not conform to W3C VC spec |
| `INVALID_CREDENTIAL_TYPE` | 400 | Credential type is not recognized |
| `CREDENTIAL_EXPIRED` | 422 | Credential has expired |
| `CREDENTIAL_REVOKED` | 422 | Credential has been revoked |
| `CREDENTIAL_NOT_ACTIVE` | 422 | Credential is not in active status |
| `INVALID_PROOF` | 422 | Credential proof verification failed |
| `INVALID_SIGNATURE` | 422 | Credential signature is invalid |
| `ISSUER_MISMATCH` | 422 | Credential issuer does not match expected issuer |
| `SUBJECT_MISMATCH` | 422 | Credential subject does not match holder |
| `MISSING_PROOF` | 400 | Credential missing required proof |

**Example**

```json
{
  "success": false,
  "error": "CREDENTIAL_REVOKED",
  "message": "Credential has been revoked and cannot be used.",
  "details": {
    "credentialId": "credential-uuid",
    "revokedAt": "2026-03-09T10:00:00Z",
    "revocationReason": "Credential compromised"
  },
  "timestamp": "2026-03-10T12:00:00Z",
  "requestId": "req-12345",
  "path": "/api/bl/credentials/credential-uuid"
}
```

---

### Presentation Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_PRESENTATION_FORMAT` | 400 | Presentation does not conform to W3C VP spec |
| `PRESENTATION_VERIFICATION_FAILED` | 422 | Presentation verification failed |
| `INVALID_CHALLENGE` | 422 | Challenge value does not match |
| `INVALID_DOMAIN` | 422 | Domain value does not match |
| `PRESENTATION_EXPIRED` | 422 | Presentation challenge has expired |
| `MISSING_CREDENTIALS` | 400 | Presentation missing required credentials |
| `CREDENTIAL_NOT_IN_PRESENTATION` | 422 | Expected credential not found in presentation |

---

### Database Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `DATABASE_ERROR` | 500 | Database operation failed |
| `DATABASE_CONNECTION_FAILED` | 503 | Cannot connect to database |
| `QUERY_FAILED` | 500 | Database query execution failed |
| `TRANSACTION_FAILED` | 500 | Database transaction failed |
| `CONSTRAINT_VIOLATION` | 409 | Database constraint violation |
| `DEADLOCK_DETECTED` | 409 | Database deadlock detected |

**Example**

```json
{
  "success": false,
  "error": "DATABASE_CONNECTION_FAILED",
  "message": "Unable to connect to tenant database. Please try again.",
  "timestamp": "2026-03-10T12:00:00Z",
  "requestId": "req-12345",
  "path": "/api/bl/credentials"
}
```

---

### AWS Service Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `STS_ASSUME_ROLE_FAILED` | 500 | AWS STS AssumeRole operation failed |
| `SECRETS_MANAGER_ERROR` | 500 | AWS Secrets Manager operation failed |
| `KMS_ERROR` | 500 | AWS KMS operation failed |
| `EVENTBRIDGE_ERROR` | 500 | AWS EventBridge operation failed |
| `COGNITO_ERROR` | 500 | AWS Cognito operation failed |
| `S3_ERROR` | 500 | AWS S3 operation failed |
| `AWS_SERVICE_UNAVAILABLE` | 503 | AWS service temporarily unavailable |

---

### Sumsub (KYB) Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `SUMSUB_ERROR` | 500 | Sumsub service error |
| `SUMSUB_TOKEN_GENERATION_FAILED` | 500 | Failed to generate Sumsub token |
| `SUMSUB_WEBHOOK_VALIDATION_FAILED` | 400 | Sumsub webhook signature validation failed |
| `KYB_NOT_FOUND` | 404 | KYB record not found |
| `KYB_PENDING` | 422 | KYB verification pending |
| `KYB_REJECTED` | 422 | KYB verification rejected |

---

### Rate Limiting Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `RATE_LIMIT_EXCEEDED` | 429 | API rate limit exceeded |
| `TOO_MANY_REQUESTS` | 429 | Too many requests from IP or user |
| `QUOTA_EXCEEDED` | 429 | Tenant quota exceeded |

**Example**

```json
{
  "success": false,
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded. Please retry after 60 seconds.",
  "details": {
    "limit": 100,
    "remaining": 0,
    "resetAt": "2026-03-10T12:01:00Z"
  },
  "timestamp": "2026-03-10T12:00:00Z",
  "requestId": "req-12345",
  "path": "/api/bl/credentials"
}
```

**Response Headers**

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1709467260
Retry-After: 60
```

---

### EventBridge Propagate Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_EVENT_FORMAT` | 400 | Event does not conform to schema |
| `EVENT_TOO_LARGE` | 413 | Event exceeds maximum size (256 KB) |
| `TARGET_TENANT_NOT_FOUND` | 404 | Target tenant does not exist |
| `EVENT_BUS_NOT_FOUND` | 404 | EventBridge bus not found |
| `EVENT_DELIVERY_FAILED` | 500 | Event delivery failed |

---

### Catalog Errors

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_SCHEMA` | 400 | JSON schema validation failed |
| `RESOURCE_IN_USE` | 409 | Cannot delete resource referenced by active records |
| `CATALOG_ENTRY_NOT_FOUND` | 404 | Catalog entry not found |
| `FORM_VALIDATION_FAILED` | 422 | Form input validation failed |

---

## Error Handling Best Practices

### Client-Side Handling

**Check HTTP Status Code First**

```javascript
try {
  const response = await fetch('/api/bl/credentials', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'x-id-token': idToken,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(credentialData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    
    // Handle specific error codes
    switch (error.error) {
      case 'TOKEN_EXPIRED':
        await refreshToken();
        return retryRequest();
      
      case 'VALIDATION_FAILED':
        displayValidationErrors(error.details);
        break;
      
      case 'RATE_LIMIT_EXCEEDED':
        const retryAfter = response.headers.get('Retry-After');
        await delay(retryAfter * 1000);
        return retryRequest();
      
      default:
        displayGenericError(error.message);
    }
  }
  
  const data = await response.json();
  return data;
  
} catch (error) {
  // Network error
  displayNetworkError('Unable to connect to server');
}
```

**Retry Logic for Transient Errors**

```javascript
const RETRYABLE_ERRORS = [
  'DATABASE_CONNECTION_FAILED',
  'AWS_SERVICE_UNAVAILABLE',
  'GATEWAY_TIMEOUT'
];

async function retryableRequest(url, options, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);
      
      if (response.ok) {
        return await response.json();
      }
      
      if (response.status >= 500) {
        const error = await response.json();
        
        if (RETRYABLE_ERRORS.includes(error.error) && attempt < maxRetries) {
          const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
          await sleep(delay);
          continue;
        }
      }
      
      throw new Error(`Request failed: ${response.status}`);
      
    } catch (error) {
      if (attempt === maxRetries) throw error;
    }
  }
}
```

### Server-Side Error Handling

**Consistent Error Response Generation**

```javascript
class APIError extends Error {
  constructor(error, message, statusCode = 500, details = null) {
    super(message);
    this.error = error;
    this.statusCode = statusCode;
    this.details = details;
  }
}

// Error handler middleware
function errorHandler(err, req, res, next) {
  const response = {
    success: false,
    error: err.error || 'INTERNAL_ERROR',
    message: err.message || 'An unexpected error occurred',
    timestamp: new Date().toISOString(),
    requestId: req.id,
    path: req.path
  };
  
  if (err.details) {
    response.details = err.details;
  }
  
  // Log error for debugging
  logger.error('API Error', {
    error: err.error,
    message: err.message,
    stack: err.stack,
    requestId: req.id,
    path: req.path,
    userId: req.auth?.userId
  });
  
  res.status(err.statusCode || 500).json(response);
}

// Usage
app.post('/api/bl/credentials', async (req, res, next) => {
  try {
    const credential = await createCredential(req.body);
    res.status(201).json({ success: true, data: credential });
  } catch (error) {
    if (error.code === 'VALIDATION_ERROR') {
      next(new APIError('VALIDATION_FAILED', error.message, 422, error.details));
    } else {
      next(new APIError('INTERNAL_ERROR', 'Failed to create credential', 500));
    }
  }
});
```

---

## Debugging Tips

### Request ID Tracing

Every error includes a unique `requestId`. Use this ID to trace the complete request lifecycle across services.

**CloudWatch Logs Insights Query**

```sql
fields @timestamp, @message
| filter requestId = "req-12345"
| sort @timestamp asc
```

### Enable Debug Mode

For development environments, set debug mode header:

```http
X-Debug-Mode: true
```

Response includes additional debugging information:

```json
{
  "success": false,
  "error": "DATABASE_ERROR",
  "message": "Database query failed",
  "details": { ... },
  "debug": {
    "query": "SELECT * FROM credentials WHERE id = $1",
    "params": ["credential-uuid"],
    "errorCode": "42P01",
    "stack": "Error: relation does not exist..."
  }
}
```

**Note**: Debug mode is disabled in production.

### Common Debugging Scenarios

**Token Issues**

1. Decode JWT token at [jwt.io](https://jwt.io)
2. Verify `exp` claim is in future
3. Verify `custom:tenant_id` matches target tenant
4. Check token signature using Cognito public keys

**Database Connection Issues**

1. Verify tenant IAM role exists
2. Confirm Secrets Manager entry: `tenant/{tenantId}/{role}-password`
3. Check RDS security group allows Lambda access
4. Verify database credentials are valid

**EventBridge Issues**

1. Check CloudWatch Logs for event delivery failures
2. Verify EventBridge rule pattern matches event
3. Confirm target Lambda has correct permissions
4. Monitor Dead Letter Queue for failed events

---

## Error Monitoring

### CloudWatch Metrics

Monitor error rates per service:

| Metric | Description |
|--------|-------------|
| `APIErrors` | Total API errors |
| `AuthErrors` | Authentication failures |
| `ValidationErrors` | Validation failures |
| `ServerErrors` | 5xx server errors |

### Alarms

Set CloudWatch alarms for:
- Error rate > 5% of total requests
- Authentication failures > 10 per minute
- Database connection failures
- AWS service errors

### Error Reporting

Integrate with error tracking services:
- **Sentry**: Real-time error tracking
- **Rollbar**: Error monitoring and alerting
- **AWS X-Ray**: Distributed tracing

---

## Related Documentation

- [API Overview](README.md)
- [Authentication](authentication.md)
- [Security Architecture](../architecture/security-architecture.md)
