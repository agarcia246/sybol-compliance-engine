# Concept Index

## Purpose

Comprehensive index of all key concepts, domain terminology, and technical entities extracted from Sybol documentation. This index provides definitions, primary sources, and cross-references for navigating the knowledge base.

**Total Concepts:** 87  
**Last Updated:** March 10, 2026

---

## Core Verifiable Credentials Concepts

| Concept | Definition | Primary Source | Related Docs |
|---------|-----------|----------------|--------------|
| **Verifiable Credential (VC)** | Tamper-evident credential cryptographically signed by an issuer, containing claims about a subject | [key-concepts.md](../overview/key-concepts.md) | [0004-w3c-verifiable-credentials.md](../decisions/0004-w3c-verifiable-credentials.md), [businesslogic-api.md](../api/businesslogic-api.md) |
| **Decentralized Identifier (DID)** | Globally unique identifier not requiring centralized registration authority (format: `did:sybol:{uuid}`) | [key-concepts.md](../overview/key-concepts.md) | [security-architecture.md](../architecture/security-architecture.md), [cryptography.md](../security/cryptography.md) |
| **DID Document** | JSON-LD document containing public keys and service endpoints for a DID | [key-concepts.md](../overview/key-concepts.md) | [backoffice-api.md](../api/backoffice-api.md) |
| **Issuer** | Entity that creates and signs verifiable credentials | [key-concepts.md](../overview/key-concepts.md) | [project-overview.md](../overview/project-overview.md), [component-architecture.md](../architecture/component-architecture.md) |
| **Holder** | Entity that receives, stores, and presents credentials | [key-concepts.md](../overview/key-concepts.md) | [project-overview.md](../overview/project-overview.md), [businesslogic-api.md](../api/businesslogic-api.md) |
| **Verifier** | Entity that receives and validates presentations | [key-concepts.md](../overview/key-concepts.md) | [project-overview.md](../overview/project-overview.md), [businesslogic-api.md](../api/businesslogic-api.md) |
| **Verifiable Presentation (VP)** | Collection of one or more VCs packaged together and signed by the holder | [key-concepts.md](../overview/key-concepts.md) | [businesslogic-api.md](../api/businesslogic-api.md) |
| **W3C VC Data Model** | International standard for representing verifiable credentials | [0004-w3c-verifiable-credentials.md](../decisions/0004-w3c-verifiable-credentials.md) | [key-concepts.md](../overview/key-concepts.md), [compliance.md](../security/compliance.md) |
| **JSON-LD** | JSON-based format for linked data providing semantic interoperability | [0004-w3c-verifiable-credentials.md](../decisions/0004-w3c-verifiable-credentials.md) | [businesslogic-api.md](../api/businesslogic-api.md) |
| **Credential Request** | Application for a verifiable credential, submitted by holder or issuer | [key-concepts.md](../overview/key-concepts.md) | [businesslogic-api.md](../api/businesslogic-api.md) |
| **DIDLESS Credential** | Credential issued to subject without DID yet, claimed after DID creation | [glossary.md](../overview/glossary.md) | [businesslogic-api.md](../api/businesslogic-api.md) |

---

## Multi-Tenancy Concepts

| Concept | Definition | Primary Source | Related Docs |
|---------|-----------|----------------|--------------|
| **Tenant** | Isolated customer environment representing an organization using Sybol | [key-concepts.md](../overview/key-concepts.md) | [multi-tenancy.md](../architecture/multi-tenancy.md), [0003-multi-tenant-database-design.md](../decisions/0003-multi-tenant-database-design.md) |
| **Tenant ID** | Unique identifier for tenant (e.g., "repsol", "iberdrola") | [key-concepts.md](../overview/key-concepts.md) | [multi-tenancy.md](../architecture/multi-tenancy.md), [authentication.md](../api/authentication.md) |
| **Tenant Isolation** | Complete separation of tenant data, compute, and cryptography | [key-concepts.md](../overview/key-concepts.md) | [0003-multi-tenant-database-design.md](../decisions/0003-multi-tenant-database-design.md), [security-architecture.md](../architecture/security-architecture.md) |
| **Database-per-Tenant** | Multi-tenancy pattern with separate PostgreSQL database per tenant | [0003-multi-tenant-database-design.md](../decisions/0003-multi-tenant-database-design.md) | [data-architecture.md](../architecture/data-architecture.md), [multi-tenancy.md](../architecture/multi-tenancy.md) |
| **Tenant Role** | User role within tenant defining permissions (admin, reader) | [key-concepts.md](../overview/key-concepts.md) | [authorization.md](../security/authorization.md), [authentication.md](../api/authentication.md) |
| **Tenant Onboarding** | Process of provisioning new tenant infrastructure and configuration | [key-concepts.md](../overview/key-concepts.md) | [tenant-onboarding.md](../operations/tenant-onboarding.md), [backoffice-api.md](../api/backoffice-api.md) |
| **Custom Tenant Attributes** | Cognito custom attributes for tenant isolation (`custom:tenant_id`, `custom:role`) | [key-concepts.md](../overview/key-concepts.md) | [0001-aws-cognito-authentication.md](../decisions/0001-aws-cognito-authentication.md), [authentication.md](../security/authentication.md) |
| **Noisy Neighbor** | Performance degradation caused by one tenant affecting others | [0003-multi-tenant-database-design.md](../decisions/0003-multi-tenant-database-design.md) | [multi-tenancy.md](../architecture/multi-tenancy.md) |

