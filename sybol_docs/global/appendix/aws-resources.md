# AWS Resources Inventory

## Purpose

This document provides a comprehensive inventory of all AWS resources used by the Sybol platform, organized by deployment scope (core vs. per-tenant), with resource naming conventions, cost estimates, and capacity planning guidance.

---

## Resource Organization

Sybol resources are organized into two categories:

- **Core Resources**: Deployed once, shared across all tenants
- **Per-Tenant Resources**: Deployed for each customer tenant

---

## Core Resources (One-Time Setup)

Core resources are provisioned once during initial platform setup and shared across all tenants.

### Cognito

| Resource | Quantity | Name/ID | Description |
|----------|----------|---------|-------------|
| User Pool | 1 | `sybol-user-pool` | Central identity provider |
| Identity Pool | 1 | `sybol-identity-pool` | AWS credentials provider |
| App Client | 1 | `sybol-app-client` | OAuth 2.0 client |
| IAM Role | 1 | `Cognito_sybol_Auth_Role` | Authenticated user role |

**Configuration:**
- Sign-in: Email only
- Password policy: Min 12 chars, uppercase, lowercase, numbers, symbols
- MFA: Optional (TOTP)
- Advanced security: Enabled
- Custom attributes: `custom:tenant_id`, `custom:role`, `custom:organization`

### RDS PostgreSQL

| Resource | Quantity | Name/ID | Description |
|----------|----------|---------|-------------|
| Aurora Cluster | 1 | `sybol-cluster` | PostgreSQL 17.4 serverless cluster |
| Writer Instance | 1 | `sybol-cluster-instance-1` | Primary write instance |
| Reader Instance | 0-1 | `sybol-cluster-instance-2` | Optional read replica |

**Fixed Databases:**

| Database | Users | Purpose |
|----------|-------|---------|
| `backofficedev` / `backoffice` | `backoffice_admin`, `backoffice_reader` | Platform administration |
| `catalog` | `catalog_admin`, `catalog_reader` | Credential templates and schemas |

**Global User:**
- `propagate_system`: Global user with INSERT permissions on all tenant databases

**Tenant Databases:**
- Pattern: `tenant_{tenantId}` (created dynamically per tenant)

**Configuration:**
- Engine: Aurora PostgreSQL Serverless v2
- Version: PostgreSQL 17.4
- Capacity: 0.5-2 ACU (Aurora Capacity Units)
- Backup retention: 7 days
- Encryption: AES-256 at rest

### VPC and Networking

| Resource | Quantity | Name/ID | CIDR/Config |
|----------|----------|---------|-------------|
| VPC | 1 | `sybol-vpc` | 10.0.0.0/16 |
| Public Subnet 1 | 1 | `sybol-public-subnet-1a` | 10.0.1.0/24 (eu-west-1a) |
| Public Subnet 2 | 1 | `sybol-public-subnet-1b` | 10.0.2.0/24 (eu-west-1b) |
| Internet Gateway | 1 | `sybol-igw` | Attached to VPC |
| Route Table | 1 | `sybol-public-rt` | Route: 0.0.0.0/0 → IGW |
| Security Group (Lambda) | 1 | `lambda-sg` | Egress: all, Ingress: none |
| Security Group (RDS) | 1 | `rds-sg` | Ingress: 5432 from lambda-sg |

**Network Design:**
- **No NAT Gateway**: Lambdas in public subnets with direct internet access
- **No Elastic IPs**: Auto-assigned public IPs per subnet
- **Multi-AZ**: Resources distributed across two availability zones

### IAM Policies

| Resource | Quantity | Name | Description |
|----------|----------|------|-------------|
| Policy | 1 | `LambdaAssumeTenantRolesPolicy` | Allows BusinessLogic and Propagate Lambdas to assume tenant-specific roles via STS |

