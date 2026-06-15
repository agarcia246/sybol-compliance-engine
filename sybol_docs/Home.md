# Sybol Wiki

Plataforma de **Verifiable Credentials** multi-tenant para organizaciones. Permite emitir, gestionar y verificar credenciales verificables (W3C VC + protocolo VEIA), con soporte para firma blockchain (Alastria RedT/RedB), KYB, y votación digital.

**Componentes:**
- **Web Apps** — `wwc` (wallet del holder) · `OnBoardingWeb` (alta de tenants) · `SybolComponents` (librería UI)
- **Services** — `backoffice` · `bm` · `businessLogic` · `catalog` · `database` · `iom` · `propagate` · `svault`
- **Lambdas** — `PAdES` · `PAdES_2` · `setupAlastriaIdentity` · `signEth`
- **blockchainManager** — abstracción blockchain EVM

---

## Navegación por componente

| Componente | Documentación |
|---|---|
| 📦 **Services** | [services](services) |
| 🌐 **Web Applications** | [webapps](webapps) |
| ⚡ **Lambdas** | [lambdas](lambdas) |
| ⛓ **blockchainManager** | [blockchainManager](blockchainManager) |
| 🌍 **Global / Transversal** | [global](global) |

---

## Documentación global

### Overview del proyecto
- [Visión general del proyecto](global/overview/project-overview)
- [Conceptos clave](global/overview/key-concepts)
- [Glosario](global/overview/glossary)
- [Documento técnico funcional](global/overview/technical-functional-doc)

### Arquitectura del sistema
- [System Overview](global/architecture/system-overview)
- [Component Architecture](global/architecture/component-architecture)
- [Data Architecture](global/architecture/data-architecture)
- [Deployment Architecture](global/architecture/deployment-architecture)
- [Integration Architecture](global/architecture/integration-architecture)
- [Multi-Tenancy](global/architecture/multi-tenancy)
- [Security Architecture](global/architecture/security-architecture)

### ADRs globales
- [ADR Index](global/decisions)
- [0001 — AWS Cognito Authentication](global/decisions/0001-aws-cognito-authentication)
- [0002 — Serverless Architecture](global/decisions/0002-serverless-architecture)
- [0003 — Multi-Tenant Database Design](global/decisions/0003-multi-tenant-database-design)
- [0004 — W3C Verifiable Credentials](global/decisions/0004-w3c-verifiable-credentials)
- [0005 — Lambda VPC Blockchain Connectivity](global/decisions/0005-lambda-vpc-blockchain-connectivity)
- [0006 — Catalog W3C Data Model Alignment](global/decisions/0006-catalog-w3c-data-model-alignment)

### API transversal
- [Authentication](global/api/authentication)
- [Error Handling](global/api/error-handling)

### Desarrollo
- [Getting Started](global/development/getting-started)
- [Local Development](global/development/local-development)
- [Coding Standards](global/development/coding-standards)
- [Testing Strategy](global/development/testing-strategy)
- [Contributing](global/development/contributing)
- [Repository Structure](global/development/repository-structure)
- [Definition of Ready](global/development/definition-of-ready)
- [Environment Config](global/development/environment-config)

### Operaciones
- [Deployment Procedures](global/operations/deployment-procedures)
- [Infrastructure Setup](global/operations/infrastructure-setup)
- [Core Setup](global/operations/core-setup)
- [Tenant Deployment](global/operations/tenant-deployment)
- [Multi-Tenant Operations](global/operations/multi-tenant-operations)
- [Monitoring](global/operations/monitoring)
- [Tenant Onboarding](global/operations/tenant-onboarding)
- [Backup & Recovery](global/operations/backup-recovery)
- [Troubleshooting](global/operations/troubleshooting)
- [KMS Management](global/operations/infrastructure/kms-management)
- [ECR Lambda Management](global/operations/infrastructure/ecr-lambda-management)

### Seguridad
- [Security Overview](global/security/security-overview)
- [Authentication](global/security/authentication)
- [Authorization](global/security/authorization)
- [Cryptography](global/security/cryptography)
- [Compliance](global/security/compliance)

### Apéndices
- [AWS Resources](global/appendix/aws-resources)
- [Environment Variables](global/appendix/environment-variables)
- [FAQ](global/appendix/faq)
- [References](global/appendix/references)

---

## Índice de conocimiento
- [Document Index](index/document-index)
- [Concept Index](index/concept-index)
- [Knowledge Graph](index/knowledge-graph)
- [Traceability](index/traceability)
