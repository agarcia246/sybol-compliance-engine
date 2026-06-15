# Sybol Documentation Hub

Toda la documentación del proyecto Sybol se centraliza en este directorio. Aquí encontrarás arquitectura, decisiones técnicas (ADRs), especificaciones, guías de desarrollo, operaciones y seguridad — organizados por componente y globalmente.

## ¿Qué es Sybol?

Plataforma de **Verifiable Credentials** multi-tenant para organizaciones. Permite emitir, gestionar y verificar credenciales verificables (W3C VC + protocolo VEIA), con soporte para firma blockchain (Alastria RedT/RedB), KYB, y votación digital.

Componentes implementados:

- **Web Apps**: `wwc` (wallet del holder), `OnBoardingWeb` (alta de tenants), `SybolComponents` (librería UI)
- **Services**: `backoffice`, `bm`, `businessLogic`, `catalog`, `database`, `iom`, `propagate`, `svault`
- **Lambdas**: `PAdES`, `PAdES_2`, `setupAlastriaIdentity`, `signEth`
- **blockchainManager**: abstracción blockchain EVM

---

## Navegación por componente

| Componente | Documentación |
|---|---|
| 📦 **Services** | [docs/services/](services/README.md) |
| 🌐 **Web Applications** | [docs/webapps/](webapps/README.md) |
| ⚡ **Lambdas** | [docs/lambdas/](lambdas/README.md) |
| ⛓ **blockchainManager** | [docs/blockchainManager/](blockchainManager/README.md) |
| 🌍 **Global / Transversal** | [docs/global/](global/README.md) |

---

## Documentación global

### Overview del proyecto
- [Visión general del proyecto](global/overview/project-overview.md)
- [Conceptos clave](global/overview/key-concepts.md)
- [Glosario](global/overview/glossary.md)
- [Documento técnico funcional](global/overview/technical-functional-doc.md)

### Arquitectura del sistema
- [System Overview](global/architecture/system-overview.md)
- [Component Architecture](global/architecture/component-architecture.md)
- [Data Architecture](global/architecture/data-architecture.md)
- [Deployment Architecture](global/architecture/deployment-architecture.md)
- [Integration Architecture](global/architecture/integration-architecture.md)
- [Multi-Tenancy](global/architecture/multi-tenancy.md)
- [Security Architecture](global/architecture/security-architecture.md)

### ADRs globales (decisiones transversales)
- [ADR Index](global/decisions/README.md)
- [0001 — AWS Cognito Authentication](global/decisions/0001-aws-cognito-authentication.md)
- [0002 — Serverless Architecture](global/decisions/0002-serverless-architecture.md)
- [0003 — Multi-Tenant Database Design](global/decisions/0003-multi-tenant-database-design.md)
- [0004 — W3C Verifiable Credentials](global/decisions/0004-w3c-verifiable-credentials.md)
- [0005 — Lambda VPC Blockchain Connectivity](global/decisions/0005-lambda-vpc-blockchain-connectivity.md)
- [0006 — Catalog W3C Data Model Alignment](global/decisions/0006-catalog-w3c-data-model-alignment.md)

### API transversal
- [Authentication](global/api/authentication.md)
- [Error Handling](global/api/error-handling.md)

### Desarrollo
- [Getting Started](global/development/getting-started.md)
- [Local Development](global/development/local-development.md)
- [Coding Standards](global/development/coding-standards.md)
- [Testing Strategy](global/development/testing-strategy.md)
- [Contributing](global/development/contributing.md)
- [Repository Structure](global/development/repository-structure.md)
- [Definition of Ready](global/development/definition-of-ready.md)
- [Environment Config](global/development/environment-config.md)

### Operaciones
- [Deployment Procedures](global/operations/deployment-procedures.md)
- [Infrastructure Setup](global/operations/infrastructure-setup.md)
- [Core Setup](global/operations/core-setup.md)
- [Tenant Deployment](global/operations/tenant-deployment.md)
- [Multi-Tenant Operations](global/operations/multi-tenant-operations.md)
- [Monitoring](global/operations/monitoring.md)
- [Tenant Onboarding](global/operations/tenant-onboarding.md)
- [Backup & Recovery](global/operations/backup-recovery.md)
- [Troubleshooting](global/operations/troubleshooting.md)

### Seguridad
- [Security Overview](global/security/security-overview.md)
- [Authentication](global/security/authentication.md)
- [Authorization](global/security/authorization.md)
- [Cryptography](global/security/cryptography.md)
- [Compliance](global/security/compliance.md)

### Apéndices
- [AWS Resources](global/appendix/aws-resources.md)
- [Environment Variables](global/appendix/environment-variables.md)
- [FAQ](global/appendix/faq.md)
- [References](global/appendix/references.md)

---

## Índice de conocimiento

- [Document Index](index/document-index.md)
- [Concept Index](index/concept-index.md)
- [Knowledge Graph](index/knowledge-graph.md)
- [Traceability](index/traceability.md)
- [Compliance](security/compliance.md) - Compliance-oriented guidance

### Appendix

- [Environment Variables](appendix/environment-variables.md) - Configuration reference
- [AWS Resources](appendix/aws-resources.md) - Resource inventory
- [FAQ](appendix/faq.md) - Frequently asked questions
- [References](appendix/references.md) - External references

## Project Status

This documentation set is being normalized against the source repository. The pages updated in this review should be treated as the authoritative current-state summary. Other pages may still contain roadmap or production-posture statements that need follow-up verification.

For service changes since late 2025, see [CHANGELOG](../CHANGELOG.md).

---

Last updated: March 2026