**Policy Statement:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::*:role/TenantRole-*"
    }
  ]
}
```

### Elastic Container Registry (ECR)

| Repository | Purpose | Image Size (approx) |
|------------|---------|---------------------|
| `sybol/backoffice` | Backoffice service container | ~300 MB |
| `sybol/businesslogic` | BusinessLogic service container | ~350 MB |
| `sybol/propagate` | Propagate service container | ~280 MB |
| `sybol/catalog` | Catalog service container | ~300 MB |

**Configuration:**
- Scan on push: Enabled
- Tag immutability: Disabled
- Lifecycle policy: Keep last 10 images

### Lambda Functions

| Function | RAM | Timeout | Execution Role | Dependencies |
|----------|-----|---------|----------------|--------------|
| `backoffice` | 512 MB | 30s | `backoffice-role-xxxxx` | RDS, Cognito, SES, Secrets Manager |
| `businesslogic` | 512 MB | 30s | `businesslogic-role-xxxxx` | RDS, KMS, STS, Secrets Manager |
| `propagate` | 512 MB | 30s | `propagate-role-xxxxx` | RDS, STS, EventBridge |
| `catalog` | 512 MB | 30s | `catalog-role-xxxxx` | RDS, Secrets Manager |

**Configuration:**
- Package type: Container image
- Architecture: x86_64
- VPC: `sybol-vpc` (both subnets)
- Security group: `lambda-sg`
- Reserved concurrency: None (default 1000)
- Ephemeral storage: 512 MB

**IAM Permissions:**

All Lambda execution roles have:
- `AWSLambdaVPCAccessExecutionRole` (managed policy)
- CloudWatch Logs write permissions (auto-created)

BusinessLogic and Propagate roles additionally have:
- `LambdaAssumeTenantRolesPolicy` (custom policy)

### CloudWatch Log Groups

| Log Group | Retention | Description |
|-----------|-----------|-------------|
| `/aws/lambda/backoffice` | 7 days | Backoffice service logs |
| `/aws/lambda/businesslogic` | 7 days | BusinessLogic service logs |
| `/aws/lambda/propagate` | 7 days | Propagate service logs |
| `/aws/lambda/catalog` | 7 days | Catalog service logs |

### API Gateway

| Resource | Type | Name | Configuration |
|----------|------|------|---------------|
| HTTP API | Public | `backoffice-api` | Routes: `/{proxy+}` |
| HTTP API | Public | `sybol-api` | Routes: `/api/bl/{proxy+}`, `/api/ps/{proxy+}`, `/api/catalog/{proxy+}` |
| JWT Authorizer | Shared | `cognito-authorizer` | User Pool: `sybol-user-pool` |

**Custom Domains (Optional):**
- `backoffice.sybol.id` → `backoffice-api`
- `api.sybol.id` → `sybol-api`

**Configuration:**
- Protocol: HTTP
- CORS: Configured per service
- Throttling: 10,000 requests per second (default)
- Stage: `$default`

### ACM Certificates (Core)

| Certificate | Domain | Region | Purpose |
|-------------|--------|--------|---------|
| Core API Cert | `*.sybol.id` | eu-west-1 | API Gateway custom domains |

### Secrets Manager (Core)

| Secret Name | Content | Description |
|-------------|---------|-------------|
| `backoffice/admin-password` | Database credentials JSON | Backoffice database password |
| `catalog/admin-password` | Database credentials JSON | Catalog database password |
| `rds/propagate-system-password` | Database credentials JSON | Propagate system user password |

**Secret Structure:**

```json
{
  "username": "backoffice_admin",
  "password": "SecureRandomPassword",
  "engine": "postgres",
  "host": "sybol-cluster.cluster-xxx.eu-west-1.rds.amazonaws.com",
  "port": 5432,
  "dbname": "backofficedev"
}
```

---

## Core Resources Summary

| Resource Type | Count |
|---------------|-------|
| Cognito User Pool | 1 |
| Cognito Identity Pool | 1 |
| Cognito App Client | 1 |
| RDS Aurora Cluster | 1 |
| Fixed Databases | 2 |
| VPC | 1 |
| Subnets | 2 |
| Internet Gateway | 1 |
| Security Groups | 2 |
| IAM Policies | 1 |
| ECR Repositories | 4 |
| Lambda Functions | 4 |
| Lambda Execution Roles | 4 |
| CloudWatch Log Groups | 4 |
| HTTP APIs | 2 |
| API Authorizers | 1 |
| Secrets (fixed) | 3 |

**Total Core Resources:** ~32

---

## Per-Tenant Resources

These resources are provisioned once per tenant during onboarding.

### Frontend Hosting

| Resource | Name Pattern | Purpose |
|----------|-------------|---------|
| CloudFront Distribution | `{tenantId}-distribution` | CDN for frontend application |
| S3 Bucket | `{tenantId}-frontend-{random}` | Static website hosting |
| ACM Certificate | - | SSL/TLS for custom domain |
| Route 53 Record | `{tenantId}.staging.wallet.sybol.id` | Custom domain DNS |

**CloudFront Configuration:**
- Origin: S3 bucket (static website)
- Viewer protocol: Redirect HTTP to HTTPS
- Geo restriction: None
- WAF: Optional
- Logging: Disabled (optional)

### Cognito Users

| Resource | Attributes | Description |
|----------|------------|-------------|
| User(s) | `email`, `custom:tenant_id`, `custom:role`, `custom:organization` | Tenant administrator and end users |

**Example:**
- Email: `admin@repsol.com`
- `custom:tenant_id`: `repsol`
- `custom:role`: `admin`

### RDS Database

| Resource | Name Pattern | Description |
|----------|-------------|-------------|
| Database | `tenant_{tenantId}` | Tenant-specific database |
| PostgreSQL User (Admin) | `{tenantId}_admin` | Full access to tenant database |
| PostgreSQL User (Reader) | `{tenantId}_reader` | Read-only access |

**Permissions:**
- `{tenantId}_admin`: ALL privileges on `tenant_{tenantId}`
- `{tenantId}_reader`: SELECT on all tables
- `propagate_system`: INSERT on all tables

### Secrets Manager

| Secret Name | Content | Description |
|-------------|---------|-------------|
| `tenant/{tenantId}/admin-password` | Database credentials JSON | Admin database credentials |
| `tenant/{tenantId}/reader-password` | Database credentials JSON | Reader database credentials |

### IAM Roles

| Role Name | Trust Policy | Permissions |
|-----------|--------------|-------------|
| `TenantRole-{tenantId}-admin` | Cognito, BusinessLogic Lambda, Propagate Lambda | Secrets, KMS, RDS access |
| `TenantRole-{tenantId}-reader` | Cognito, BusinessLogic Lambda | Secrets (reader), KMS (reader) |

**Trust Policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::{accountId}:role/businesslogic-role-xxxxx",
          "arn:aws:iam::{accountId}:role/propagate-role-xxxxx"
        ],
        "Federated": "cognito-identity.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Permissions Policy (Inline):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:eu-west-1:{accountId}:secret:tenant/{tenantId}/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:GetPublicKey",
        "kms:Sign"
      ],
      "Resource": "arn:aws:kms:eu-west-1:{accountId}:key/*",
      "Condition": {
        "StringEquals": {
          "aws:ResourceTag/tenant": "{tenantId}"
        }
      }
    }
  ]
}
```

