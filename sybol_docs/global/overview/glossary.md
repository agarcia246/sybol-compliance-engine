# Glossary

Quick reference for terms, acronyms, and technical vocabulary used in the Sybol platform.

## A

**ACM (AWS Certificate Manager)**  
AWS service for provisioning and managing SSL/TLS certificates. Used for HTTPS on CloudFront and API Gateway.

**ADR (Architecture Decision Record)**  
Document capturing an important architectural decision, its context, and consequences. See [Decision Records](../decisions/README.md).

**API Gateway**  
AWS service providing RESTful HTTP APIs with authentication, throttling, and Lambda integration.

**Assume Role**  
AWS STS operation allowing an entity to temporarily obtain credentials for a different IAM role. Core mechanism for tenant isolation.

**Attribute**  
**[DEPRECATED]** Former term for Claim. See "Claim".

## B

**Backoffice Service**  
Sybol microservice handling user onboarding, authentication, KYB verification, and billing.

**Business Logic Service**  
Sybol microservice managing verifiable credentials, credential requests, presentations, and presentation requests.

## C

**Catalog Service**  
Sybol microservice providing document templates, claim definitions, forms, and compliance regions.

**CDK (AWS Cloud Development Kit)**  
Infrastructure as Code framework used to define AWS resources in TypeScript. Used in `CoreInfra` and `ClientInfra`.

**Claim**  
Reusable data field definition with validation rules. Building block of credentials. Example: `energy_production_kwh`.

**CloudFront**  
AWS CDN service for distributing frontend applications globally with low latency.

**Cognito**  
AWS managed authentication service. Sybol uses Cognito User Pools for user directories and Identity Pools for AWS credentials.

**Compliance Region**  
Jurisdiction or regulatory framework associated with documents. Examples: EU, Spain, eIDAS 2.0.

**Credential Request**  
Application for a verifiable credential, submitted by a holder or issuer. Goes through approval workflows.

**CUPS**  
Universal Supply Point Code - identifier for energy supply points in Spain. Often used in energy certificates.

## D

**DID (Decentralized Identifier)**  
Globally unique identifier not requiring a centralized authority. Format: `did:sybol:{uuid}`.

**DIDLESS Credential**  
Credential issued to a subject without a DID yet. Subject claims it later after DID creation.

**DID Document**  
JSON-LD document containing public keys and service endpoints for a DID. Used to verify signatures.

**Document**  
Conceptual container for a type of credential. Represents versioned credential templates. (Formerly "Origin")

## E

**ECR (Elastic Container Registry)**  
AWS Docker registry for storing Lambda container images.

**eIDAS (electronic IDentification, Authentication and trust Services)**  
EU regulation for electronic identification and trust services. eIDAS 2.0 adds verifiable credentials support.

**EventBridge**  
AWS event bus service for application integration. Used by propagate service for cross-tenant communication.

## F

**Form**  
Logical view over claims, organizing them into sections for data entry. Defines credential input UI.

## G

**GDPR (General Data Protection Regulation)**  
EU regulation on data privacy and protection. Sybol is designed for GDPR compliance.

**GO (Guarantee of Origin)**  
Certificate proving that energy was produced from renewable sources. Common use case for Sybol.

## H

**Holder**  
Entity that receives, stores, and presents verifiable credentials. One of three primary VC roles.

**HTTP API**  
API Gateway type using HTTP protocol (AWS API Gateway v2). More cost-effective than REST API.

## I

**IAM (Identity and Access Management)**  
AWS service for managing permissions. Sybol uses IAM roles for tenant isolation.

**Identity Pool**  
Cognito service that exchanges JWT tokens for temporary AWS credentials via STS.

**Issuer**  
Entity that creates and signs verifiable credentials. One of three primary VC roles.

## J

**JWT (JSON Web Token)**  
Compact, URL-safe token format used for authentication and encoding verifiable credentials.

## K

**KMS (Key Management Service)**  
AWS service for creating and managing cryptographic keys. Sybol uses KMS asymmetric keys (ECC_NIST_P256) for signing credentials.

**KYB (Know Your Business)**  
Business identity verification process. Sybol integrates with Sumsub for KYB checks.

## L

**Lambda**  
AWS serverless compute service. Sybol microservices run as Lambda functions with container images.

## M

**MAU (Monthly Active Users)**  
Pricing metric for Cognito. Free tier: 50,000 MAU.

**MFA (Multi-Factor Authentication)**  
Authentication requiring multiple verification methods. Supported via Cognito with TOTP.

**Multi-Tenant**  
Architecture pattern where a single application instance serves multiple customers (tenants) with data isolation.

## N

