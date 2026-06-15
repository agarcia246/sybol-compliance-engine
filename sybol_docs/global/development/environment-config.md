Environment
0. Create and buy domain in s3
1. Cognito 
  1.1 Userpool & IdentityPool
  1.2 Appclient -- config custom claims
  1.3 Rol Cognito_sybol_Auth_Role
2. RDS
  2.1 Create and config rds internal access
  2.2 Create backoffice database
    2.2.1 Create users, run schmemas y grant access
  2.3 Create catalog database
    2.3.1 Create users, run schmeas y grant access
3. Red VPC (Acceso lambdas a internet y red interna)
  2.1 Ip etc etc
4. Policy for lambdas which needs tenant role sts access
5. Lambdas (backoffice, businesslogic, propagate, catalog) !!REVISAR TRUST POLICY!!
  5.1 Rol por lambda
  5.2 Attach policy for lambdas with tenant role sts access
  5.3 ECR images, build and push code
  5.4 Env Vars
  5.5 Edit retention log policy
6. Api Gw
  6.1 HTTP API
  6.2 Create routes
  6.3 Integrations with lambda functions
  6.4 Authorization with cognito

Por Tenant

1. Domain: {tenantId}.staging.wallet.sybol.id
2. Certificiate
3. Cloudfront
  3.1 Distribution
  3.2 S3 (build statics) -- config look&feel front -- ¿workflow?
4. Create User in cognito App client con sus custom:attributes
5. RDS
  5.1 Create Database
  5.2 Create user
  5.3 Run schemas (incluiding Create propagate_system user, and grant access)
  5.4 Grant accesses
6. Secret Manager
  6.1 Crear secreto de acceso a rds (tenant/{tenantId}/{tenantRole}-password)
  6.2 Modificar el valor de nombre de la base de datos (database_name)
7. Crear IAM role (TenantRole-{tenantId}-{tenantRole})
  7.1 Añadir a trust policy (sts:AssumeRole y los roles de la cognito, lambda businesslogic y lambda propagate)
  7.2 Añadir a permissions policy el secretsaccess y el kms access
8. Crear kms del tenant (tenant/{tenant_id}/{role}-jwt)
  8.1 Crear politica con el tenantSpecificAccess
  8.2 Añadir permisos de kms a roles del tenant (actualizar tenantrole)
9. Crear did document
  9.1 Llamar a la api/did-document con el did:sybol del nuevo tenant y su identificador de clave kms


Inventario (Por cada Tenant)
 1 Cognito (Userpool, IdentityPool, Appclient, Rol)
 1 (user)
 6 Rol (Cognito_sybol_Auth_Role, businesslogic_lambda, propagate_lambda, catalog_lambda, backoffice_lambda, Tenant_{tenantId})
 1 Subnet (subnet)
 1 Ip 
 2 Security Group (Lambda-sg , RDS-sg)
 4 Lambdas (backoffice, businesslogic, propagate, catalog)
 1 Policy (STS TenantRole Policy, )
 4 Cloudwatch logs groups lambdas

---

## INVENTARIO COMPLETO DE RECURSOS AWS

### CORE (Una sola vez - Compartido)

#### Cognito:
- **1** User Pool (`sybol-user-pool`)
- **1** Identity Pool (`sybol-identity-pool`)
- **1** App Client (`sybol-app-client`)
- **1** IAM Role (`Cognito_sybol_Auth_Role`)

#### RDS PostgreSQL:
- **1** Cluster RDS (PostgreSQL 17.4)
  - **1** Writer instance
  - **1** Reader instance (opcional, alta disponibilidad)
- **2** Databases fijas:
  - `backoffice` (con usuarios: backoffice_admin, backoffice_reader)
  - `catalog` (con usuarios: catalog_admin, catalog_reader)
- **1** Usuario global: `propagate_system` (para /receive endpoint)
- **N** Databases por tenant: `tenant_{tenantId}` (creadas dinámicamente)

#### VPC y Networking:
- **1** VPC (`sybol-vpc`) - CIDR: 10.0.0.0/16
- **2** Subnets públicas (multi-AZ):
  - `sybol-public-subnet-1a` (10.0.1.0/24, eu-west-1a)
  - `sybol-public-subnet-1b` (10.0.2.0/24, eu-west-1b)
- **1** Internet Gateway (`sybol-igw`)
- **1** Route Table (con ruta 0.0.0.0/0 → IGW)
- **2** Security Groups:
  - `lambda-sg` (para Lambdas)
  - `rds-sg` (para RDS)
- **0** NAT Gateways (no se utiliza)
- **0** Elastic IPs dedicadas (auto-asignadas por subnet)

#### IAM Policies:
- **1** Policy compartida: `LambdaAssumeTenantRolesPolicy` (permite STS AssumeRole a TenantRole-*)

#### ECR (Elastic Container Registry):
- **4** Repositorios privados:
  - `sybol/backoffice`
  - `sybol/businesslogic`
  - `sybol/propagate`
  - `sybol/catalog`

#### Lambda Functions:
- **4** Lambdas con containers:
  - `backoffice` (512 MB, 30s timeout)
  - `businesslogic` (512 MB, 30s timeout)
  - `propagate` (512 MB, 30s timeout)
  - `catalog` (512 MB, 30s timeout)
- **4** IAM Execution Roles (auto-creados):
  - `backoffice-role-xxxxx`
  - `businesslogic-role-xxxxx` ← Tiene LambdaAssumeTenantRolesPolicy
  - `propagate-role-xxxxx` ← Tiene LambdaAssumeTenantRolesPolicy
  - `catalog-role-xxxxx`
