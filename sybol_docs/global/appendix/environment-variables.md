# Environment Variables Reference

## Purpose

This document provides a comprehensive reference for all environment variables used across Sybol services. Use this guide to configure services correctly for development, staging, and production environments.

---

## Variable Type Legend

| Symbol | Meaning |
|--------|---------|
| **✓ Required** | Must be set for service to function |
| **○ Optional** | Has sensible defaults, can be omitted |
| **⚠ Sensitive** | Contains credentials, store in Secrets Manager |

---

## Backoffice Service

The Backoffice service manages tenant administration, user management, and platform configuration.

### Database Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DB_HOST` | ✓ ⚠ | - | RDS PostgreSQL endpoint |
| `DB_PORT` | ○ | `5432` | PostgreSQL port |
| `DB_NAME` | ✓ | - | Database name (typically `backofficedev` or `backoffice`) |
| `DB_USER` | ✓ ⚠ | - | Database username (e.g., `backoffice_admin`) |
| `DB_PASSWORD` | ✓ ⚠ | - | Database password (retrieve from Secrets Manager) |
| `DB_SSL` | ○ | `true` | Enable SSL for database connections |
| `DB_MAX_CONNECTIONS` | ○ | `10` | Maximum database connection pool size |
| `DB_IDLE_TIMEOUT` | ○ | `30000` | Idle connection timeout (milliseconds) |
| `DB_CONNECTION_TIMEOUT` | ○ | `2000` | Connection acquisition timeout (milliseconds) |

### AWS Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `AWS_REGION` | ✓ | - | Primary AWS region (e.g., `eu-west-1`) |
| `AWS_ACCOUNT_ID` | ✓ | - | AWS Account ID (12-digit number) |
| `AWS_SECRETS_REGION` | ○ | `AWS_REGION` | Region for Secrets Manager |

### Cognito Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `COGNITO_USER_POOL_ID` | ✓ | - | User Pool ID (e.g., `eu-west-1_XXXXXXXXX`) |
| `COGNITO_REGION` | ✓ | - | Cognito region (e.g., `eu-west-1`) |
| `COGNITO_CLIENT_ID` | ✓ | - | App Client ID |

### Server Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PORT` | ○ | `3000` | HTTP server port (local development) |
| `NODE_ENV` | ○ | `development` | Node.js environment (`development`, `staging`, `production`) |
| `LOG_LEVEL` | ○ | `info` | Logging level (`error`, `warn`, `info`, `debug`) |

### CORS Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ALLOWED_ORIGINS` | ○ | `*` | Comma-separated list of allowed origins |

### Example .env File

```bash
# Database Configuration
DB_HOST=sybol-cluster.cluster-xxx.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=backofficedev
DB_USER=backoffice_admin
DB_PASSWORD=<retrieve-from-secrets-manager>
DB_SSL=true

# AWS Configuration
AWS_REGION=eu-west-1
AWS_ACCOUNT_ID=123456789012

# Cognito Configuration
COGNITO_USER_POOL_ID=eu-west-1_DfCT76YmS
COGNITO_REGION=eu-west-1
COGNITO_CLIENT_ID=4tj2a7of4sbqctemkhh07vsoe2

# Server Configuration
PORT=3000
NODE_ENV=development
LOG_LEVEL=debug
```

---

## BusinessLogic Service

The BusinessLogic service manages verifiable credential lifecycle operations.

### Database Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DB_HOST` | ✓ ⚠ | - | RDS PostgreSQL endpoint |
| `DB_PORT` | ○ | `5432` | PostgreSQL port |
| `DB_NAME` | ✓ | - | Tenant-specific database (e.g., `tenant_repsol`) |
| `DB_USER` | ✓ ⚠ | - | Database username (e.g., `repsol_admin`) |
| `DB_PASSWORD` | ✓ ⚠ | - | Database password (retrieve from Secrets Manager) |
| `DB_SSL` | ○ | `true` | Enable SSL for database connections |