### KMS Keys

| Key Alias | Key Spec | Usage | Description |
|-----------|----------|-------|-------------|
| `tenant/{tenantId}/admin-jwt` | ECC_NIST_P256 | SIGN_VERIFY | Admin role JWT signing |
| `tenant/{tenantId}/reader-jwt` | ECC_NIST_P256 | SIGN_VERIFY | Reader role JWT signing |

**Key Policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Enable IAM policies",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::{accountId}:root"
      },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow tenant role access",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::{accountId}:role/TenantRole-{tenantId}-admin"
      },
      "Action": [
        "kms:GetPublicKey",
        "kms:Sign",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    }
  ]
}
```

**Key Tags:**
- `tenant`: `{tenantId}`
- `role`: `admin` or `reader`

### DID Document

| Resource | Storage | Description |
|----------|---------|-------------|
| DID Document | Backoffice database | W3C DID document with KMS key references |

**DID Format:** `did:sybol:{uuid}`

**DID Document Structure:**

```json
{
  "id": "did:sybol:550e8400-e29b-41d4-a716-446655440000",
  "verificationMethod": [
    {
      "id": "did:sybol:550e8400-e29b-41d4-a716-446655440000#key-1",
      "type": "JsonWebKey2020",
      "controller": "did:sybol:550e8400-e29b-41d4-a716-446655440000",
      "publicKeyJwk": {
        "kty": "EC",
        "crv": "P-256",
        "x": "...",
        "y": "...",
        "kid": "arn:aws:kms:eu-west-1:account:key/uuid"
      }
    }
  ]
}
```

---

## Per-Tenant Resources Summary

| Resource Type | Count per Tenant |
|---------------|------------------|
| CloudFront Distribution | 1 |
| S3 Bucket | 1 |
| ACM Certificate | 1 |
| Route 53 Record | 1 |
| Cognito Users | 1+ |
| RDS Database | 1 |
| PostgreSQL Users | 2 |
| Secrets Manager | 2 |
| IAM Roles | 2 |
| KMS Keys | 2 |
| DID Document | 1 |

**Total Per-Tenant:** ~14 resources

---

## Total Resource Count Examples

### With 5 Tenants:
- Core: 32 resources
- Tenants: 5 × 14 = 70 resources
- **Total: 102 resources**

### With 20 Tenants:
- Core: 32 resources
- Tenants: 20 × 14 = 280 resources
- **Total: 312 resources**

### With 100 Tenants:
- Core: 32 resources
- Tenants: 100 × 14 = 1,400 resources
- **Total: 1,432 resources**

---

## Resource Naming Conventions

| Resource Type | Naming Pattern | Example |
|---------------|----------------|---------|
| Database | `tenant_{tenantId}` | `tenant_repsol` |
| Database User | `{tenantId}_{role}` | `repsol_admin` |
| Secret | `tenant/{tenantId}/{role}-password` | `tenant/repsol/admin-password` |
| KMS Alias | `tenant/{tenantId}/{role}-jwt` | `tenant/repsol/admin-jwt` |
| IAM Role | `TenantRole-{tenantId}-{role}` | `TenantRole-repsol-admin` |
| S3 Bucket | `{tenantId}-frontend-{random}` | `repsol-frontend-a1b2c3` |
| DID | `did:sybol:{uuid}` | `did:sybol:550e8400-e29b-41d4-a716-446655440000` |
| Domain | `{tenantId}.staging.wallet.sybol.id` | `repsol.staging.wallet.sybol.id` |

---

## Cost Estimates (EU-West-1)

### Monthly Cost Breakdown - Core Resources

| Service | Usage | Unit Cost | Monthly Cost |
|---------|-------|-----------|--------------|
| **RDS Aurora Serverless v2** | 0.5-1 ACU average | $0.12/ACU-hour | $45 |
| **Lambda Invocations** | 1M requests | $0.20/1M | $0.20 |
| **Lambda Compute** | 512 MB, 1s avg | $0.0000166667/GB-s | $8.33 |
| **Lambda Duration** | 1M × 1s × 0.5 GB | - | - |
| **API Gateway** | 1M requests | $3.50/1M | $3.50 |
| **VPC** | 2 subnets, 1 IGW | No charge | $0 |
| **ECR Storage** | 4 images × 300 MB | $0.10/GB-month | $1.20 |
| **Cognito Users** | Up to 50K MAU | Free tier | $0 |
| **CloudWatch Logs** | 1 GB ingested | $0.50/GB | $0.50 |
| **Secrets Manager** | 3 secrets | $0.40/secret | $1.20 |

**Subtotal Core:** ~$60/month (at 1M requests/month)

### Monthly Cost Per Tenant

| Service | Usage | Unit Cost | Monthly Cost |
|---------|-------|-----------|--------------|
| **CloudFront** | 10 GB data transfer | $0.085/GB | $0.85 |
| **CloudFront Requests** | 100K requests | $0.0075/10K | $0.075 |
| **S3 Storage** | 1 GB | $0.023/GB | $0.023 |
| **S3 Requests** | 10K GET | $0.0004/1K | $0.004 |
| **KMS Keys** | 2 symmetric keys | $1/key-month | $2.00 |
| **KMS Sign Operations** | 1K signatures | $0.03/10K | $0.003 |
| **Secrets Manager** | 2 secrets | $0.40/secret | $0.80 |
| **RDS Storage** | 5 GB per database | Included in ACU | $0 |
| **ACM Certificate** | 1 public cert | Free | $0 |

**Subtotal Per Tenant:** ~$4/month

### Total Cost Examples

| Scenario | Core | Tenants | Total |
|----------|------|---------|-------|
| **1 Tenant** | $60 | 1 × $4 = $4 | **$64/month** |
| **5 Tenants** | $60 | 5 × $4 = $20 | **$80/month** |
| **20 Tenants** | $60 | 20 × $4 = $80 | **$140/month** |
| **50 Tenants** | $60 | 50 × $4 = $200 | **$260/month** |
| **100 Tenants** | $60 | 100 × $4 = $400 | **$460/month** |

⚠️ **Note:** Costs vary based on actual usage (API requests, data transfer, RDS capacity).

### Cost Optimization Strategies

1. **RDS Aurora Serverless:** Auto-scales from 0.5 to 2 ACU based on load
2. **Lambda Reserved Concurrency:** Not configured (pay only for actual usage)
3. **CloudWatch Log Retention:** 7 days (reduces storage costs)
4. **S3 Intelligent-Tiering:** Move infrequently accessed objects to cheaper storage
5. **CloudFront Caching:** Reduce origin requests by increasing TTL
6. **ECR Lifecycle Policies:** Keep only last 10 images per repository

---

## Resource Limits and Quotas

### AWS Service Limits

| Service | Limit | Current Usage | Notes |
|---------|-------|---------------|-------|
| Lambda Concurrent Executions | 1,000 | ~100 | Request increase if needed |
| API Gateway Rate Limit | 10,000 req/s | ~100 req/s | Per-account limit |
| RDS Cluster Instances | 40 | 1 | Can add read replicas |
| KMS Keys | 10,000 | 2N (N=tenants) | Soft limit, can request increase |
| Secrets Manager Secrets | 40,000 | 3+2N | No issue expected |
| IAM Roles | 5,000 | 4+2N | Monitor as tenants grow |
| S3 Buckets | 1,000 | N | Hard limit per account |
| CloudFront Distributions | 200 | N | Request increase at ~150 tenants |

### Scaling Considerations

**At 100 Tenants:**
- 200 KMS keys (well within 10K limit)
- 203 secrets (well within 40K limit)
- 204 IAM roles (well within 5K limit)
- 100 S3 buckets (within 1K limit)
- 100 CloudFront distributions (within free quota limit)

**At 200 Tenants:**
- ⚠️ CloudFront distributions near limit (200) - request quota increase
- All other resources well within limits

---

## Resource Tagging Strategy

All resources are tagged for cost allocation and management:

| Tag Key | Tag Value | Purpose |
|---------|-----------|---------|
| `Project` | `sybol` | Identify all Sybol resources |
| `Environment` | `dev`, `staging`, `production` | Environment segregation |
| `ManagedBy` | `CDK`, `Terraform`, `Manual` | Infrastructure management tool |
| `CostCenter` | `engineering`, `operations` | Cost allocation |
| `Tenant` | `{tenantId}` | Per-tenant resources |
| `Component` | `frontend`, `backend`, `database` | Architectural component |

---

## Infrastructure as Code

### Core Infrastructure

- **Repository:** `infraestructure/CoreInfra/`
- **Tool:** AWS CDK (TypeScript)
- **Stack:** `CoreInfraStack`
- **Deployment:** `./deploy-core-infra.sh`

### Tenant Infrastructure

- **Repository:** `infraestructure/ClientInfra/`
- **Tool:** AWS CDK (TypeScript)
- **Stack:** `ClientInfraStack`
- **Deployment:** `./onboard-client.sh {tenantId}`

---

## Monitoring and Alerts

### CloudWatch Alarms

Recommended alarms for production:

| Metric | Threshold | Action |
|--------|-----------|--------|
| Lambda Error Rate | > 5% | SNS notification |
| Lambda Throttles | > 10 | SNS notification |
| RDS CPU Utilization | > 80% | Scale up ACU |
| RDS DatabaseConnections | > 80% max | Investigate connection leaks |
| API Gateway 5XX Errors | > 1% | SNS notification |
| API Gateway Latency | p99 > 3000ms | Investigate slow endpoints |

---

## References

- [Infrastructure Setup](../operations/infrastructure-setup.md)
- [Tenant Onboarding](../operations/tenant-onboarding.md)
- [Deployment Procedures](../operations/deployment-procedures.md)
- [Multi-Tenancy Architecture](../architecture/multi-tenancy.md)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