---

## Authentication & Authorization Concepts

| Concept | Definition | Primary Source | Related Docs |
|---------|-----------|----------------|--------------|
| **AWS Cognito** | Managed authentication service with User Pools and Identity Pools | [0001-aws-cognito-authentication.md](../decisions/0001-aws-cognito-authentication.md) | [authentication.md](../security/authentication.md), [infrastructure-setup.md](../operations/infrastructure-setup.md) |
| **Cognito User Pool** | Centralized user directory managing all users across tenants | [key-concepts.md](../overview/key-concepts.md) | [0001-aws-cognito-authentication.md](../decisions/0001-aws-cognito-authentication.md), [authentication.md](../api/authentication.md) |
| **Cognito Identity Pool** | Service exchanging JWT tokens for temporary AWS credentials via STS | [key-concepts.md](../overview/key-concepts.md) | [0001-aws-cognito-authentication.md](../decisions/0001-aws-cognito-authentication.md), [authorization.md](../security/authorization.md) |
| **STS AssumeRole** | AWS Security Token Service operation providing temporary, scoped credentials | [key-concepts.md](../overview/key-concepts.md) | [authorization.md](../security/authorization.md), [multi-tenancy.md](../architecture/multi-tenancy.md) |
| **JWT (JSON Web Token)** | Compact, URL-safe token format for authentication and encoding credentials | [glossary.md](../overview/glossary.md) | [authentication.md](../api/authentication.md), [0001-aws-cognito-authentication.md](../decisions/0001-aws-cognito-authentication.md) |
| **Access Token** | Cognito token validated by API Gateway for authentication | [authentication.md](../api/authentication.md) | [api/README.md](../api/README.md) |
| **ID Token** | Cognito token containing custom claims (tenant_id, role) | [authentication.md](../api/authentication.md) | [api/README.md](../api/README.md) |
| **MFA (Multi-Factor Authentication)** | Authentication requiring multiple verification methods (TOTP, SMS) | [glossary.md](../overview/glossary.md) | [0001-aws-cognito-authentication.md](../decisions/0001-aws-cognito-authentication.md), [authentication.md](../security/authentication.md) |
| **IAM Role** | AWS identity with permissions policies for resource access | [glossary.md](../overview/glossary.md) | [authorization.md](../security/authorization.md), [security-architecture.md](../architecture/security-architecture.md) |
| **Tenant IAM Role** | Dedicated IAM role per tenant for resource isolation (`TenantRole-{tenantId}-{role}`) | [key-concepts.md](../overview/key-concepts.md) | [authorization.md](../security/authorization.md), [tenant-onboarding.md](../operations/tenant-onboarding.md) |
| **Trust Policy** | IAM policy defining which principals can assume a role | [key-concepts.md](../overview/key-concepts.md) | [authorization.md](../security/authorization.md) |
| **RBAC (Role-Based Access Control)** | Access control model based on user roles | [glossary.md](../overview/glossary.md) | [authorization.md](../security/authorization.md) |

---

## Data Model Concepts

| Concept | Definition | Primary Source | Related Docs |
|---------|-----------|----------------|--------------|
| **Document** | Conceptual container for credential type with versioning (formerly "Origin") | [key-concepts.md](../overview/key-concepts.md) | [catalog-api.md](../api/catalog-api.md), [data-architecture.md](../architecture/data-architecture.md) |
| **Claim** | Reusable data field definition with validation rules (formerly "Attribute") | [key-concepts.md](../overview/key-concepts.md) | [catalog-api.md](../api/catalog-api.md), [data-architecture.md](../architecture/data-architecture.md) |
| **Form** | Logical view over claims organizing them into sections for data entry | [key-concepts.md](../overview/key-concepts.md) | [catalog-api.md](../api/catalog-api.md) |
| **Compliance Region** | Jurisdiction or regulatory framework associated with documents | [glossary.md](../overview/glossary.md) | [catalog-api.md](../api/catalog-api.md) |
| **Credential Schema** | Structure defining credential data fields and validation | [data-architecture.md](../architecture/data-architecture.md) | [catalog-api.md](../api/catalog-api.md) |
| **Presentation Request** | Request from verifier specifying required credentials and claims | [businesslogic-api.md](../api/businesslogic-api.md) | [key-concepts.md](../overview/key-concepts.md) |