### AWS Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `AWS_REGION` | ✓ | - | Primary AWS region (e.g., `eu-west-1`) |
| `AWS_TENANT_ROLE_ARN` | ✓ ⚠ | - | Tenant-specific IAM Role ARN for STS AssumeRole |
| `AWS_SECRETS_REGION` | ○ | `AWS_REGION` | Region for Secrets Manager |
| `AWS_SECRET_NAME_PREFIX` | ○ | `tenant` | Prefix for secret names |

### External Service URLs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENTITY_MANAGER_URL` | ✓ | - | Backoffice entity API endpoint |
| `CATALOG_SERVICE_URL` | ✓ | - | Catalog service endpoint |
| `DID_DOCUMENT_SERVICE_URL` | ✓ | - | DID document resolution endpoint |

### API Base URLs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_BASE_URL` | ✓ | - | Base URL for Sybol APIs (e.g., `https://api.sybol.id`) |
| `STATUS_LIST_CREDENTIAL_URL` | ✓ | - | Status list credential endpoint |

### W3C Schema URLs

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `W3C_CREDENTIALS_CONTEXT_V2` | ○ | `https://www.w3.org/ns/credentials/v2` | W3C Verifiable Credentials context URL |
| `W3C_CREDENTIALS_EXAMPLES_V2` | ○ | `https://www.w3.org/ns/credentials/examples/v2` | W3C examples context URL |
| `DEFAULT_CREDENTIAL_SCHEMA` | ○ | `https://api.sybol.id/schemas/credential-schema` | Default credential schema URL |

### JWT Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `JWT_ISSUER_DID` | ✓ | - | DID of the JWT issuer (e.g., `did:sybol:tenant-uuid`) |
| `JWT_ALGORITHM` | ○ | `ES256` | JWT signing algorithm (`ES256`, `RS256`) |
| `JWT_EXPIRES_IN` | ○ | `31536000` | JWT expiration time (seconds, default 1 year) |
| `JWT_KMS_KEY_ID` | ✓ ⚠ | - | KMS Key ID or alias for JWT signing |

### Server Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PORT` | ○ | `3001` | HTTP server port (local development) |
| `NODE_ENV` | ○ | `development` | Node.js environment |
| `LOG_LEVEL` | ○ | `info` | Logging level |
| `API_TIMEOUT` | ○ | `10000` | External API request timeout (milliseconds) |
| `MAX_REQUEST_SIZE` | ○ | `10mb` | Maximum request body size |

### Hedera Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HEDERA_NETWORK` | ○ | `testnet` | Hedera network (`testnet` o `mainnet`) |
| `HEDERA_OPERATOR_ID` | ✓ | - | Account ID del operador Hedera (e.g. `0.0.8570019`) |
| `HEDERA_OPERATOR_KEY` | ✓ ⚠ | - | Clave privada del operador (hex, con o sin prefijo `0x`) |
| `HEDERA_KEY_TYPE` | ○ | `ecdsa` | Tipo de clave del operador: `ecdsa` o `ed25519` |

> ⚠️ **Warning — producción:** `HEDERA_OPERATOR_KEY` es una clave privada que controla la cuenta operadora de Hedera (paga las transacciones HCS). **No debe configurarse como variable de entorno en Lambda en producción.** Debe almacenarse en AWS Secrets Manager bajo el path `hedera/operator/{network}` y leerse en tiempo de ejecución desde `hederaClient.js`. Ver [ADR-hedera-002](../../../docs/poc/adr-hedera-002-key-management.md) para el patrón de migración.

### STS Cache Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `STS_CACHE_DURATION` | ○ | `3600000` | STS credentials cache duration (milliseconds, default 1 hour) |

### Example .env File

