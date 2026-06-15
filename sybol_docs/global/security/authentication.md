# Authentication

## Purpose

This page documents the authentication behavior that is verifiable in the current repository and the `CoreInfra` stack. It avoids presenting roadmap security posture as already enforced.

## Current Authentication Architecture

Sybol uses AWS Cognito for user authentication and token issuance. The base infrastructure in `infraestructure/CoreInfra/lib/sybol-core-stack.ts` provisions these core pieces:

- A Cognito User Pool
- A Cognito User Pool Client
- A Cognito Identity Pool
- An HTTP API JWT authorizer bound to the User Pool

Backend services then use Cognito-issued JWTs to authorize API requests, and some flows rely on STS-based tenant access patterns after token validation.

## Verified Cognito Configuration

### User Pool

| Setting | Current value in `CoreInfra` |
| ------- | ---------------------------- |
| Self sign-up | Enabled |
| Sign-in aliases | Email and username |
| Email required | Yes |
| Email auto verification | Yes |
| Password minimum length | 8 |
| Password complexity | Uppercase, lowercase, digits, and symbols required |
| MFA configuration | Not explicitly configured in the reviewed stack |
| Removal policy | Retain |

### Custom Attributes

The reviewed base User Pool defines only these custom attributes:

```json
{
   "custom:tenantId": "tenant identifier",
   "custom:role": "role name"
}
```

That means earlier references to `custom:organization` or a richer built-in authorization claim model were overstated.

### User Pool Client

The User Pool Client enables these auth flows:

- `adminUserPassword`
- `userPassword`
- `userSrp`
- `custom`

Configured token validity in the stack:

| Token | Lifetime |
| ----- | -------- |
| Access token | 1 hour |
| ID token | 1 hour |
| Refresh token | 30 days |

### Identity Pool

The Identity Pool disables unauthenticated identities, accepts the Cognito User Pool as provider, and attaches a basic authenticated role. That role supports authenticated platform access but is not itself the final tenant-scoped application role.

## API Authentication Model

### Gateway behavior

The HTTP API uses a JWT authorizer backed by the Cognito issuer and the configured User Pool Client audience.

### Service behavior

Service routes commonly enforce one of these patterns:

- `Authorization: Bearer <jwt>` validated by API Gateway and or service middleware
- `x-id-token` validation for specific internal or tenant-aware operations

The exact header contract varies by service and endpoint family, so route-specific details should stay in the API pages.

## Tenant Isolation and STS

Comments in `CoreInfra` and the `ClientInfra` onboarding documentation describe this intended model:

1. A user authenticates with Cognito.
2. The JWT carries tenant context.
3. Backend code extracts tenant role information and uses STS `AssumeRole`.
4. The backend accesses tenant-scoped resources with temporary credentials.

Current-state caveat:

- `ClientInfra` documentation references `custom:roleArn` during onboarding.
- The base User Pool reviewed in `CoreInfra` defines only `custom:tenantId` and `custom:role`.

So tenant-role propagation depends on onboarding or environment-specific behavior beyond the base Cognito stack definition.

## MFA Status

MFA is not enforced by the reviewed base Cognito stack.

What is present:

- `OnBoardingWeb` contains MFA-step UI state and related flow terminology.
- The technical-functional document treats MFA as a security objective.

What is not verified in the checked infrastructure:

- Required MFA for privileged users
- TOTP enforcement in the Cognito stack
- A complete end-to-end Cognito MFA enrollment flow as a platform default

MFA should therefore be described as partial or in-progress, not as a universally enforced control.

## Application Notes

### WWC

- Uses Cognito-related AWS SDK packages and JWT tooling
- Calls authenticated backend APIs across backoffice, businessLogic, catalog, and propagate

### OnBoardingWeb

- Tracks onboarding, MFA-step, and KYB-step state in React context
- Includes mocked status persistence in `src/services/Sybol.js`, so not all onboarding-state behavior should be described as server-backed today

## Documentation Corrections from This Review

The following claims were removed or downgraded in this pass:

- Minimum password length of 12
- Required MFA by role
- `custom:organization` as a current Cognito attribute
- Fully enforced TOTP as a platform default
- Fully self-contained tenant role resolution inside the base Cognito stack

## Related Documentation

- [Project Overview](../overview/project-overview.md)
- [System Overview](../architecture/system-overview.md)
- [Current State Audit](../current-state-audit.md)