---

## AWS Serverless Concepts

| Concept | Definition | Primary Source | Related Docs |
|---------|-----------|----------------|--------------|
| **AWS Lambda** | Serverless compute service running code in response to events | [0002-serverless-architecture.md](../decisions/0002-serverless-architecture.md) | [deployment-architecture.md](../architecture/deployment-architecture.md), [component-architecture.md](../architecture/component-architecture.md) |
| **API Gateway** | AWS service providing RESTful HTTP APIs with Lambda integration | [glossary.md](../overview/glossary.md) | [0002-serverless-architecture.md](../decisions/0002-serverless-architecture.md), [system-overview.md](../architecture/system-overview.md) |
| **Lambda Container Image** | Containerized Lambda function using Docker images | [0002-serverless-architecture.md](../decisions/0002-serverless-architecture.md) | [deployment-architecture.md](../architecture/deployment-architecture.md) |
| **Cold Start** | Latency when Lambda function first invoked after period of inactivity | [0002-serverless-architecture.md](../decisions/0002-serverless-architecture.md) | [glossary.md](../overview/glossary.md) |
| **RDS (Relational Database Service)** | AWS managed PostgreSQL database service | [system-overview.md](../architecture/system-overview.md) | [data-architecture.md](../architecture/data-architecture.md), [infrastructure-setup.md](../operations/infrastructure-setup.md) |
| **RDS Proxy** | Connection pooling service for Lambda-to-RDS connections | [deployment-architecture.md](../architecture/deployment-architecture.md) | [data-architecture.md](../architecture/data-architecture.md) |
| **CloudFront** | AWS CDN service for distributing frontend applications globally | [glossary.md](../overview/glossary.md) | [deployment-architecture.md](../architecture/deployment-architecture.md), [tenant-onboarding.md](../operations/tenant-onboarding.md) |
| **S3 (Simple Storage Service)** | AWS object storage service for files and static assets | [system-overview.md](../architecture/system-overview.md) | [deployment-architecture.md](../architecture/deployment-architecture.md) |
| **EventBridge** | AWS event bus service for application integration | [glossary.md](../overview/glossary.md) | [integration-architecture.md](../architecture/integration-architecture.md), [propagate-api.md](../api/propagate-api.md) |
| **KMS (Key Management Service)** | AWS service for creating and managing cryptographic keys | [glossary.md](../overview/glossary.md) | [cryptography.md](../security/cryptography.md), [security-architecture.md](../architecture/security-architecture.md) |
| **Secrets Manager** | AWS service for storing and rotating secrets and credentials | [deployment-architecture.md](../architecture/deployment-architecture.md) | [security-architecture.md](../architecture/security-architecture.md) |
| **ECR (Elastic Container Registry)** | AWS Docker registry for Lambda container images | [glossary.md](../overview/glossary.md) | [deployment-procedures.md](../operations/deployment-procedures.md) |
| **Route 53** | AWS DNS service for domain management | [infrastructure-setup.md](../operations/infrastructure-setup.md) | [deployment-architecture.md](../architecture/deployment-architecture.md) |
| **ACM (AWS Certificate Manager)** | AWS service for SSL/TLS certificate provisioning | [glossary.md](../overview/glossary.md) | [tenant-onboarding.md](../operations/tenant-onboarding.md) |
| **CDK (Cloud Development Kit)** | Infrastructure as Code framework using TypeScript | [glossary.md](../overview/glossary.md) | [deployment-architecture.md](../architecture/deployment-architecture.md), [infrastructure-setup.md](../operations/infrastructure-setup.md) |

---

## Sybol Services & Components

