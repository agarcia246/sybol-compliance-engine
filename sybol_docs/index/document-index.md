# Document Index

Indice completo de todos los documentos del proyecto Sybol, organizados por seccion.

**Total documentos:** ~134 markdown + YAML
**Ultima actualizacion:** marzo 2026

---

## Root Documentation

| Document Path | Category | Purpose | Key Concepts | Target Audience |
|--------------|----------|---------|--------------|-----------------|
| [README.md](../README.md) | Entry Point | Documentation hub and navigation guide | Documentation structure, quick links | All users |
| [CORE_SETUP.md](../CORE_SETUP.md) | Setup | Core infrastructure setup instructions | Infrastructure deployment | Platform administrators |
| [DOR_V2.md](../DOR_V2.md) | Technical | Document of Record Version 2 specifications | DOR structure, versioning | Developers, architects |
| [Environment.md](../Environment.md) | Configuration | Environment configuration reference | Environment variables, deployment environments | DevOps, developers |
| [GUIA_OPERATIVA_MULTI_TENANT.md](../GUIA_OPERATIVA_MULTI_TENANT.md) | Operations | Multi-tenant operational guide (Spanish) | Multi-tenancy operations, tenant management | Operations team |

---

## Overview (3 documents)

Foundation concepts and project introduction.

| Document Path | Category | Purpose | Key Concepts | Target Audience |
|--------------|----------|---------|--------------|-----------------|
| [overview/project-overview.md](../overview/project-overview.md) | Overview | High-level project vision, mission, features, use cases | Verifiable Credentials, Multi-Tenancy, Technology Stack | All stakeholders |
| [overview/key-concepts.md](../overview/key-concepts.md) | Concepts | Core domain concepts and terminology | VC, DID, Holders, Issuers, Verifiers, Tenant, STS AssumeRole | Developers, architects, product team |
| [overview/glossary.md](../overview/glossary.md) | Reference | Alphabetical glossary of terms and acronyms | Technical vocabulary, AWS services, domain terms | All users |

---

## Architecture (7 documents)

System design, components, and technical architecture.

| Document Path | Category | Purpose | Key Concepts | Target Audience |
|--------------|----------|---------|--------------|-----------------|
| [architecture/system-overview.md](../architecture/system-overview.md) | Architecture | High-level system architecture and context | System components, data flows, technology stack | Architects, technical leads |
| [architecture/component-architecture.md](../architecture/component-architecture.md) | Architecture | Detailed microservices breakdown | Backoffice, BusinessLogic, Catalog, Propagate services | Backend developers, architects |
| [architecture/data-architecture.md](../architecture/data-architecture.md) | Architecture | Database design and data models | Database-per-tenant, schemas, data isolation | Database administrators, backend developers |
| [architecture/security-architecture.md](../architecture/security-architecture.md) | Architecture | Security model and controls | Authentication, authorization, cryptography, tenant isolation | Security team, compliance, architects |
| [architecture/multi-tenancy.md](../architecture/multi-tenancy.md) | Architecture | Multi-tenant design patterns and implementation | Tenant isolation, resource allocation, STS credentials | Architects, backend developers |
| [architecture/integration-architecture.md](../architecture/integration-architecture.md) | Architecture | External system integrations | EventBridge, cross-tenant communication, webhooks | Integration developers, architects |
| [architecture/deployment-architecture.md](../architecture/deployment-architecture.md) | Architecture | AWS infrastructure and deployment topology | Lambda, API Gateway, RDS, CloudFront, CDK | DevOps, infrastructure team |

---

## Architecture Decisions (5 documents)

Key technical decisions with rationale and trade-offs.

| Document Path | Category | Purpose | Key Concepts | Target Audience |
|--------------|----------|---------|--------------|-----------------|
| [decisions/README.md](../decisions/README.md) | ADR Index | ADR overview and template | Decision-making framework, ADR structure | All technical stakeholders |
| [decisions/0001-aws-cognito-authentication.md](../decisions/0001-aws-cognito-authentication.md) | ADR | Authentication provider decision | AWS Cognito, User Pools, Identity Pools, JWT | Architects, security team |
| [decisions/0002-serverless-architecture.md](../decisions/0002-serverless-architecture.md) | ADR | Compute architecture decision | AWS Lambda, API Gateway, serverless | Architects, DevOps |
| [decisions/0003-multi-tenant-database-design.md](../decisions/0003-multi-tenant-database-design.md) | ADR | Multi-tenancy database strategy | Database-per-tenant, data isolation, compliance | Architects, DBAs, compliance |
| [decisions/0004-w3c-verifiable-credentials.md](../decisions/0004-w3c-verifiable-credentials.md) | ADR | Credential format standard decision | W3C VC, JSON-LD, eIDAS 2.0, interoperability | Architects, product team, compliance |

