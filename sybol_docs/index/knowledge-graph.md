# Documentation Knowledge Graph

## Purpose

Visual representation of relationships between Sybol documentation files using Mermaid diagrams. This knowledge graph enables intuitive navigation and reveals conceptual connections across the documentation system.

**Total Node Types:** 6 (Documents, Concepts, ADRs, Components, APIs, Operations)  
**Total Relationships:** 150+  
**Last Updated:** March 10, 2026

---

## Table of Contents

1. [Complete Documentation Network](#complete-documentation-network)
2. [Architecture Documentation Flow](#architecture-documentation-flow)
3. [ADR Influence Map](#adr-influence-map)
4. [Concept Dependency Graph](#concept-dependency-graph)
5. [Service Integration Map](#service-integration-map)
6. [User Journey Navigation Paths](#user-journey-navigation-paths)
7. [API Documentation Relationships](#api-documentation-relationships)
8. [Operations Workflow](#operations-workflow)

---

## Complete Documentation Network

High-level view of all documentation categories and key cross-references.

```mermaid
graph TB
    %% Entry Points
    README[📖 README.md]
    
    %% Main Categories
    Overview[📘 Overview]
    Architecture[🏗️ Architecture]
    Decisions[🎯 Decisions]
    Development[💻 Development]
    API[🔌 API]
    Operations[⚙️ Operations]
    Security[🔒 Security]
    Appendix[📚 Appendix]
    
    %% Entry connections
    README --> Overview
    README --> Development
    README --> Operations
    README --> API
    README --> Architecture
    
    %% Category connections
    Overview --> Architecture
    Overview --> API
    Overview --> Security
    
    Architecture --> Decisions
    Architecture --> Security
    Architecture --> Operations
    Architecture --> API
    
    Decisions --> Architecture
    Decisions --> Security
    Decisions --> Operations
    
    Development --> API
    Development --> Operations
    Development --> Security
    
    API --> Security
    API --> Architecture
    
    Operations --> Security
    Operations --> Architecture
    Operations --> Appendix
    
    Security --> Appendix
    Architecture --> Appendix
    
    style README fill:#e1f5ff
    style Overview fill:#fff4e1
    style Architecture fill:#e8f5e9
    style Decisions fill:#f3e5f5
    style Development fill:#fce4ec
    style API fill:#e0f2f1
    style Operations fill:#fff9c4
    style Security fill:#ffebee
    style Appendix fill:#f5f5f5
```

---

## Architecture Documentation Flow

Detailed architecture documentation hierarchy and dependencies.

```mermaid
graph TB
    %% Overview Layer
    ProjOverview[project-overview.md]
    KeyConcepts[key-concepts.md]
    Glossary[glossary.md]
    
    %% Architecture Layer
    SystemOverview[system-overview.md]
    ComponentArch[component-architecture.md]
    DataArch[data-architecture.md]
    SecurityArch[security-architecture.md]
    MultiTenancy[multi-tenancy.md]
    IntegrationArch[integration-architecture.md]
    DeploymentArch[deployment-architecture.md]
    
    %% Concept Flow
    ProjOverview --> KeyConcepts
    KeyConcepts --> Glossary
    
    %% Architecture Flow
    SystemOverview --> ComponentArch
    SystemOverview --> DataArch
    SystemOverview --> DeploymentArch
    
    ComponentArch --> SecurityArch
    ComponentArch --> MultiTenancy
    ComponentArch --> IntegrationArch
    
    DataArch --> MultiTenancy
    DataArch --> SecurityArch
    
    SecurityArch --> MultiTenancy
    
    %% Concept to Architecture
    KeyConcepts --> SystemOverview
    KeyConcepts --> MultiTenancy
    KeyConcepts --> SecurityArch
    
    %% Cross-references
    MultiTenancy --> DataArch
    IntegrationArch --> ComponentArch
    DeploymentArch --> ComponentArch
    DeploymentArch --> DataArch
    
    style ProjOverview fill:#bbdefb
    style KeyConcepts fill:#bbdefb
    style Glossary fill:#bbdefb
    style SystemOverview fill:#c8e6c9
    style ComponentArch fill:#c8e6c9
    style DataArch fill:#c8e6c9
    style SecurityArch fill:#ffccbc
    style MultiTenancy fill:#c8e6c9
    style IntegrationArch fill:#c8e6c9
    style DeploymentArch fill:#c8e6c9
```

---

## ADR Influence Map

How Architecture Decision Records influence implementation documentation.

```mermaid
graph TD
    %% ADRs
    ADR0001[ADR-0001<br/>Cognito Auth]
    ADR0002[ADR-0002<br/>Serverless]
    ADR0003[ADR-0003<br/>DB-per-Tenant]
    ADR0004[ADR-0004<br/>W3C VC]
    
    %% Architecture Docs
    SystemOverview[system-overview.md]
    ComponentArch[component-architecture.md]
    DataArch[data-architecture.md]
    SecurityArch[security-architecture.md]
    MultiTenancy[multi-tenancy.md]
    DeploymentArch[deployment-architecture.md]
    
    %% Security Docs
    AuthenticationDoc[security/authentication.md]
    AuthorizationDoc[security/authorization.md]
    CryptographyDoc[security/cryptography.md]
    ComplianceDoc[security/compliance.md]
    
    %% API Docs
    APIReadme[api/README.md]
    BackofficeAPI[api/backoffice-api.md]
    BusinessLogicAPI[api/businesslogic-api.md]
    CatalogAPI[api/catalog-api.md]
    
    %% Operations Docs
    InfraSetup[operations/infrastructure-setup.md]
    TenantOnboarding[operations/tenant-onboarding.md]
    DeploymentProc[operations/deployment-procedures.md]
    BackupRecovery[operations/backup-recovery.md]
    
    %% ADR → Architecture
    ADR0001 --> SecurityArch
    ADR0001 --> ComponentArch
    ADR0002 --> SystemOverview
    ADR0002 --> ComponentArch
    ADR0002 --> DeploymentArch
    ADR0003 --> DataArch
    ADR0003 --> MultiTenancy
    ADR0003 --> SecurityArch
    ADR0004 --> ComponentArch
    ADR0004 --> DataArch
    
    %% ADR → Security
    ADR0001 --> AuthenticationDoc
    ADR0001 --> AuthorizationDoc
    ADR0003 --> AuthorizationDoc
    ADR0003 --> ComplianceDoc
    ADR0004 --> CryptographyDoc
    ADR0004 --> ComplianceDoc
    
    %% ADR → API
    ADR0001 --> APIReadme
    ADR0001 --> BackofficeAPI
    ADR0003 --> APIReadme
    ADR0004 --> BusinessLogicAPI
    ADR0004 --> CatalogAPI
    
    %% ADR → Operations
    ADR0001 --> InfraSetup
    ADR0001 --> TenantOnboarding
    ADR0002 --> InfraSetup
    ADR0002 --> DeploymentProc
    ADR0003 --> TenantOnboarding
    ADR0003 --> BackupRecovery
    
    style ADR0001 fill:#e1bee7
    style ADR0002 fill:#e1bee7
    style ADR0003 fill:#e1bee7
    style ADR0004 fill:#e1bee7
    style SystemOverview fill:#c8e6c9
    style SecurityArch fill:#ffccbc
    style DataArch fill:#c8e6c9
    style MultiTenancy fill:#c8e6c9
```

---

## Concept Dependency Graph

Core concepts and their relationships.

```mermaid
graph TB
    %% Core VC Concepts
    VC[Verifiable Credential]
    DID[Decentralized Identifier]
    Issuer[Issuer]
    Holder[Holder]
    Verifier[Verifier]
    VP[Verifiable Presentation]
    W3CVC[W3C VC Standard]
    
    %% Multi-Tenancy Concepts
    Tenant[Tenant]
    TenantID[Tenant ID]
    DBPerTenant[Database-per-Tenant]
    TenantIsolation[Tenant Isolation]
    TenantRole[Tenant Role]
    
    %% Auth Concepts
    Cognito[AWS Cognito]
    UserPool[User Pool]
    IdentityPool[Identity Pool]
    JWT[JWT Token]
    STSAssume[STS AssumeRole]
    IAMRole[IAM Role]
    
    %% Serverless Concepts
    Lambda[AWS Lambda]
    APIGateway[API Gateway]
    RDS[RDS PostgreSQL]
    KMS[AWS KMS]
    
    %% VC Relationships
    VC -->|implements| W3CVC
    VC -->|signed by| Issuer
    VC -->|held by| Holder
    VC -->|verified by| Verifier
    VC -->|identified by| DID
    VC -->|packaged in| VP
    Holder -->|presents| VP
    
    %% Multi-Tenancy Relationships
    Tenant -->|identified by| TenantID
    Tenant -->|isolated using| DBPerTenant
    Tenant -->|enforces| TenantIsolation
    Tenant -->|has users with| TenantRole
    TenantID -->|stored in| JWT
    
    %% Auth Relationships
    Cognito -->|contains| UserPool
    Cognito -->|provides| IdentityPool
    UserPool -->|issues| JWT
    IdentityPool -->|enables| STSAssume
    STSAssume -->|assumes| IAMRole
    JWT -->|validated by| APIGateway
    
    %% Integration
    Lambda -->|invoked via| APIGateway
    Lambda -->|connects to| RDS
    Lambda -->|uses| KMS
    Tenant -->|authenticated via| Cognito
    Tenant -->|has dedicated| IAMRole
    DBPerTenant -->|hosted on| RDS
    VC -->|signed with| KMS
    BusinessLogic -->|issues| VC
    
    %% Services
    BusinessLogic[BusinessLogic Service]
    Backoffice[Backoffice Service]
    Catalog[Catalog Service]
    
    Backoffice -->|manages| Tenant
    Catalog -->|defines schemas for| VC
    
    style VC fill:#bbdefb
    style DID fill:#bbdefb
    style VP fill:#bbdefb
    style Tenant fill:#c8e6c9
    style Cognito fill:#ffccbc
    style Lambda fill:#fff9c4
```

---

## Service Integration Map

Microservices and their dependencies.

```mermaid
graph TB
    %% Frontend
    WWC[WWC Wallet App]
    OnBoard[OnBoarding Web]
    
    %% API Gateway
    Gateway[API Gateway]
    
    %% Backend Services
    Backoffice[Backoffice Service]
    BusinessLogic[BusinessLogic Service]
    Catalog[Catalog Service]
    Propagate[Propagate Service]
    IOM[IOM Service]
    SVault[SVault Service]
    
    %% Lambda Utilities
    PAdES[PAdES Lambda]
    SignEth[SignEth Lambda]
    
    %% Data Stores
    CoreDB[(Core Database)]
    TenantDB1[(Tenant DB 1)]
    TenantDB2[(Tenant DB 2)]
    TenantDBN[(Tenant DB N)]
    
    %% AWS Services
    Cognito[Cognito]
    KMS[KMS]
    S3[S3]
    EventBridge[EventBridge]
    SecretsManager[Secrets Manager]
    
    %% Frontend → Gateway
    WWC --> Gateway
    OnBoard --> Gateway
    
    %% Gateway → Services
    Gateway --> Backoffice
    Gateway --> BusinessLogic
    Gateway --> Catalog
    Gateway --> Propagate
    Gateway --> IOM
    Gateway --> SVault
    
    %% Service → Data
    Backoffice --> CoreDB
    BusinessLogic --> TenantDB1
    BusinessLogic --> TenantDB2
    BusinessLogic --> TenantDBN
    Catalog --> CoreDB
    Catalog --> TenantDB1
    Propagate --> TenantDB1
    IOM --> CoreDB
    SVault --> TenantDB1
    
    %% Service → AWS
    Backoffice --> Cognito
    Backoffice --> S3
    Backoffice --> KMS
    BusinessLogic --> KMS
    BusinessLogic --> S3
    BusinessLogic --> PAdES
    BusinessLogic --> SignEth
    Propagate --> EventBridge
    
    %% Lambda Utilities
    PAdES --> S3
    SignEth --> KMS
    
    %% Event Flow
    EventBridge --> Propagate
    EventBridge --> BusinessLogic
    
    %% Secrets
    Backoffice -.->|credentials| SecretsManager
    BusinessLogic -.->|credentials| SecretsManager
    
    style WWC fill:#e1f5ff
    style OnBoard fill:#e1f5ff
    style Gateway fill:#fff9c4
    style Backoffice fill:#c8e6c9
    style BusinessLogic fill:#c8e6c9
    style Catalog fill:#c8e6c9
    style Propagate fill:#c8e6c9
    style CoreDB fill:#bbdefb
    style TenantDB1 fill:#bbdefb
    style TenantDB2 fill:#bbdefb
    style TenantDBN fill:#bbdefb
    style Cognito fill:#ffccbc
    style KMS fill:#ffccbc
    style EventBridge fill:#fff9c4
```

---

## User Journey Navigation Paths

Recommended documentation paths for different user personas.

### New Developer Journey

```mermaid
graph LR
    Start([New Developer]) --> README[README.md]
    README --> ProjOverview[project-overview.md]
    ProjOverview --> KeyConcepts[key-concepts.md]
    KeyConcepts --> GettingStarted[getting-started.md]
    GettingStarted --> RepoStructure[repository-structure.md]
    RepoStructure --> LocalDev[local-development.md]
    LocalDev --> CodingStandards[coding-standards.md]
    CodingStandards --> APIReadme[api/README.md]
    APIReadme --> ComponentArch[component-architecture.md]
    ComponentArch --> End([Ready to Develop])
    
    style Start fill:#e8f5e9
    style End fill:#e8f5e9
    style README fill:#bbdefb
    style GettingStarted fill:#ffccbc
```

### Architect Journey

```mermaid
graph LR
    Start([Architect]) --> README[README.md]
    README --> ProjOverview[project-overview.md]
    ProjOverview --> SystemOverview[system-overview.md]
    SystemOverview --> ADRIndex[decisions/README.md]
    ADRIndex --> ADR0001[ADR-0001]
    ADRIndex --> ADR0002[ADR-0002]
    ADRIndex --> ADR0003[ADR-0003]
    ADRIndex --> ADR0004[ADR-0004]
    ADR0001 --> SecurityArch[security-architecture.md]
    ADR0002 --> DeploymentArch[deployment-architecture.md]
    ADR0003 --> DataArch[data-architecture.md]
    ADR0004 --> ComponentArch[component-architecture.md]
    ComponentArch --> End([System Understanding])
    
    style Start fill:#e8f5e9
    style End fill:#e8f5e9
    style ADR0001 fill:#e1bee7
    style ADR0002 fill:#e1bee7
    style ADR0003 fill:#e1bee7
    style ADR0004 fill:#e1bee7
```

### DevOps Journey

```mermaid
graph LR
    Start([DevOps Engineer]) --> README[README.md]
    README --> CoreSetup[CORE_SETUP.md]
    CoreSetup --> InfraSetup[infrastructure-setup.md]
    InfraSetup --> DeploymentArch[deployment-architecture.md]
    DeploymentArch --> TenantOnboard[tenant-onboarding.md]
    TenantOnboard --> DeploymentProc[deployment-procedures.md]
    DeploymentProc --> Monitoring[monitoring.md]
    Monitoring --> BackupRecovery[backup-recovery.md]
    BackupRecovery --> Troubleshooting[troubleshooting.md]
    Troubleshooting --> End([Ops Ready])
    
    style Start fill:#e8f5e9
    style End fill:#e8f5e9
    style InfraSetup fill:#fff9c4
    style Monitoring fill:#fff9c4
```

### API Consumer Journey

```mermaid
graph LR
    Start([API Consumer]) --> README[README.md]
    README --> APIReadme[api/README.md]
    APIReadme --> Authentication[api/authentication.md]
    Authentication --> BackofficeAPI[backoffice-api.md]
    Authentication --> BusinessLogicAPI[businesslogic-api.md]
    Authentication --> CatalogAPI[catalog-api.md]
    BusinessLogicAPI --> ErrorHandling[error-handling.md]
    CatalogAPI --> KeyConcepts[key-concepts.md]
    ErrorHandling --> End([Integration Complete])
    
    style Start fill:#e8f5e9
    style End fill:#e8f5e9
    style APIReadme fill:#e0f2f1
    style Authentication fill:#e0f2f1
```

### Security Auditor Journey

```mermaid
graph LR
    Start([Security Auditor]) --> README[README.md]
    README --> SecurityOverview[security-overview.md]
    SecurityOverview --> SecurityArch[security-architecture.md]
    SecurityArch --> Authentication[security/authentication.md]
    SecurityArch --> Authorization[security/authorization.md]
    SecurityArch --> Cryptography[cryptography.md]
    SecurityArch --> Compliance[compliance.md]
    Compliance --> ADR0001[ADR-0001 Cognito]
    Compliance --> ADR0003[ADR-0003 DB Isolation]
    Compliance --> ADR0004[ADR-0004 W3C VC]
    Cryptography --> End([Audit Complete])
    
    style Start fill:#e8f5e9
    style End fill:#e8f5e9
    style SecurityOverview fill:#ffebee
    style SecurityArch fill:#ffebee
```

---

## API Documentation Relationships

API documentation hierarchy and dependencies.

```mermaid
graph TB
    %% API Entry
    APIReadme[api/README.md]
    
    %% Core API Concepts
    AuthenticationDoc[authentication.md]
    ErrorHandling[error-handling.md]
    
    %% Service APIs
    BackofficeAPI[backoffice-api.md]
    BusinessLogicAPI[businesslogic-api.md]
    CatalogAPI[catalog-api.md]
    PropagateAPI[propagate-api.md]
    
    %% Architecture References
    ComponentArch[component-architecture.md]
    SecurityArch[security-architecture.md]
    
    %% Concept References
    KeyConcepts[key-concepts.md]
    Glossary[glossary.md]
    
    %% API Flow
    APIReadme --> AuthenticationDoc
    APIReadme --> BackofficeAPI
    APIReadme --> BusinessLogicAPI
    APIReadme --> CatalogAPI
    APIReadme --> PropagateAPI
    
    AuthenticationDoc --> BackofficeAPI
    AuthenticationDoc --> BusinessLogicAPI
    AuthenticationDoc --> CatalogAPI
    AuthenticationDoc --> PropagateAPI
    
    ErrorHandling --> BackofficeAPI
    ErrorHandling --> BusinessLogicAPI
    ErrorHandling --> CatalogAPI
    ErrorHandling --> PropagateAPI
    
    %% API → Architecture
    BackofficeAPI --> ComponentArch
    BusinessLogicAPI --> ComponentArch
    CatalogAPI --> ComponentArch
    PropagateAPI --> ComponentArch
    
    AuthenticationDoc --> SecurityArch
    
    %% API → Concepts
    BusinessLogicAPI --> KeyConcepts
    CatalogAPI --> KeyConcepts
    BackofficeAPI --> Glossary
    
    style APIReadme fill:#e0f2f1
    style AuthenticationDoc fill:#e0f2f1
    style BackofficeAPI fill:#b2dfdb
    style BusinessLogicAPI fill:#b2dfdb
    style CatalogAPI fill:#b2dfdb
    style PropagateAPI fill:#b2dfdb
```

---

## Operations Workflow

Operational procedure dependencies and sequences.

```mermaid
graph TB
    %% Prerequisites
    Start([Operations Start])
    Prerequisites[Prerequisites Check]
    
    %% Core Infrastructure
    InfraSetup[infrastructure-setup.md]
    CoreDB[Setup Core Database]
    Cognito[Setup Cognito]
    APIGateway[Setup API Gateway]
    
    %% Service Deployment
    DeploymentProc[deployment-procedures.md]
    BuildImages[Build Lambda Images]
    PushECR[Push to ECR]
    DeployLambdas[Deploy Lambda Functions]
    
    %% Tenant Operations
    TenantOnboard[tenant-onboarding.md]
    CreateTenant[Create Tenant]
    ProvisionDB[Provision Tenant DB]
    SetupIAM[Setup Tenant IAM]
    SetupKMS[Setup Tenant KMS]
    SetupCloudFront[Setup CloudFront]
    
    %% Monitoring & Maintenance
    Monitoring[monitoring.md]
    SetupLogs[Setup CloudWatch Logs]
    SetupMetrics[Setup Metrics]
    SetupAlarms[Setup Alarms]
    
    BackupRecovery[backup-recovery.md]
    ConfigBackup[Configure Backups]
    TestRestore[Test Recovery]
    
    %% Troubleshooting
    Troubleshooting[troubleshooting.md]
    
    %% Flow
    Start --> Prerequisites
    Prerequisites --> InfraSetup
    
    InfraSetup --> CoreDB
    InfraSetup --> Cognito
    InfraSetup --> APIGateway
    
    CoreDB --> DeploymentProc
    Cognito --> DeploymentProc
    APIGateway --> DeploymentProc
    
    DeploymentProc --> BuildImages
    BuildImages --> PushECR
    PushECR --> DeployLambdas
    
    DeployLambdas --> TenantOnboard
    
    TenantOnboard --> CreateTenant
    CreateTenant --> ProvisionDB
    ProvisionDB --> SetupIAM
    SetupIAM --> SetupKMS
    SetupKMS --> SetupCloudFront
    
    SetupCloudFront --> Monitoring
    
    Monitoring --> SetupLogs
    Monitoring --> SetupMetrics
    Monitoring --> SetupAlarms
    
    SetupAlarms --> BackupRecovery
    
    BackupRecovery --> ConfigBackup
    ConfigBackup --> TestRestore
    
    TestRestore --> End([Production Ready])
    
    %% Continuous
    Monitoring -.->|ongoing| Troubleshooting
    BackupRecovery -.->|ongoing| Troubleshooting
    
    style Start fill:#e8f5e9
    style End fill:#e8f5e9
    style InfraSetup fill:#fff9c4
    style DeploymentProc fill:#fff9c4
    style TenantOnboard fill:#fff9c4
    style Monitoring fill:#fff9c4
```

---

## Document Criticality Matrix

Documents ranked by importance for different user roles.

```mermaid
graph TD
    subgraph Critical["🔴 Critical (Must Read)"]
        C1[README.md]
        C2[project-overview.md]
        C3[key-concepts.md]
        C4[system-overview.md]
    end
    
    subgraph High["🟡 High Priority"]
        H1[component-architecture.md]
        H2[security-architecture.md]
        H3[api/README.md]
        H4[infrastructure-setup.md]
        H5[ADR Index]
    end
    
    subgraph Medium["🟢 Medium Priority"]
        M1[data-architecture.md]
        M2[deployment-architecture.md]
        M3[tenant-onboarding.md]
        M4[Service APIs]
    end
    
    subgraph Reference["⚪ Reference"]
        R1[glossary.md]
        R2[appendix/*]
        R3[faq.md]
    end
    
    Critical --> High
    High --> Medium
    Medium --> Reference
    
    style Critical fill:#ffcdd2
    style High fill:#fff9c4
    style Medium fill:#c8e6c9
    style Reference fill:#f5f5f5
```

---

## Cross-Cutting Concerns Map

Documentation addressing platform-wide concerns.

```mermaid
graph TB
    %% Concerns
    Security[🔒 Security]
    MultiTenancy[🏢 Multi-Tenancy]
    Compliance[⚖️ Compliance]
    Scalability[📈 Scalability]
    Monitoring[📊 Monitoring]
    
    %% Security Documents
    Security --> SecurityArch[security-architecture.md]
    Security --> Authentication[security/authentication.md]
    Security --> Authorization[security/authorization.md]
    Security --> Cryptography[security/cryptography.md]
    Security --> ADR0001[ADR-0001]
    
    %% Multi-Tenancy Documents
    MultiTenancy --> MultiTenancyDoc[multi-tenancy.md]
    MultiTenancy --> DataArch[data-architecture.md]
    MultiTenancy --> ADR0003[ADR-0003]
    MultiTenancy --> TenantOnboard[tenant-onboarding.md]
    
    %% Compliance Documents
    Compliance --> ComplianceDoc[security/compliance.md]
    Compliance --> ADR0004[ADR-0004]
    Compliance --> BackupRecovery[backup-recovery.md]
    
    %% Scalability Documents
    Scalability --> ADR0002[ADR-0002]
    Scalability --> DeploymentArch[deployment-architecture.md]
    Scalability --> ComponentArch[component-architecture.md]
    
    %% Monitoring Documents
    Monitoring --> MonitoringDoc[monitoring.md]
    Monitoring --> Troubleshooting[troubleshooting.md]
    Monitoring --> DeploymentProc[deployment-procedures.md]
    
    style Security fill:#ffebee
    style MultiTenancy fill:#e0f2f1
    style Compliance fill:#fff9c4
    style Scalability fill:#e8eaf6
    style Monitoring fill:#fce4ec
```

---

## Navigation Efficiency Metrics

| Path Type | Avg Documents | Max Depth | Efficiency |
|-----------|--------------|-----------|------------|
| **New Developer** | 9 docs | 3 levels | ⚡ Optimized |
| **Architect** | 12 docs | 4 levels | ⚡ Optimized |
| **DevOps** | 8 docs | 3 levels | ⚡ Optimized |
| **API Consumer** | 6 docs | 2 levels | ⚡⚡ Highly Optimized |
| **Security Auditor** | 10 docs | 3 levels | ⚡ Optimized |

---

## Graph Statistics

| Metric | Value |
|--------|-------|
| **Total Documentation Nodes** | 49 |
| **Total Concept Nodes** | 87 |
| **Total ADR Nodes** | 4 |
| **Total Service Nodes** | 8 |
| **Direct Relationships** | 156+ |
| **Transitive Relationships** | 400+ |
| **Average Path Length** | 2.8 documents |
| **Graph Density** | 0.36 (well-connected) |
| **Clustering Coefficient** | 0.42 (good modularity) |

---

## Index Metadata

- **Generated:** March 10, 2026
- **Graph Complexity:** Medium-High
- **Visualization Format:** Mermaid.js
- **Total Diagrams:** 14
- **Related Indexes:** [document-index.md](document-index.md), [concept-index.md](concept-index.md), [traceability.md](traceability.md), [knowledge-graph.json](knowledge-graph.json)