| Concept | Definition | Primary Source | Related Docs |
|---------|-----------|----------------|--------------|
| **Backoffice Service** | Microservice handling platform administration, tenant onboarding, KYB verification | [component-architecture.md](../architecture/component-architecture.md) | [backoffice-api.md](../api/backoffice-api.md), [system-overview.md](../architecture/system-overview.md) |
| **BusinessLogic Service** | Microservice managing verifiable credentials lifecycle | [component-architecture.md](../architecture/component-architecture.md) | [businesslogic-api.md](../api/businesslogic-api.md), [system-overview.md](../architecture/system-overview.md) |
| **Catalog Service** | Microservice providing document templates, claims, and forms | [component-architecture.md](../architecture/component-architecture.md) | [catalog-api.md](../api/catalog-api.md), [system-overview.md](../architecture/system-overview.md) |
| **Propagate Service** | Microservice handling cross-tenant event propagation | [component-architecture.md](../architecture/component-architecture.md) | [propagate-api.md](../api/propagate-api.md), [integration-architecture.md](../architecture/integration-architecture.md) |
| **IOM (Identity & Organization Management)** | Service managing identities and organizational structures | [component-architecture.md](../architecture/component-architecture.md) | [system-overview.md](../architecture/system-overview.md) |
| **SVault (Secure Vault)** | Service for secure storage of sensitive credentials | [component-architecture.md](../architecture/component-architecture.md) | [system-overview.md](../architecture/system-overview.md) |
| **PAdES Lambda** | Lambda function for PDF document signing with qualified electronic signatures | [system-overview.md](../architecture/system-overview.md) | [component-architecture.md](../architecture/component-architecture.md) |
| **SignEth Lambda** | Lambda function for Ethereum blockchain signing using KMS | [system-overview.md](../architecture/system-overview.md) | [component-architecture.md](../architecture/component-architecture.md) |
| **WWC (Wallet Web Client)** | React-based end-user credential wallet application | [system-overview.md](../architecture/system-overview.md) | [component-architecture.md](../architecture/component-architecture.md) |
| **OnBoarding Web** | React-based tenant self-service portal | [system-overview.md](../architecture/system-overview.md) | [component-architecture.md](../architecture/component-architecture.md) |

---

## Cryptography & Security Concepts

| Concept | Definition | Primary Source | Related Docs |
|---------|-----------|----------------|--------------|
| **KMS Asymmetric Key** | Public-private key pair managed by AWS KMS for signing (ECC_NIST_P256) | [cryptography.md](../security/cryptography.md) | [security-architecture.md](../architecture/security-architecture.md) |
| **Digital Signature** | Cryptographic signature proving authenticity and integrity | [key-concepts.md](../overview/key-concepts.md) | [cryptography.md](../security/cryptography.md), [0004-w3c-verifiable-credentials.md](../decisions/0004-w3c-verifiable-credentials.md) |
| **Encryption at Rest** | Data encryption when stored on disk | [cryptography.md](../security/cryptography.md) | [security-architecture.md](../architecture/security-architecture.md) |
| **Encryption in Transit** | Data encryption during network transmission (TLS/SSL) | [cryptography.md](../security/cryptography.md) | [security-architecture.md](../architecture/security-architecture.md) |
| **Selective Disclosure** | Ability to share specific credential claims without revealing entire credential | [key-concepts.md](../overview/key-concepts.md) | [0004-w3c-verifiable-credentials.md](../decisions/0004-w3c-verifiable-credentials.md) |
| **BBS+ Signatures** | Cryptographic signature scheme enabling selective disclosure | [0004-w3c-verifiable-credentials.md](../decisions/0004-w3c-verifiable-credentials.md) | [cryptography.md](../security/cryptography.md) |
| **Qualified Electronic Signature** | Digital signature with legal equivalence to handwritten signature | [cryptography.md](../security/cryptography.md) | [compliance.md](../security/compliance.md) |
| **PAdES (PDF Advanced Electronic Signatures)** | Standard for advanced electronic signatures in PDF documents | [glossary.md](../overview/glossary.md) | [cryptography.md](../security/cryptography.md) |
| **PKI (Public Key Infrastructure)** | Framework for managing digital certificates and public keys | [cryptography.md](../security/cryptography.md) | [security-architecture.md](../architecture/security-architecture.md) |

---

## Compliance & Standards Concepts

| Concept | Definition | Primary Source | Related Docs |
|---------|-----------|----------------|--------------|
| **eIDAS 2.0** | EU regulation for electronic identification and trust services | [glossary.md](../overview/glossary.md) | [compliance.md](../security/compliance.md), [0004-w3c-verifiable-credentials.md](../decisions/0004-w3c-verifiable-credentials.md) |
| **GDPR (General Data Protection Regulation)** | EU regulation on data privacy and protection | [glossary.md](../overview/glossary.md) | [compliance.md](../security/compliance.md), [0003-multi-tenant-database-design.md](../decisions/0003-multi-tenant-database-design.md) |
| **Right to Erasure** | GDPR right allowing users to request data deletion | [0003-multi-tenant-database-design.md](../decisions/0003-multi-tenant-database-design.md) | [compliance.md](../security/compliance.md) |
| **KYB (Know Your Business)** | Business identity verification process | [glossary.md](../overview/glossary.md) | [backoffice-api.md](../api/backoffice-api.md) |
| **SOC 2** | Security compliance framework for service organizations | [compliance.md](../security/compliance.md) | [security-overview.md](../security/security-overview.md) |
| **Audit Logging** | Complete audit trail for compliance and security | [key-concepts.md](../overview/key-concepts.md) | [monitoring.md](../operations/monitoring.md), [security-overview.md](../security/security-overview.md) |