```bash
# Database Configuration
DB_HOST=sybol-cluster.cluster-xxx.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=tenant_repsol
DB_USER=repsol_admin
DB_PASSWORD=<retrieve-from-secrets-manager>
DB_SSL=true

# AWS Configuration
AWS_REGION=eu-west-1
AWS_TENANT_ROLE_ARN=arn:aws:iam::123456789012:role/TenantRole-repsol-admin
AWS_SECRET_NAME_PREFIX=tenant

# External Services
ENTITY_MANAGER_URL=https://backoffice.sybol.id/api/entity
CATALOG_SERVICE_URL=https://api.sybol.id/api/catalog/catalog-entries
DID_DOCUMENT_SERVICE_URL=https://backoffice.sybol.id/api/did-document

# API Base URLs
API_BASE_URL=https://api.sybol.id
STATUS_LIST_CREDENTIAL_URL=https://api.sybol.id/credentials/status-list

# W3C Configuration
W3C_CREDENTIALS_CONTEXT_V2=https://www.w3.org/ns/credentials/v2
DEFAULT_CREDENTIAL_SCHEMA=https://api.sybol.id/schemas/credential-schema

# JWT Configuration
JWT_ISSUER_DID=did:sybol:repsol-uuid
JWT_ALGORITHM=ES256
JWT_EXPIRES_IN=31536000
JWT_KMS_KEY_ID=alias/tenant/repsol/admin-jwt

# Hedera Configuration
HEDERA_NETWORK=testnet
HEDERA_OPERATOR_ID=0.0.xxxxxxx
HEDERA_OPERATOR_KEY=0x<hex-private-key>   # ⚠ En producción usar Secrets Manager
HEDERA_KEY_TYPE=ecdsa

# Server Configuration
PORT=3001
NODE_ENV=development
LOG_LEVEL=debug
STS_CACHE_DURATION=3600000
```

---

## Catalog Service

The Catalog service manages credential templates, schemas, and claim definitions.

### Database Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DB_HOST` | ✓ ⚠ | - | RDS PostgreSQL endpoint |
| `DB_PORT` | ○ | `5432` | PostgreSQL port |
| `DB_NAME` | ✓ | - | Database name (`catalog`) |
| `DB_USER` | ✓ ⚠ | - | Database username (e.g., `catalog_admin`) |
| `DB_PASSWORD` | ✓ ⚠ | - | Database password |
| `DB_SSL` | ○ | `true` | Enable SSL connections |
| `DB_MAX_CONNECTIONS` | ○ | `10` | Maximum connection pool size |

### AWS Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `AWS_REGION` | ✓ | - | Primary AWS region (e.g., `eu-west-1`) |
| `SYBOL_AWS_REGION` | ○ | `AWS_REGION` | Sybol-specific AWS region (deprecated, use AWS_REGION) |

### Cognito Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `COGNITO_USER_POOL_ID` | ✓ | - | User Pool ID |
| `COGNITO_REGION` | ✓ | - | Cognito region |

### Server Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PORT` | ○ | `3002` | HTTP server port |
| `NODE_ENV` | ○ | `development` | Node.js environment |
| `LOG_LEVEL` | ○ | `info` | Logging level |
| `ALLOWED_ORIGINS` | ○ | `*` | CORS allowed origins |

### Example .env File

```bash
# Database Configuration
DB_HOST=sybol-cluster.cluster-xxx.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=catalog
DB_USER=catalog_admin
DB_PASSWORD=<retrieve-from-secrets-manager>
DB_SSL=true

# AWS Configuration
AWS_REGION=eu-west-1

# Cognito Configuration
COGNITO_USER_POOL_ID=eu-west-1_DfCT76YmS
COGNITO_REGION=eu-west-1

# Server Configuration
PORT=3002
NODE_ENV=development
LOG_LEVEL=debug
```

---

## Propagate Service

The Propagate service handles cross-tenant event propagation and credential delivery.

### Database Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DB_HOST` | ✓ ⚠ | - | RDS PostgreSQL endpoint |
| `DB_PORT` | ○ | `5432` | PostgreSQL port |
| `DB_USER` | ✓ ⚠ | `propagate_system` | Global propagate system user |
| `DB_PASSWORD` | ✓ ⚠ | - | Propagate system password (from Secrets Manager) |
| `DB_SSL` | ○ | `true` | Enable SSL connections |

