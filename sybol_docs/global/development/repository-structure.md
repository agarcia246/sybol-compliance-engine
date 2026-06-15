# Repository Structure

## Purpose

This page describes the repository layout that is actually present in the workspace. It is intentionally narrower than earlier generated versions and focuses on checked-in directories rather than inferred architecture.

## Root Layout

```text
sybolRelases/
├── services/
├── infraestructure/
├── lambdas/
├── webApps/
├── docs/
├── deploy/
├── CHANGELOG.md
└── README.md
```

## services

```text
services/
├── backoffice/
├── bm/
├── businessLogic/
├── catalog/
├── database/
├── iom/
├── propagate/
└── svault/
```

The main backend projects are Node.js and Express services that typically include `src/`, a Lambda entrypoint, route definitions, service or repository layers, a `package.json`, and a README.

### Verified service roles

- `backoffice`: KYB, DID document management, and email helper endpoints under `/api/bo`
- `businessLogic`: credentials, requests, presentations, contacts, activity, and delegation flows under `/api/bl`
- `catalog`: documents, claims, forms, fields, and compliance region APIs under `/api/catalog`
- `propagate`: send, receive, and EventBridge publication flows under `/api/ps`
- `svault`: KMS-backed cryptographic operations referenced by service documentation

The `bm`, `iom`, and `database` directories also exist in the repository. They were not the primary focus of this documentation correction pass, but some are referenced by infrastructure routing.

## infraestructure

```text
infraestructure/
├── ClientInfra/
├── CoreInfra/
└── Despliegue/
```

### CoreInfra

`infraestructure/CoreInfra` contains the base CDK application. The main stack file is `lib/sybol-core-stack.ts`, which provisions shared AWS resources such as VPC networking, RDS, Cognito, the Identity Pool, Lambda integrations, and the HTTP API.

### ClientInfra

`infraestructure/ClientInfra` contains the tenant onboarding CDK application. Its main stack file is `lib/client_infra-stack.ts`, and it supports tenant IAM role creation, tenant database setup inside the shared RDS instance, and tenant onboarding scripts.

## lambdas

```text
lambdas/
├── PAdES/
├── PAdES_2/
└── signEth/
```

- `PAdES` and `PAdES_2` contain PDF-signing related projects
- `signEth` contains Ethereum signing helpers

## webApps

```text
webApps/
├── OnBoardingWeb/
├── SybolComponents/
└── wwc/
```

- `wwc`: main wallet-style React application for credential, catalog, and contact flows
- `OnBoardingWeb`: onboarding and KYB React application with MFA-step UI state
- `SybolComponents`: shared frontend component workspace

## docs and deploy

- `docs`: architecture, API, security, and operations documentation
- `deploy`: shell scripts for infrastructure and service deployment

```text
deploy/
├── deploy.sh
└── deployServices.sh
```

## Related Documentation

- [Project Overview](../overview/project-overview.md)
- [System Overview](../architecture/system-overview.md)
- [Current State Audit](../current-state-audit.md)