**NAT Gateway**  
AWS service for enabling internet access from private subnets. **Not used** in Sybol (public subnets with Lambda auto-assigned IPs).

## O

**OAC (Origin Access Control)**  
CloudFront feature restricting S3 bucket access to only CloudFront. Ensures direct S3 access is blocked.

**OpenID Connect (OIDC)**  
Identity layer on top of OAuth 2.0. Supported by Cognito.

**Origin**  
**[DEPRECATED]** Former term for Document. See "Document".

## P

**PAdES (PDF Advanced Electronic Signature)**  
Standard for digitally signing PDF documents. Sybol PAdES Lambda provides PDF signing capabilities.

**Presentation**  
See Verifiable Presentation.

**Propagate Service**  
Sybol microservice handling cross-tenant event communication via EventBridge.

**PostgreSQL**  
Open-source relational database. Sybol uses RDS PostgreSQL 17.4 with JSONB for flexible credential storage.

## R

**RDS (Relational Database Service)**  
AWS managed database service. Sybol uses RDS PostgreSQL with multi-AZ for high availability.

**Role (IAM)**  
AWS identity with specific permissions. Sybol tenants have dedicated roles like `TenantRole-{tenantId}-admin`.

**Role (User)**  
Permission level within a tenant. Examples: `admin` (full access), `reader` (read-only).

## S

**S3 (Simple Storage Service)**  
AWS object storage. Used for frontend static assets.

**Secrets Manager**  
AWS service for storing sensitive data like database passwords. Secret naming: `tenant/{tenantId}/{role}-password`.

**Security Group**  
AWS firewall rules for VPC resources. Sybol uses `lambda-sg` and `rds-sg`.

**Serverless**  
Cloud computing model where cloud provider manages infrastructure. Sybol uses Lambda, API Gateway, RDS Serverless-compatible.

**SOC 2 (Service Organization Control 2)**  
Auditing standard for security, availability, and confidentiality. AWS services are SOC 2 compliant.

**SRP (Secure Remote Password)**  
Authentication protocol that doesn't transmit passwords. Cognito supports SRP authentication flow.

**STS (Security Token Service)**  
AWS service providing temporary, limited-privilege credentials via `AssumeRole`.

**Subject**  
Entity that a credential makes claims about. Can be a person, organization, or thing.

**Subnet**  
Network segment within a VPC. Sybol uses public subnets in multiple availability zones.

**Sumsub**  
Third-party KYB/KYC verification service integrated with Sybol for business identity verification.

## T

**Tenant**  
Isolated customer environment within Sybol. Each tenant has separate database, IAM roles, KMS keys, and frontend.

**Tenant ID**  
Unique identifier for a tenant. Examples: `repsol`, `iberdrola`, `sybol`.

**TOTP (Time-based One-Time Password)**  
Algorithm for generating temporary authentication codes. Used for MFA via authenticator apps.

**Trust Policy**  
IAM policy attached to a role defining which entities can assume the role.

## U

**User Pool**  
Cognito user directory storing user accounts. Single User Pool serves all Sybol tenants with tenant isolation via custom attributes.

## V

**VC (Verifiable Credential)**  
Cryptographically signed credential following W3C standard. Core data object in Sybol.

**Verifier**  
Entity that receives and validates verifiable presentations. One of three primary VC roles.

**Verifiable Presentation (VP)**  
Collection of one or more VCs packaged and signed by the holder. Used when proving claims to a verifier.

**VPC (Virtual Private Cloud)**  
Isolated AWS network. Sybol uses a VPC with public subnets for Lambda and RDS networking.

## W

**W3C (World Wide Web Consortium)**  
International standards organization. Publishes Verifiable Credentials and DID specifications.

**Wallet**  
Application for storing and managing verifiable credentials. Sybol includes a web wallet (`wwc`).

**wwc (Wallet Web Client)**  
Sybol's React-based web application for holders to manage credentials.

## X

**XMP (Extensible Metadata Platform)**  
Metadata standard for embedding information in files. Used in PAdES-signed PDFs for compliance metadata.

---

## Symbol Conventions

Throughout the documentation:

- `{tenantId}` - Placeholder for tenant identifier (e.g., `repsol`)
- `{role}` - Placeholder for user role (e.g., `admin`, `reader`)
- `{uuid}` - Placeholder for UUID
- `/api/bo/*` - Base path for backoffice API
- `/api/bl/*` - Base path for business logic API
- `did:sybol:*` - DID format for Sybol platform

---

## Related Documentation

- [Key Concepts](key-concepts.md) - Detailed explanation of core concepts
- [API Overview](../api/README.md) - API endpoints and authentication
- [Security Architecture](../architecture/security-architecture.md) - Security model details

---

*Last updated: March 2026*
