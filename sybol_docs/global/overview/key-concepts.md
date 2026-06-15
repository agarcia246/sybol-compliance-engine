# Key Concepts

This document explains the core concepts and domain terminology used throughout the Sybol platform.

## Verifiable Credentials & DIDs

### Verifiable Credential (VC)

A **Verifiable Credential** is a tamper-evident credential that has been cryptographically signed by an issuer. VCs are claims about a subject (person, organization, or thing) that can be independently verified without contacting the issuer.

**Key Properties**:
- **Cryptographically signed**: Uses digital signatures to ensure authenticity
- **Tamper-evident**: Any modification invalidates the signature
- **Machine-verifiable**: Can be automatically validated
- **Privacy-preserving**: Supports selective disclosure

**Example**: A renewable energy certificate stating that "Company X produced 1000 MWh of solar energy in January 2026."

**W3C Standard**: Sybol implements the [W3C Verifiable Credentials Data Model](https://www.w3.org/TR/vc-data-model/).

### Decentralized Identifier (DID)

A **DID** is a globally unique identifier that does not require a centralized registration authority. DIDs enable verifiable, self-sovereign digital identities.

**Format**: `did:sybol:{uuid}`

**Example**: `did:sybol:550e8400-e29b-41d4-a716-446655440000`

**DID Document**: A JSON-LD document containing public keys and service endpoints associated with a DID. Stored in the backoffice database and used to verify credential signatures.

### Issuer, Holder, Verifier

The three primary roles in the verifiable credentials ecosystem:

| Role | Description | Example |
|------|-------------|---------|
| **Issuer** | Entity that creates and signs verifiable credentials | Energy certification authority issuing GO certificates |
| **Holder** | Entity that receives, stores, and presents credentials | A renewable energy producer holding their GO certificates |
| **Verifier** | Entity that receives and validates presentations | An auditor checking the validity of GO certificates |

### Verifiable Presentation (VP)

A **Verifiable Presentation** is a collection of one or more verifiable credentials packaged together and signed by the holder. Used when a holder needs to prove claims to a verifier.

**Use Case**: A company presenting multiple credentials (business license, energy certificates, compliance attestations) to demonstrate eligibility for a program.

## Multi-Tenancy

### Tenant

A **tenant** is an isolated customer environment within the Sybol platform. Each tenant represents an organization (company, institution, etc.) that uses Sybol to issue or manage credentials.

**Tenant Properties**:
- Unique identifier (e.g., "repsol", "iberdrola")
- Isolated database (`tenant_{tenantId}`)
- Dedicated IAM roles and KMS keys
- Custom frontend branding and domain
- Independent user management

**Isolation Levels**:
- **Data**: Separate PostgreSQL databases per tenant
- **Compute**: Tenant-scoped IAM roles enforced via STS
- **Cryptography**: Tenant-specific KMS keys
- **Network**: CloudFront distributions per tenant

### Tenant Role

Within a tenant, users have roles that define their permissions:

| Role | Permissions | Use Case |
|------|-------------|----------|
| **admin** | Full read/write access to tenant data | Tenant administrators managing credentials |
| **reader** | Read-only access to tenant data | Auditors, compliance officers |

Roles are stored as custom attributes in AWS Cognito (`custom:role`) and enforced via IAM policies.

### Tenant Onboarding

The process of provisioning a new tenant includes:
1. Creating tenant domain and SSL certificate
2. Setting up CloudFront distribution and S3 bucket
3. Creating Cognito users with tenant attributes
4. Provisioning PostgreSQL database
5. Creating IAM roles and KMS keys
6. Registering DID document

See [Tenant Onboarding](../operations/tenant-onboarding.md) for detailed procedures.

## Authentication & Authorization

### Cognito User Pool

A centralized **user directory** managed by AWS Cognito. All users across all tenants are stored in a single User Pool, with tenant isolation enforced through custom attributes.

**Custom Attributes**:
- `custom:tenant_id`: Identifies which tenant the user belongs to
- `custom:role`: User's role within the tenant (admin, reader)

### Identity Pool

AWS Cognito Identity Pool that exchanges authenticated User Pool tokens for **temporary AWS credentials** via STS (Security Token Service).

### STS Assume Role

**Security Token Service (STS)** enables temporary, scoped access to AWS resources. Sybol uses STS to:
1. User authenticates with Cognito → receives JWT token
2. Backend assumes tenant-specific IAM role via STS
3. Temporary credentials grant access only to tenant's resources (database, KMS keys)

**Trust Policy**: Tenant IAM roles trust Cognito Identity Pool and specific Lambda execution roles.

**Tenant Isolation**: Each tenant has dedicated IAM roles (`TenantRole-{tenantId}-{role}`) that can only access their own resources.

## Data Model

### Document (formerly Origin)

A **Document** is a conceptual container representing a type of credential or certificate. Documents are versioned and define the structure and metadata for credentials.

**Example**: "Renewable Energy GO Certificate v2.0"

**Properties**:
- Version control
- Metadata schema
- Associated claims
- Compliance region mappings

### Claim (formerly Attribute)

A **Claim** is a reusable data field definition with validation rules. Claims are the building blocks of credentials.

**Example Claims**:
- `energy_production_kwh`: Numeric field for energy production
- `technology_type`: Enum field (solar, wind, hydro)
- `validity_period_start`: Date field

**Properties**:
- Data type (string, number, date, enum)
- Validation regex
- Required/optional
- Display name and description

### Form

A **Form** is a logical view over claims, organizing them into sections for data entry. Forms define the user interface for creating credential data.

**Structure**:
- Sections (grouping related claims)
- Fields (individual claims with UI metadata)
- Validation rules
- Conditional logic

### Compliance Region

A **Compliance Region** represents a jurisdiction or regulatory framework. Used to associate documents and credentials with applicable regulations.

**Examples**:
- European Union (EU)
- Spain
- eIDAS 2.0
- GO Certificates Regulation

**Hierarchy**: Regions can have parent-child relationships (e.g., Spain → EU).

## Credential Lifecycle

### Credential Request

A **Credential Request** is an application for a credential, submitted by a holder or issuer. Requests go through approval workflows before credentials are issued.

**States**:
- `pending`: Awaiting review
- `approved`: Request approved, credential can be issued
- `rejected`: Request denied
- `issued`: Credential has been created

### Credential Issuance

The process of creating a signed verifiable credential:
1. Validate credential data against claim definitions
2. Generate JWT payload following W3C VC format
3. Sign JWT using tenant's KMS key
4. Store credential in database with status `issued`

### Credential Revocation

Marking a credential as no longer valid. Revoked credentials should not be accepted by verifiers.

**Revocation Methods**:
- Status list (bitmap of revoked credential IDs)
- Timestamp-based revocation
- Revocation registry (blockchain-based)

### DIDLESS Credentials

**DIDLESS credentials** are credentials issued to subjects who do not yet have a DID. This supports bulk issuance scenarios where:
- Credentials are issued in advance
- Subjects claim credentials later by creating a DID
- Authentication via email, password, or challenge code

**Workflow**:
1. Issuer uploads credential data without DIDs
2. System creates DIDLESS credential records
3. Subject registers → creates DID
4. Subject claims credential → links to DID
5. Final VC issued with subject DID

## Integration Concepts

### KYB (Know Your Business)

Identity verification for business entities via **Sumsub** integration. Used during tenant onboarding to verify organization legitimacy.

**Workflow**:
1. Tenant provides business documents
2. Sumsub performs verification
3. Webhook updates KYB status in Sybol
4. Approval gate for tenant activation

### Propagate (Cross-Tenant Communication)

The **propagate service** enables secure communication between tenants via AWS EventBridge.

**Use Cases**:
- Cross-tenant credential sharing
- Notification of credential updates
- Multi-party workflows

**Security**: Messages are validated and only authorized tenants can send/receive events.

### PAdES Signing

**PAdES** (PDF Advanced Electronic Signature) is a standard for digitally signing PDF documents. Sybol includes a PAdES Lambda for:
- Signing PDF certificates
- Embedding metadata and form fields
- XMP metadata for compliance

## Operational Concepts

### Lambda Execution Role

Each Lambda function has an **execution role** that grants permissions to AWS resources (CloudWatch Logs, VPC access, etc.).

**Special Permissions**:
- `businessLogic` and `propagate` Lambdas have `AssumeRole` permissions to assume tenant roles
- Other Lambdas use default database credentials

### Secrets Manager

AWS Secrets Manager stores sensitive configuration:
- RDS database passwords (per tenant, per role)
- API keys for external services (Sumsub)
- KMS key references

**Secret Naming**: `tenant/{tenantId}/{role}-password`

### KMS Asymmetric Keys

AWS KMS keys used for signing JWTs and DID documents. Each tenant has dedicated keys per role.

**Key Spec**: `ECC_NIST_P256` (elliptic curve, suitable for JWT signing)

**Key Policy**: Restricts access to tenant-specific IAM roles only.

---

## Next Steps

- [Glossary](glossary.md) - Quick reference for terms and acronyms
- [System Overview](../architecture/system-overview.md) - How these concepts fit together
- [Data Architecture](../architecture/data-architecture.md) - Database schema details

---

*Last updated: March 2026*