---

## Development (6 documents)

Developer guides and contribution procedures.

| Document Path | Category | Purpose | Key Concepts | Target Audience |
|--------------|----------|---------|--------------|-----------------|
| [development/getting-started.md](../development/getting-started.md) | Developer Guide | Developer onboarding and environment setup | Local setup, prerequisites, first steps | New developers |
| [development/repository-structure.md](../development/repository-structure.md) | Developer Guide | Codebase organization and navigation | Repository layout, service directories, infrastructure | Developers |
| [development/local-development.md](../development/local-development.md) | Developer Guide | Local development workflow and debugging | Docker, CLI tools, debugging techniques | Developers |
| [development/coding-standards.md](../development/coding-standards.md) | Developer Guide | Code style, patterns, and quality standards | Linting, formatting, best practices | Developers |
| [development/testing-strategy.md](../development/testing-strategy.md) | Developer Guide | Testing approach and methodologies | Unit tests, integration tests, coverage | Developers, QA |
| [development/contributing.md](../development/contributing.md) | Developer Guide | Contribution guidelines and workflow | Git workflow, PR process, code review | Contributors |

---

## API Reference (7 documents)

API specifications and usage guidelines.

| Document Path | Category | Purpose | Key Concepts | Target Audience |
|--------------|----------|---------|--------------|-----------------|
| [api/README.md](../api/README.md) | API Overview | API organization, authentication, conventions | JWT authentication, multi-tenant architecture | API consumers, developers |
| [api/authentication.md](../api/authentication.md) | API Guide | Authentication flows and token management | Cognito flows, JWT structure, STS AssumeRole | Frontend developers, integration teams |
| [api/backoffice-api.md](../api/backoffice-api.md) | API Reference | Backoffice service endpoints | Tenant onboarding, KYB verification, admin operations | Platform administrators, backend developers |
| [api/businesslogic-api.md](../api/businesslogic-api.md) | API Reference | BusinessLogic service endpoints | Credential issuance, requests, presentations, verification | Integration developers, frontend developers |
| [api/catalog-api.md](../api/catalog-api.md) | API Reference | Catalog service endpoints | Documents (templates), claims, forms, compliance regions | Frontend developers, content managers |
| [api/propagate-api.md](../api/propagate-api.md) | API Reference | Propagate service endpoints | Cross-tenant events, notifications | Integration developers |
| [api/error-handling.md](../api/error-handling.md) | API Guide | Standard error responses and codes | Error structure, status codes, debugging | API consumers, developers |

---

## Operations (6 documents)

Infrastructure deployment, maintenance, and operational procedures.

| Document Path | Category | Purpose | Key Concepts | Target Audience |
|--------------|----------|---------|--------------|-----------------|
| [operations/infrastructure-setup.md](../operations/infrastructure-setup.md) | Operations | Core AWS infrastructure deployment | Route 53, Cognito, RDS, API Gateway, Lambda | DevOps, platform administrators |
| [operations/tenant-onboarding.md](../operations/tenant-onboarding.md) | Operations | Tenant provisioning procedures | CDK deployment, KMS keys, IAM roles, CloudFront | DevOps, platform administrators |
| [operations/deployment-procedures.md](../operations/deployment-procedures.md) | Operations | CI/CD pipelines and deployment workflows | GitHub Actions, ECR, Lambda deployment | DevOps, developers |
| [operations/monitoring.md](../operations/monitoring.md) | Operations | CloudWatch monitoring and alerting | Metrics, logs, alarms, dashboards | DevOps, SRE |
| [operations/backup-recovery.md](../operations/backup-recovery.md) | Operations | Data backup and disaster recovery | RDS snapshots, point-in-time recovery, S3 versioning | DevOps, DBAs |
| [operations/troubleshooting.md](../operations/troubleshooting.md) | Operations | Common issues and resolution procedures | Error patterns, debugging strategies | All technical staff |