### AWS Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `AWS_REGION` | ✓ | - | Primary AWS region |
| `AWS_TENANT_ROLE_ARN` | ✓ ⚠ | - | Tenant-specific IAM Role ARN (for authenticated endpoints) |

### EventBridge Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EVENTBRIDGE_BUS_NAME` | ○ | `default` | EventBridge event bus name |

### Server Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PORT` | ○ | `3003` | HTTP server port |
| `NODE_ENV` | ○ | `development` | Node.js environment |
| `LOG_LEVEL` | ○ | `info` | Logging level |

### Example .env File

```bash
# Database Configuration
DB_HOST=sybol-cluster.cluster-xxx.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_USER=propagate_system
DB_PASSWORD=<retrieve-from-secrets-manager>
DB_SSL=true

# AWS Configuration
AWS_REGION=eu-west-1

# Server Configuration
PORT=3003
NODE_ENV=development
LOG_LEVEL=debug
```

---

## WWC Wallet Web Application

The WWC (Web Wallet Client) is a React-based frontend application for credential holders.

### Cognito Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REACT_APP_COGNITO_REGION` | ✓ | - | Cognito region (e.g., `eu-west-1`) |
| `REACT_APP_COGNITO_USER_POOL_ID` | ✓ | - | User Pool ID |
| `REACT_APP_COGNITO_CLIENT_ID` | ✓ | - | App Client ID |

### API Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REACT_APP_API_BASE_URL` | ✓ | - | Base URL for backend APIs |
| `REACT_APP_BUSINESS_LOGIC_API` | ○ | `/api/bl` | BusinessLogic service path |
| `REACT_APP_CATALOG_API` | ○ | `/api/catalog` | Catalog service path |

### Example .env File

```bash
# AWS Cognito Configuration
REACT_APP_COGNITO_REGION=eu-west-1
REACT_APP_COGNITO_USER_POOL_ID=eu-west-1_DfCT76YmS
REACT_APP_COGNITO_CLIENT_ID=4tj2a7of4sbqctemkhh07vsoe2

# API Configuration
REACT_APP_API_BASE_URL=https://api.sybol.id
```

---

## Core Infrastructure Variables

These environment variables are used by the CDK infrastructure deployment scripts.

### CoreInfra CDK Stack

| Variable | Type | Description |
|----------|------|-------------|
| `AWS_ACCOUNT` | ✓ | AWS Account ID (12-digit) |
| `AWS_REGION` | ✓ | Deployment region (e.g., `eu-west-1`) |
| `ENVIRONMENT` | ✓ | Environment name (`dev`, `staging`, `production`) |
| `VPC_CIDR` | ○ | VPC CIDR block (default: `10.0.0.0/16`) |
| `RDS_MASTER_USERNAME` | ✓ | RDS master username |
| `RDS_MASTER_PASSWORD` | ✓ ⚠ | RDS master password (store in Secrets Manager) |
| `COGNITO_DOMAIN_PREFIX` | ✓ | Cognito domain prefix |

### ClientInfra CDK Stack

| Variable | Type | Description |
|----------|------|-------------|
| `TENANT_ID` | ✓ | Tenant identifier (lowercase alphanumeric) |
| `TENANT_DOMAIN` | ✓ | Tenant custom domain (e.g., `repsol.staging.wallet.sybol.id`) |
| `ADMIN_EMAIL` | ✓ | Tenant administrator email |
| `CERTIFICATE_ARN` | ✓ | ACM certificate ARN (us-east-1 for CloudFront) |

---

## Secrets Manager Configuration

Sybol uses AWS Secrets Manager to store sensitive configuration values. Secrets follow a naming convention for easy identification.

### Secret Naming Conventions

