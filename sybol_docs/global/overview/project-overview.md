# Project Overview

## What is Sybol?

Sybol is a platform for sharing, issuing, and validating business information through verifiable credentials, identity documents, and tenant-specific workflows. The technical-functional product document describes Sybol as an enterprise-oriented Web3 and digital-trust platform. The repository confirms a substantial part of that vision through working web applications, backend services, and AWS provisioning code.

The current source tree shows a platform centered on:

- W3C-style credential and presentation flows
- DID document storage and lookup
- KYB onboarding through Sumsub
- Multi-tenant database and IAM isolation
- Catalog-driven documents, claims, and forms
- Cross-tenant propagation via JWT exchange and EventBridge

## Product Objectives

The following goals are supported by the technical-functional document and are consistent with the codebase direction:

- Reduce friction in structured information exchange between organizations
- Reuse previously validated information instead of repeating collection work
- Provide auditable, cryptographically signed business credentials
- Support enterprise onboarding and compliance-heavy workflows
- Keep tenant data and permissions isolated while reusing shared platform infrastructure

## Verified Product Surface

### Web Applications

- `webApps/wwc`: the main wallet-style React application for managing credentials, presentations, contacts, catalog assets, and delegation flows
- `webApps/OnBoardingWeb`: a React onboarding portal focused on registration, MFA step orchestration, KYB progression, and legal onboarding content

### Backend Services

- `services/backoffice`: KYB, DID document, and email support APIs
- `services/businessLogic`: credentials, credential requests, presentations, presentation requests, contacts, activity, and delegation tree APIs
- `services/catalog`: documents, claims, forms, fields, and compliance region APIs
- `services/propagate`: cross-tenant JWT delivery and EventBridge publishing

### Supporting Services and Infrastructure

- `lambdas/PAdES`: PDF signing workflows
- `lambdas/signEth`: Ethereum signing helpers backed by AWS KMS
- `services/svault`: KMS-backed cryptographic service used for JWT and blockchain operations
- `infraestructure/CoreInfra`: base AWS resources including VPC, RDS, Cognito, Identity Pool, Lambda wiring, and HTTP API
- `infraestructure/ClientInfra`: tenant onboarding stack for IAM roles, tenant database creation, and KMS-related tenant setup

## Current Use Cases Reflected in Documentation

The technical-functional document describes several business use cases. In the repository, they should be read as product scenarios rather than separate hard-coded modules unless a corresponding implementation is present.

- Supplier and contractor verification for CAE-style workflows
- Renewable-origin or energy-related credential scenarios such as DOR
- Employee identity and qualification credentials

These use cases are consistent with the credential, catalog, onboarding, and propagation primitives implemented in the codebase.

## Technology Stack

### Verified in Source

- Frontend: React 18, Material UI, React Router, i18next
- Backend: Node.js, Express, Joi, jose, pg
- Identity: AWS Cognito User Pool and Identity Pool
- Data: PostgreSQL on Amazon RDS
- Cryptography: AWS KMS, JWT signing, blockchain signing helpers
- Events: Amazon EventBridge in the propagate service
- Infrastructure as code: AWS CDK with TypeScript

### Referenced as Product Direction or Partial Implementation

- Broader eIDAS 2.0 positioning
- Mobile wallet application
- More open or decentralized wallet interoperability
- Stronger MFA posture across all user journeys
- Expanded blockchain and DID method interoperability

## Current-State Caveats

- The CoreInfra stack provisions RDS PostgreSQL 15.8 with `multiAz: false`; documentation should not describe Multi-AZ or read replicas as current behavior.
- The CoreInfra stack does not provision CloudFront or S3 frontend hosting; those deployment patterns may still exist operationally, but they are not represented in the current CDK stack.
- The onboarding application includes MFA-related steps and state, but the current Cognito stack does not enforce MFA.
- The changelog notes that some newer `businessLogic` and `propagate` API routes still require API Gateway wiring updates in `CoreInfra`.

## Roadmap Signals from the Technical-Functional Document

The technical-functional document is still useful as a roadmap source. The following items should be treated as planned or evolving unless separately verified in code or infrastructure:

- Mobile wallet support
- Expanded interoperability with external identity standards and wallets
- More open decentralized architecture across tenant nodes
- Broader security hardening, including MFA maturity and stronger lifecycle controls
- Wider use of blockchain anchoring and Alastria-related identity capabilities

## Repository Shape

```text
sybolRelases/
├── services/
│   ├── backoffice/
│   ├── bm/
│   ├── businessLogic/
│   ├── catalog/
│   ├── iom/
│   ├── propagate/
│   ├── svault/
│   └── database/
├── lambdas/
│   ├── PAdES/
│   ├── PAdES_2/
│   └── signEth/
├── infraestructure/
│   ├── CoreInfra/
│   └── ClientInfra/
├── webApps/
│   ├── OnBoardingWeb/
│   ├── SybolComponents/
│   └── wwc/
└── docs/
```

For a code-oriented view, see [Repository Structure](../development/repository-structure.md).

## Related Documentation

- [System Overview](../architecture/system-overview.md)
- [Component Architecture](../architecture/component-architecture.md)
- [Repository Structure](../development/repository-structure.md)
- [Current State Audit](../current-state-audit.md)

---

Last updated: March 2026