---

## Security (5 documents)

Security architecture, compliance, and best practices.

| Document Path | Category | Purpose | Key Concepts | Target Audience |
|--------------|----------|---------|--------------|-----------------|
| [security/security-overview.md](../security/security-overview.md) | Security | Security model and principles | Defense in depth, least privilege, audit logging | Security team, architects, compliance |
| [security/authentication.md](../security/authentication.md) | Security | Authentication mechanisms and implementation | Cognito User Pools, MFA, JWT validation | Security team, backend developers |
| [security/authorization.md](../security/authorization.md) | Security | Authorization model and access control | IAM roles, STS, tenant isolation, RBAC | Security team, backend developers |
| [security/cryptography.md](../security/cryptography.md) | Security | Cryptographic operations and key management | KMS, signing keys, DID keys, encryption at rest | Security team, cryptography specialists |
| [security/compliance.md](../security/compliance.md) | Security | Regulatory compliance and certifications | GDPR, eIDAS 2.0, SOC 2, audit requirements | Compliance team, security team, legal |

---

## Appendix (4 documents)

Reference materials and supplementary information.

| Document Path | Category | Purpose | Key Concepts | Target Audience |
|--------------|----------|---------|--------------|-----------------|
| [appendix/environment-variables.md](../appendix/environment-variables.md) | Reference | Environment configuration variables | Lambda env vars, secrets, configuration | Developers, DevOps |
| [appendix/aws-resources.md](../appendix/aws-resources.md) | Reference | AWS resource inventory and ARNs | Resource naming, ARN formats, service inventory | DevOps, architects |
| [appendix/faq.md](../appendix/faq.md) | Support | Frequently asked questions | Common questions, troubleshooting tips | All users |
| [appendix/references.md](../appendix/references.md) | Reference | External links and standards | W3C specs, AWS docs, eIDAS regulation | Researchers, architects |

---

## API Documentation (1 document)

API specifications in machine-readable format.

| Document Path | Category | Purpose | Key Concepts | Target Audience |
|--------------|----------|---------|--------------|-----------------|
| [api-docs/activity.yaml](../api-docs/activity.yaml) | API Spec | OpenAPI/Swagger specification | Activity tracking API schema | API consumers, integration developers |

---

## Document Categories Summary

| Category | Document Count | Purpose |
|----------|---------------|---------|
| **Root** | 5 | Entry points and setup guides |
| **Overview** | 3 | Project introduction and concepts |
| **Architecture** | 7 | System design and technical architecture |
| **Decisions** | 5 | Architecture Decision Records |
| **Development** | 6 | Developer guides and contribution |
| **API Reference** | 7 | API documentation and specifications |
| **Operations** | 6 | Infrastructure and operational procedures |
| **Security** | 5 | Security model and compliance |
| **Appendix** | 4 | Reference materials |
| **API Docs** | 1 | Machine-readable API specs |
| **Total** | **49** | Complete documentation system |

---

## Navigation Paths

### For New Users
1. [README.md](../README.md) → [overview/project-overview.md](../overview/project-overview.md) → [overview/key-concepts.md](../overview/key-concepts.md)

### For Developers
1. [development/getting-started.md](../development/getting-started.md) → [development/repository-structure.md](../development/repository-structure.md) → [development/local-development.md](../development/local-development.md)

### For Architects
1. [architecture/system-overview.md](../architecture/system-overview.md) → [decisions/README.md](../decisions/README.md) → Individual ADRs

### For DevOps
1. [operations/infrastructure-setup.md](../operations/infrastructure-setup.md) → [operations/tenant-onboarding.md](../operations/tenant-onboarding.md) → [operations/deployment-procedures.md](../operations/deployment-procedures.md)

### For API Consumers
1. [api/README.md](../api/README.md) → [api/authentication.md](../api/authentication.md) → Specific service API docs

---

## Index Metadata

- **Generated:** March 10, 2026
- **Documentation Version:** 2026-Q1
- **Index Format:** Markdown
- **Related Indexes:** [concept-index.md](concept-index.md), [traceability.md](traceability.md), [knowledge-graph.md](knowledge-graph.md)