| Secret Name Pattern | Description | Example |
|---------------------|-------------|---------|
| `backoffice/admin-password` | Backoffice database password | - |
| `catalog/admin-password` | Catalog database password | - |
| `rds/propagate-system-password` | Propagate system user password | - |
| `tenant/{tenantId}/admin-password` | Tenant admin database password | `tenant/repsol/admin-password` |
| `tenant/{tenantId}/reader-password` | Tenant reader database password | `tenant/repsol/reader-password` |

### Secret Structure

Database secrets use JSON format:

```json
{
  "username": "repsol_admin",
  "password": "SecureRandomPassword123!",
  "engine": "postgres",
  "host": "sybol-cluster.cluster-xxx.eu-west-1.rds.amazonaws.com",
  "port": 5432,
  "dbname": "tenant_repsol"
}
```

### Retrieving Secrets in Code

```javascript
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager({ region: process.env.AWS_REGION });

async function getDatabaseCredentials(tenantId, role) {
  const secretName = `tenant/${tenantId}/${role}-password`;
  const data = await secretsManager.getSecretValue({ SecretId: secretName }).promise();
  return JSON.parse(data.SecretString);
}
```

---

## KMS Configuration

KMS keys are used for cryptographic operations (JWT signing, credential signing).

### KMS Key Aliases

| Alias Pattern | Purpose | Example |
|---------------|---------|---------|
| `tenant/{tenantId}/admin-jwt` | Admin role JWT signing | `tenant/repsol/admin-jwt` |
| `tenant/{tenantId}/reader-jwt` | Reader role JWT signing | `tenant/repsol/reader-jwt` |

### KMS Key Specifications

| Parameter | Value |
|-----------|-------|
| Key Type | Asymmetric |
| Key Spec | `ECC_NIST_P256` |
| Key Usage | `SIGN_VERIFY` |
| Algorithm | `ECDSA_SHA_256` |

### Using KMS for JWT Signing

Environment variable configuration:

```bash
JWT_KMS_KEY_ID=alias/tenant/repsol/admin-jwt
JWT_ALGORITHM=ES256
```

---

## Sumsub Integration Variables

Sumsub is used for Know Your Business (KYB) verification in the onboarding process.

| Variable | Type | Description |
|----------|------|-------------|
| `SUMSUB_APP_TOKEN` | ✓ ⚠ | Sumsub API application token |
| `SUMSUB_SECRET_KEY` | ✓ ⚠ | Sumsub secret key for request signing |
| `SUMSUB_BASE_URL` | ○ | Sumsub API base URL (default: `https://api.sumsub.com`) |
| `SUMSUB_WEBHOOK_SECRET` | ✓ ⚠ | Webhook signature verification secret |

---

## Environment-Specific Configuration

### Development Environment

```bash
NODE_ENV=development
LOG_LEVEL=debug
DB_SSL=false
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Staging Environment

```bash
NODE_ENV=staging
LOG_LEVEL=info
DB_SSL=true
ALLOWED_ORIGINS=https://*.staging.wallet.sybol.id
API_BASE_URL=https://api.staging.sybol.id
```

### Production Environment

```bash
NODE_ENV=production
LOG_LEVEL=warn
DB_SSL=true
ALLOWED_ORIGINS=https://*.wallet.sybol.id
API_BASE_URL=https://api.sybol.id
```

---

## Validation Checklist

Before deploying a service, verify:

- ✓ All required variables are set
- ✓ Database credentials retrieved from Secrets Manager
- ✓ KMS keys exist and have correct permissions
- ✓ IAM roles have necessary policies attached
- ✓ URLs use correct environment domain
- ✓ Cognito IDs match deployed User Pool
- ✓ Sensitive values never committed to version control

---

## References

- [Infrastructure Setup](../operations/infrastructure-setup.md)
- [Tenant Onboarding](../operations/tenant-onboarding.md)
- [Security Architecture](../architecture/security-architecture.md)
- [Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