---

## Domain-Specific Concepts

| Concept | Definition | Primary Source | Related Docs |
|---------|-----------|----------------|--------------|
| **Guarantee of Origin (GO)** | Certificate proving energy was produced from renewable sources | [glossary.md](../overview/glossary.md) | [project-overview.md](../overview/project-overview.md) |
| **CUPS (Universal Supply Point Code)** | Identifier for energy supply points in Spain | [glossary.md](../overview/glossary.md) | [catalog-api.md](../api/catalog-api.md) |
| **Renewable Energy Certificate** | Credential verifying renewable energy production | [project-overview.md](../overview/project-overview.md) | [key-concepts.md](../overview/key-concepts.md) |

---

## Operational Concepts

| Concept | Definition | Primary Source | Related Docs |
|---------|-----------|----------------|--------------|
| **Infrastructure as Code (IaC)** | Managing infrastructure through code rather than manual processes | [deployment-architecture.md](../architecture/deployment-architecture.md) | [infrastructure-setup.md](../operations/infrastructure-setup.md) |
| **CoreInfra** | CDK stack for core shared infrastructure | [infrastructure-setup.md](../operations/infrastructure-setup.md) | [deployment-architecture.md](../architecture/deployment-architecture.md) |
| **ClientInfra** | CDK stack for tenant-specific infrastructure | [tenant-onboarding.md](../operations/tenant-onboarding.md) | [deployment-architecture.md](../architecture/deployment-architecture.md) |
| **Point-in-Time Recovery (PITR)** | RDS backup feature enabling restore to specific timestamp | [backup-recovery.md](../operations/backup-recovery.md) | [data-architecture.md](../architecture/data-architecture.md) |
| **CloudWatch** | AWS monitoring and observability service | [monitoring.md](../operations/monitoring.md) | [deployment-architecture.md](../architecture/deployment-architecture.md) |
| **CI/CD (Continuous Integration/Continuous Deployment)** | Automated software delivery pipeline | [deployment-procedures.md](../operations/deployment-procedures.md) | [contributing.md](../development/contributing.md) |

---

## Concept Relationships

### Primary Concept Dependencies

```
Verifiable Credential
├── Issuer (creates VC)
├── Holder (stores VC)
├── Verifier (validates VC)
├── DID (identifies issuer/holder)
├── Digital Signature (proves authenticity)
└── W3C VC Data Model (standard format)

Multi-Tenancy
├── Tenant (isolated environment)
├── Tenant ID (unique identifier)
├── Database-per-Tenant (isolation strategy)
├── Tenant IAM Role (access control)
└── STS AssumeRole (temporary credentials)

Authentication
├── AWS Cognito (identity provider)
├── User Pool (user directory)
├── Identity Pool (credential exchange)
├── JWT (token format)
└── MFA (additional security)
```

---

## Concept Cross-Reference Matrix

| From Concept | Relationship | To Concept |
|--------------|-------------|-----------|
| Verifiable Credential | implements | W3C VC Data Model |
| Verifiable Credential | signed by | Issuer |
| Verifiable Credential | held by | Holder |
| Verifiable Credential | verified by | Verifier |
| Verifiable Credential | identified by | DID |
| Tenant | isolated using | Database-per-Tenant |
| Tenant | authenticated via | AWS Cognito |
| Tenant | authorized using | STS AssumeRole |
| Tenant | encrypted with | KMS |
| BusinessLogic Service | issues | Verifiable Credential |
| Catalog Service | provides | Document |
| Catalog Service | provides | Claim |
| Backoffice Service | manages | Tenant |
| Lambda | invoked via | API Gateway |
| JWT | contains | Tenant ID |
| IAM Role | assumed via | STS AssumeRole |

---

## Index Metadata

- **Generated:** March 10, 2026
- **Total Concepts:** 87
- **Concept Categories:** 11
- **Related Indexes:** [document-index.md](document-index.md), [traceability.md](traceability.md), [knowledge-graph.md](knowledge-graph.md)