- **4** CloudWatch Log Groups (auto-creados)

#### API Gateway:
- **2** HTTP APIs:
  - `backoffice-api` (rutas: `/{proxy+}`)
  - `sybol-api` (rutas: `/api/bl/{proxy+}`, `/api/ps/{proxy+}`, `/api/catalog/{proxy+}`)
- **1** JWT Authorizer compartido (Cognito)
- **2** Custom domains (opcional):
  - `backoffice.sybol.id`
  - `api.sybol.id`
- **2** ACM Certificates (si se usan custom domains)

#### Secrets Manager:
- **2** Secrets para databases fijas:
  - `backoffice/admin-password`
  - `catalog/admin-password`
- **1** Secret para propagate_system:
  - `rds/propagate-system-password`

---

### POR TENANT (Se crean N veces, una por cada tenant)

#### Frontend y CDN:
- **1** CloudFront Distribution
- **1** S3 Bucket (para archivos estáticos del frontend)
- **1** Custom Domain: `{tenantId}.staging.wallet.sybol.id`
- **1** ACM Certificate (para el dominio custom)

#### Cognito User:
- **1+** Usuarios en el User Pool existente
  - Con attributes: `custom:tenant_id`, `custom:role`
  - Ejemplo: `usuario@repsol.com` con `tenant_id=repsol`, `role=admin`

#### RDS:
- **1** Database: `tenant_{tenantId}`
- **2** Usuarios PostgreSQL por tenant:
  - `{tenantId}_admin`
  - `{tenantId}_reader`
- Permisos INSERT para `propagate_system` en todas las tablas

#### Secrets Manager:
- **2** Secrets por tenant:
  - `tenant/{tenantId}/admin-password`
  - `tenant/{tenantId}/reader-password`

#### IAM Roles:
- **2** IAM Roles por tenant:
  - `TenantRole-{tenantId}-admin`
  - `TenantRole-{tenantId}-reader`
- Cada rol tiene:
  - **Trust Policy** (permite AssumeRole desde Cognito, businessLogic, propagate)
  - **Permissions Policy inline** (acceso a Secrets y KMS del tenant)

#### KMS Keys:
- **2** KMS Keys asimétricas (ECC_NIST_P256) por tenant:
  - `tenant/{tenantId}/admin-jwt` (para firmar JWTs)
  - `tenant/{tenantId}/reader-jwt` (para firmar JWTs)
- **Key Policy** que restringe acceso solo al tenant role correspondiente

#### DID Document:
- **1** DID Document registrado en backoffice database
  - `did:sybol:{uuid}` único por tenant
  - Con referencia a KMS key para firmas

---

## RESUMEN NUMÉRICO

### CORE (Una sola vez):
| Recurso | Cantidad |
|---------|----------|
| Cognito User Pool | 1 |
| Cognito Identity Pool | 1 |
| Cognito App Client | 1 |
| RDS Cluster | 1 |
| Databases fijas | 2 (backoffice, catalog) |
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
| Secrets (DB fijos) | 3 |

**Total CORE:** ~32 recursos

### POR TENANT (× N tenants):
| Recurso | Cantidad por tenant |
|---------|---------------------|
| CloudFront Distribution | 1 |
| S3 Bucket | 1 |
| ACM Certificate | 1 |
| Cognito Users | 1+ |
| RDS Database | 1 |
| RDS Users | 2 |
| Secrets Manager | 2 |
| IAM Roles | 2 |
| KMS Keys | 2 |
| DID Document | 1 |

**Total POR TENANT:** ~13 recursos

### EJEMPLO CON 5 TENANTS:
- **CORE:** 32 recursos
- **TENANTS:** 5 × 13 = 65 recursos
- **TOTAL:** 97 recursos AWS

---

## COSTOS ESTIMADOS MENSUALES (Región eu-west-1)

### CORE (Fijos):
- **RDS Aurora Serverless v2** (0.5-1 ACU): ~$45/mes
- **Lambda invocations** (1M requests, 512MB, 1s avg): ~$20/mes
- **API Gateway** (1M requests): ~$3.50/mes
- **VPC** (Subnets, IGW): $0/mes (sin NAT Gateway)
- **ECR Storage** (4 imágenes × 500MB): ~$2/mes
- **Cognito** (hasta 50k MAU): $0/mes (free tier)

**Subtotal CORE:** ~$70/mes

### POR TENANT:
- **CloudFront** (10 GB transfer): ~$1/mes
- **S3** (1 GB storage, 10k requests): ~$0.50/mes
- **KMS** (2 keys × $1): $2/mes
- **Secrets Manager** (2 secrets × $0.40): $0.80/mes
- **RDS database** (compartido, costo marginal): ~$5/mes

**Subtotal POR TENANT:** ~$9/mes

### TOTAL CON 5 TENANTS:
- **CORE:** $70/mes
- **5 TENANTS:** 5 × $9 = $45/mes
- **TOTAL:** ~$115/mes

### TOTAL CON 20 TENANTS:
- **CORE:** $70/mes
- **20 TENANTS:** 20 × $9 = $180/mes
- **TOTAL:** ~$250/mes

⚠️ **Nota:** Costos aproximados. Varían según uso real (requests, storage, data transfer).

---

## REFERENCIAS RÁPIDAS

### Naming Conventions
```
Databases: tenant_{tenantId}
Secrets: tenant/{tenantId}/{role}-password
KMS Aliases: tenant/{tenantId}/{role}-jwt
IAM Roles: TenantRole-{tenantId}-{role}
DID: did:sybol:{uuid}
Frontend Domain: {tenantId}.staging.wallet.sybol.id
```
