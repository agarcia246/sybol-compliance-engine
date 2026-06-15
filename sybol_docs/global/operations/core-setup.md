# 🚀 GUÍA DE DESPLIEGUE INICIAL - INFRAESTRUCTURA CORE

Esta guía detalla paso a paso la configuración inicial de la infraestructura compartida AWS necesaria para el sistema multi-tenant Sybol. **Esta configuración se realiza una sola vez**.

---

## 📋 ÍNDICE

1. [Registrar Dominio](#1-registrar-dominio)
2. [Cognito (Autenticación)](#2-cognito)
3. [RDS PostgreSQL](#3-rds-postgresql)
4. [VPC y Red](#4-vpc-y-red)
5. [IAM Policies para STS](#5-iam-policies-para-sts)
6. [Lambdas y ECR](#6-lambdas-y-ecr)
7. [API Gateway](#7-api-gateway)
8. [EventBridge (Comunicación Cross-Tenant)](#8-eventbridge-comunicación-cross-tenant)
9. [S3 Data Bucket y SQS Batch Import](#9-s3-data-bucket-y-sqs-batch-import)
10. [Usuario Propagate System](#10-crear-usuario-propagate_system)

---

## 1. REGISTRAR DOMINIO

### 1.1 Registrar dominio base en Route 53

1. **AWS Console** → **Route 53** → **Registered domains** → **Register domain**

2. Buscar y registrar: `sybol.id` o el dominio base que uses

3. Completar información de registro

4. **Create hosted zone** para el dominio

**📝 Anotar:**
```
Domain: sybol.id
Hosted Zone ID: Z1234567890ABC
Name servers: ns-xxx.awsdns-xx.com, ...
```

⚠️ **IMPORTANTE:** NO crear records DNS todavía. Los subdominios se configurarán más adelante:
- `backoffice.sybol.id` → Se creará en [sección 7.3 - API Gateway Custom Domains](#73-custom-domains-opcional)
- `api.sybol.id` → Se creará en [sección 7.3 - API Gateway Custom Domains](#73-custom-domains-opcional)
- `{tenant}.staging.wallet.sybol.id` → Se creará en [GUIA_OPERATIVA_MULTI_TENANT.md - sección 1](./GUIA_OPERATIVA_MULTI_TENANT.md#1-preparación-dominio-y-certificado)

✅ **Checkpoint Dominio:**
- [ ] Dominio registrado
- [ ] Hosted zone creada
- [ ] Name servers anotados

---

## 2. COGNITO

### 2.1 Crear User Pool

#### **Paso 1: Configure sign-in experience**

1. **AWS Console** → **Cognito** → **User pools** → **Create user pool**

2. **Configure options** ⚠️ **ESTAS OPCIONES NO SE PUEDEN CAMBIAR DESPUÉS**

   **Options for sign-in identifiers:**
   - ✅ **Email** (usuarios usarán email como username)
   - ❌ Phone number
   - ❌ Username (no permitir usernames custom)

   **Self-registration:**
   - ✅ **Disable self-registration** ⚠️ **IMPORTANTE**
   - Marcar "Enable self-registration"

   **Required attributes for sign-up:**
   - ✅ **email** (ya requerido por ser el sign-in identifier)
   - Dejar el resto sin marcar

3. **Next**

#### **Paso 2: Configure security requirements**

1. **Password policy:**
   - **Mode:** Cognito defaults
   - Minimum length: 8 characters
   - Contains: at least 1 number, 1 special character, 1 uppercase, 1 lowercase

2. **Multi-factor authentication (MFA):**
   - **MFA enforcement:** Optional MFA
   - **MFA methods:** ✅ Authenticator apps

3. **User account recovery:**
   - ✅ **Email only** (enviar código de recuperación por email)

4. **Next**

#### **Paso 3: Configure sign-up experience**

1. **Cognito-assisted verification and confirmation:**
   - **Allow Cognito to automatically send messages to verify and confirm:** ✅ Yes
   - **Attributes to verify:** ✅ Email

2. **Verifying attribute changes:**
   - ✅ Send email message, verify new email address

4. **Required attributes:** (ya configurado en paso 1)
   - ✅ email

5. **Custom attributes:** ⚠️ **CRÍTICO - ESTOS NO SE PUEDEN CAMBIAR DESPUÉS**
   
   Click **Add custom attribute** dos veces:

   **Attribute 1:**
   ```
   Name: tenant_id
   Type: String
   Min length: 3
   Max length: 100
   Mutable: Yes
   SOLO CON PERMISOS DE LECTURA (NO WRITE)
   TIENE QUE SER NO MUTABLE
   ```

   **Attribute 2:**
   ```
   Name: role
   Type: String
   Min length: 4
   Max length: 50
   Mutable: Yes
   SOLO CON PERMISOS DE LECTURA (NO WRITE)
   ```

6. **Next**

#### **Paso 5: Integrate your app**

1. **User pool name:** `sybol-user-pool`

2. **Hosted authentication pages:**
   - ❌ Use the Cognito Hosted UI (no necesario por ahora)

3. **Initial app client:**
   - ✅ **Public client** (para aplicaciones web/móviles)
   - **App client name:** `sybol-app-client`
   - **Client secret:** ❌ Don't generate a client secret
   - **Authentication flows:**
     - ✅ ALLOW_USER_SRP_AUTH
     - ✅ ALLOW_REFRESH_TOKEN_AUTH
     - ❌ ALLOW_USER_PASSWORD_AUTH (menos seguro, no necesario con SRP)

4. **Advanced app client settings (Opcional):**
   - Expandir **Advanced app client settings**
   - **Token expiration:**
     ```
     Refresh token expiration: 30 days (por defecto)
     Access token expiration: 60 minutes (por defecto, puede reducirse a 5-15 min)
     ID token expiration: 60 minutes (por defecto, puede reducirse a 5-15 min)
     ```
   
   💡 **Recomendación:** Para mayor seguridad, reducir access/ID tokens a 15-30 minutos.
   Los refresh tokens permiten obtener nuevos tokens sin re-autenticar.

5. **Next**

#### **Paso 6: Review and create**

1. Revisar toda la configuración

2. **Create user pool**

⏱️ Tarda 1-2 minutos.

**📝 Anotar:**
```
User Pool ID: eu-west-1_XXXXXXXXX
User Pool ARN: arn:aws:cognito-idp:eu-west-1:ACCOUNT_ID:userpool/eu-west-1_XXXXXXXXX
App Client ID: 1234567890abcdefghij
Region: eu-west-1
```

### 2.2 Crear Identity Pool

1. **Cognito** → **Identity pools** → **Create identity pool**

2. **Identity pool name:** `sybol-identity-pool`

3. **Enable access to unauthenticated identities:** ❌ NO

4. **Authentication providers** → **Cognito user pools**
   - **User pool ID:** `eu-west-1_XXXXXXXXX`
   - **App client ID:** `1234567890abcdefghij`

5. **Basic (classic) authentication:** ⚠️ **NO MARCAR**
   - ❌ **NO activar** "Activate basic flow"
   - Usar solo Enhanced (Simplified) Flow por seguridad
   - El flujo clásico delega la selección de roles IAM al cliente (menos seguro)

6. **Create new IAM roles:**
   - **Authenticated role name:** `Cognito_sybol_Auth_Role`
   - **Create**

**📝 Anotar:**
```
Identity Pool ID: eu-west-1:aaaa-bbbb-cccc-dddd-eeee
Auth Role ARN: arn:aws:iam::ACCOUNT_ID:role/Cognito_sybol_Auth_Role
```
---

## 3. RDS POSTGRESQL

⚠️ **IMPORTANTE - BUSINESS RULES DE PERMISOS:**

Antes de configurar RDS, es crítico entender el modelo de permisos que implementaremos:

**Usuarios Core:**
- `sybol_admin`: ÚNICO con escritura en `catalog` y `backofficedev`
- `catalog`: Solo lectura en `catalog`
- `propagate_system`: Acceso a TODAS las `tenant_*` (lectura + escritura)

**Usuarios Tenant (por cada tenant):**
- `{tenant}_admin`: Escritura en su `tenant_*`, lectura en `catalog` y `backofficedev`
- `{tenant}_user`: Lectura en su `tenant_*`, `catalog` y `backofficedev`

**Seguridad:**
- `PUBLIC` NO debe tener acceso (REVOKE obligatorio)
- Permisos solo por GRANT explícito

📚 **Referencia completa:** `v1/services/database/BUSINESS_RULES.md`

---

### 3.1 Crear Cluster RDS

1. **AWS Console** → **RDS** → **Databases** → **Create database**

2. **Engine options:**
   - **Engine:** PostgreSQL
   - **Version:** PostgreSQL 17.4 compatible
   - **Capacity:** Serverless v2 (recomendado)
sybol
3. **Settings:**
   - **Cluster identifier:** `sybol-cluster`
   - **Master username:** `postgres`
   - **Master password:** [GENERAR FUERTE] o DELEGAR A SecretManager

4. **Serverless v2 scaling:**
   - **Minimum:** 0.5 ACUs
   - **Maximum:** 2 ACUs (ajustar según carga) (stagoing db.t4g.small with 100Gb)

5. **Connectivity:**
   - **VPC:** Seleccionar tu VPC (crear si no existe - ver sección 4)
   - **Public access:** ❌ NO
   - **VPC security group:** Create new → `rds-sg`

6. **Additional configuration:**
   - **Initial database:** `postgres`
   - **Backup retention:** 7 días
   - **Encryption:** ✅ Enable (default KMS)
   - **IAM database authentication:** ✅ Enable (IMPORTANTE)

7. **Create database**

⏱️ Tarda 5-10 minutos en estar disponible.

**📝 Anotar:**
```
Cluster Endpoint: sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com
Reader Endpoint: sybol-cluster.cluster-ro-xxxxx.eu-west-1.rds.amazonaws.com
Port: 5432
Master User: postgres
Master Password: [EN SECRETS MANAGER]
Security Groups: internal-sg, rds-sg (ver configuración abajo)
```

### 3.1.1 Configurar Security Groups

⚠️ **Crear los Security Groups ANTES de continuar con las databases:**

#### **A. Security Group Internal (internal-sg)**

1. **EC2 Console** → **Security Groups** → **Create security group**
   - **Name:** `internal-sg`
   - **Description:** Internal access within VPC
   - **VPC:** `sybol-vpc`

2. **Inbound rules:**
   ```
   Type: All traffic
   Source: 10.0.0.0/16 (CIDR de la VPC)
   Description: Allow all traffic from VPC
   ```

3. **Outbound rules:**
   ```
   Type: All traffic
   Destination: 0.0.0.0/0
   Description: Allow all outbound traffic
   ```

4. **Create security group**

**📝 Anotar:**
```
Internal SG: sg-internal123
```

#### **B. Security Group RDS (rds-sg)**

1. **Security Groups** → **Create security group**
   - **Name:** `rds-sg`
   - **Description:** PostgreSQL access for RDS cluster
   - **VPC:** `sybol-vpc`

2. **Inbound rules:**
   
   **Regla 1 - Acceso desde Lambdas:**
   ```
   Type: PostgreSQL
   Port: 5432
   Source: sg-lambda123 (se creará en sección 6)
   Description: Allow Lambda access
   ```
   
   **Regla 2 - Acceso interno:**
   ```
   Type: PostgreSQL
   Port: 5432
   Source: sg-internal123
   Description: Allow internal VPC access
   ```
   
   **Regla 3 - Mantenimiento:**
   ```
   Type: PostgreSQL
   Port: 5432
   Source: [IP_MANTENIMIENTO_1]/32
   Description: Maintenance IP 1
   ```
   
   ⚠️ **Añadir más reglas** para cada IP de mantenimiento necesaria.

3. **Outbound rules:**
   ```
   (Ninguna - dejar vacío)
   ```

4. **Create security group**

**📝 Anotar:**
```
RDS SG: sg-rds123
IPs Mantenimiento: [Lista de IPs configuradas]
```

💡 **Nota:** El `sg-lambda123` se creará en la [sección 6.3 - Lambdas](#63-crear-lambda-functions). Una vez creado, volver aquí y añadir la regla de inbound.

✅ **Checkpoint Security Groups:**
- [ ] internal-sg creado (permite todo dentro de VPC)
- [ ] rds-sg creado (permite PostgreSQL desde internal-sg y IPs mantenimiento)
- [ ] IPs de mantenimiento añadidas a rds-sg
- [ ] Recordatorio: Añadir sg-lambda123 cuando se cree en sección 6

---

### 3.2 Crear Database Backoffice

#### **Conectar al cluster:**

```bash
# Desde instancia EC2 en la VPC o Session Manager
psql -h sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
     -U postgres \
     -p 5432 \
     -d postgres
```

#### **Crear database y usuarios:**

⚠️ **IMPORTANTE:** Según las business rules, `backoffice` es una database CORE que:
- Solo **sybol_admin** tiene permisos de LECTURA + ESCRITURA
- Todos los **{tenant}_admin** y **{tenant}_user** tienen permisos de LECTURA
- **NO** se usa catalog, propagate_system ni otros usuarios core en backoffice

```sql
-- Crear database
CREATE DATABASE backofficedev;

-- Conectar a la nueva database
\c backofficedev

-- PASO 1: REVOCAR acceso público (crítico para seguridad)
-- Por defecto PostgreSQL da CONNECT a PUBLIC, esto debe eliminarse
REVOKE CONNECT ON DATABASE backofficedev FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- PASO 2: Crear usuario sybol_admin (admin del sistema + tenant sybol)
CREATE USER sybol_admin WITH PASSWORD 'PASSWORD_MUY_SEGURA_SYBOL!';

-- PASO 3: Otorgar permisos COMPLETOS a sybol_admin (ÚNICO con escritura)
GRANT CONNECT ON DATABASE backofficedev TO sybol_admin;
GRANT ALL PRIVILEGES ON DATABASE backofficedev TO sybol_admin;
GRANT ALL PRIVILEGES ON SCHEMA public TO sybol_admin;

-- Permisos en tablas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sybol_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sybol_admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO sybol_admin;

-- Permisos en tablas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sybol_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sybol_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO sybol_admin;

-- Verificar usuarios
\du

-- Verificar que PUBLIC no tiene acceso
\l+ backofficedev
```

#### **Ejecutar schemas:**

```sql
-- Ejecutar schema backoffice como sybol_admin
-- (Las tablas se crearán con sybol_admin como owner)
\i /path/to/v1/services/backoffice/database/schema.sql

-- Verificar tablas
\dt

-- Verificar owner de las tablas (debe ser sybol_admin)
\dt+
```

**Tablas esperadas:**
- `did_documents`
- `did_keys`
- `entities`
- `catalog_entries`
- `catalog_claims`
- Otras según el schema

> ⚠️ **Tabla `entities` — crear si no existe en el schema:**
> ```sql
> CREATE TABLE IF NOT EXISTS entities (
>   tenant       TEXT PRIMARY KEY,
>   business_name TEXT,
>   cif          TEXT,
>   created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
>   updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
> );
> -- Permisos para el usuario de escritura:
> GRANT SELECT, INSERT, UPDATE, DELETE ON entities TO sybol_admin;
> -- Permisos de lectura para el usuario backoffice:
> GRANT SELECT ON entities TO backoffice;
> ```

**📝 Anotar:**
```
Database: backofficedev
Owner: postgres
Usuario con escritura: sybol_admin (ÚNICO)
Password sybol_admin: [GUARDAR EN SECRETS MANAGER]
```

💡 **Nota:** Los permisos de LECTURA para {tenant}_admin y {tenant}_user se otorgarán cuando se cree cada tenant. Ver **[GUIA_OPERATIVA_MULTI_TENANT.md - Sección 4.8](#)** para más detalles.

### 3.3 Crear Database Catalog

⚠️ **IMPORTANTE:** Según las business rules, `catalog` es una database CORE que:
- Usuario **catalog** (servicio): SOLO LECTURA
- Usuario **sybol_admin**: LECTURA + ESCRITURA (ÚNICO con escritura)
- Todos los **{tenant}_admin** y **{tenant}_user**: LECTURA (permisos otorgados al crear cada tenant)
- **propagate_system**: SIN acceso

```sql
-- Volver a postgres
\c postgres

-- Crear database
CREATE DATABASE catalog;

-- Conectar
\c catalog

-- PASO 1: REVOCAR acceso público (crítico para seguridad)
REVOKE CONNECT ON DATABASE catalog FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- PASO 2: Crear usuario 'catalog' (servicio de catálogo - solo lectura)
CREATE USER catalog WITH PASSWORD 'PASSWORD_SEGURA_CATALOG_789!';

-- PASO 3: Permisos de LECTURA para usuario 'catalog'
GRANT CONNECT ON DATABASE catalog TO catalog;
GRANT USAGE ON SCHEMA public TO catalog;

-- Permisos en tablas existentes (solo SELECT)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO catalog;

-- Permisos en tablas futuras (solo SELECT)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO catalog;

-- PASO 4: Otorgar permisos COMPLETOS a sybol_admin
-- (Ya creado en sección 3.2, aquí solo damos permisos en catalog)
GRANT CONNECT ON DATABASE catalog TO sybol_admin;
GRANT ALL PRIVILEGES ON DATABASE catalog TO sybol_admin;
GRANT ALL PRIVILEGES ON SCHEMA public TO sybol_admin;

-- Permisos en tablas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sybol_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sybol_admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO sybol_admin;

-- Permisos en tablas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sybol_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sybol_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO sybol_admin;

-- Verificar usuarios
\du

-- Verificar que PUBLIC no tiene acceso
\l+ catalog
```

#### **Ejecutar schema:**

```sql
-- Ejecutar schema como sybol_admin (owner de las tablas)
\i /path/to/v0/catalog/backend/database/schema.sql

-- Verificar tablas creadas
\dt

-- Verificar owner de las tablas (debe ser sybol_admin)
\dt+

-- Verificar permisos del usuario 'catalog'
\z
```

**📝 Anotar:**
```
Database: catalog
Owner: postgres
Usuario servicio catalog: catalog (SOLO LECTURA)
Password catalog: [GUARDAR EN SECRETS MANAGER]
Usuario admin: sybol_admin (LECTURA + ESCRITURA)
Password sybol_admin: [YA GUARDADA EN SECCIÓN 3.2]
```

💡 **Nota:** Los permisos de LECTURA para {tenant}_admin y {tenant}_user se otorgarán cuando se cree cada tenant. Ver **[GUIA_OPERATIVA_MULTI_TENANT.md - Sección 4.8](#)** para más detalles.

✅ **Checkpoint RDS:**
- [ ] Cluster creado y running
- [ ] Database `backofficedev` creada
- [ ] Usuario `sybol_admin` creado con permisos LECTURA+ESCRITURA en backofficedev
- [ ] Database `catalog` creada
- [ ] Usuario `catalog` creado con permisos SOLO LECTURA en catalog
- [ ] Usuario `sybol_admin` tiene permisos LECTURA+ESCRITURA en catalog
- [ ] Schemas ejecutados en ambas databases
- [ ] PUBLIC no tiene acceso (REVOKE ejecutado)
- [ ] IAM database authentication habilitado
- [ ] Passwords en Secrets Manager (hacer después)

---

## 4. VPC Y RED

### Objetivo

Configurar una VPC que permita a las Lambdas acceder a internet mediante Elastic IP. Cuando se configura una Lambda con una subnet pública y un security group, AWS genera automáticamente un ENI (Elastic Network Interface) en la consola EC2. Si varias Lambdas comparten la misma configuración (misma subnet y mismo security group), reutilizarán el mismo ENI, aunque en la descripción del ENI solo aparezca el nombre de la primera Lambda configurada.

### 4.1 Verificar VPC

La cuenta AWS normalmente incluye una VPC predeterminada. Verificar que existe y tiene:

1. **VPC Console** → **Your VPCs** → Buscar VPC existente (ej: `vpc-default` o crear una nueva)

**📝 Anotar:**
```
VPC ID: vpc-0abc123
```

⚠️ **Requisitos de la VPC:**
- Debe tener un **Route Table** configurado
- Debe tener un **Internet Gateway** attached

### 4.2 Verificar Internet Gateway

1. **VPC** → **Internet Gateways** → Verificar que existe un IGW adjunto a la VPC

2. Si no existe, crear uno:
   - **Create internet gateway**
   - **Name:** `sybol-igw`
   - **Actions** → **Attach to VPC** → Seleccionar la VPC

**📝 Anotar:**
```
IGW ID: igw-0xyz789
```

### 4.3 Verificar Route Table

1. **VPC** → **Route Tables** → Buscar el route table de la VPC

2. **Routes** tab → Verificar que existe ruta a internet:
   ```
   Destination: 0.0.0.0/0
   Target: igw-0xyz789
   ```

3. Si no existe, agregar la ruta:
   - **Edit routes** → **Add route**
   - **Destination:** `0.0.0.0/0`
   - **Target:** Internet Gateway (seleccionar el IGW)
   - **Save changes**

### 4.4 Verificar Subnets Privadas

Por defecto, la VPC tendrá **3 subnets privadas** creadas en diferentes zonas de disponibilidad.

1. **VPC** → **Subnets** → Listar subnets de la VPC

**📝 Anotar las subnets privadas existentes:**
```
Private Subnet 1: subnet-xxx (AZ: eu-west-1a)
Private Subnet 2: subnet-yyy (AZ: eu-west-1b)
Private Subnet 3: subnet-zzz (AZ: eu-west-1c)
```

### 4.5 Crear Subnet Pública para Lambdas

Crear una subnet pública específica para las Lambdas:

1. **VPC** → **Subnets** → **Create subnet**

2. **Configuración:**
   ```
   VPC: [Seleccionar la VPC]
   Subnet name: lambda-public-subnet
   Availability Zone: eu-west-1a
   IPv4 CIDR block: 10.0.10.0/24
   ```

3. **Create subnet**

4. **Asociar con Route Table:**
   - **VPC** → **Route Tables** → Seleccionar route table de la VPC
   - **Subnet associations** → **Edit subnet associations**
   - ✅ Marcar `lambda-public-subnet`
   - **Save associations**

**📝 Anotar:**
```
Lambda Public Subnet: subnet-lambda-xxx (10.0.10.0/24, eu-west-1a)
```

### 4.6 Crear Elastic IP

Reservar una Elastic IP que se asignará posteriormente al ENI de las Lambdas:

1. **VPC Console** → **Elastic IPs** → **Allocate Elastic IP address**

2. **Network Border Group:** eu-west-1

3. **Tags:**
   ```
   Key: Name
   Value: lambda-elastic-ip
   ```

4. **Allocate**

**📝 Anotar:**
```
Elastic IP: 108.xxx.xxx.xxx
Allocation ID: eipalloc-0abc123def456
```

⚠️ **IMPORTANTE:** NO asignar todavía la Elastic IP. Se asignará después de configurar las Lambdas.

### 4.7 Asignar Elastic IP al ENI de las Lambdas

⚠️ **Este paso se realiza DESPUÉS de configurar las Lambdas con la VPC** (ver sección 6).

Una vez que las Lambdas estén configuradas con la subnet pública y el security group:

1. **EC2 Console** → **Network Interfaces (ENIs)**

2. **Buscar el ENI de las Lambdas:**
   - Filtrar por subnet: `lambda-public-subnet`
   - El ENI aparecerá con una descripción como: `AWS Lambda VPC ENI-lambdaFunctionName-xxx`
   - Aunque varias Lambdas compartan la configuración, solo verás una descripción con el nombre de la primera Lambda configurada

3. **Copiar el ENI ID:** `eni-0abc123def456`

**📝 Anotar:**
```
Lambda ENI ID: eni-0abc123def456
```

4. **Asignar Elastic IP al ENI:**
   - **VPC Console** → **Elastic IPs**
   - Seleccionar la Elastic IP reservada
   - **Actions** → **Associate Elastic IP address**
   - **Resource type:** Network interface
   - **Network interface:** Pegar el ENI ID (eni-0abc123def456)
   - **Associate**

✅ Las Lambdas ahora tienen acceso a internet a través de la Elastic IP.

### 4.8 Security Groups

#### **A. Security Group para Lambdas:**

⚠️ **IMPORTANTE:** Este Security Group debe tener reglas restrictivas desde el inicio.

1. **Security Groups** → **Create security group**

2. **Basic details:**
   ```
   Security group name: lambda-sg
   Description: Security group for Lambda functions with restricted egress
   VPC: sybol-vpc
   ```

3. **Outbound rules** → **Eliminar regla default "All traffic"**

4. **Add outbound rules** (una por una):

   **Regla 1 - HTTPS para Cognito JWKS:**
   ```
   Type: HTTPS
   Protocol: TCP
   Port range: 443
   Destination: 0.0.0.0/0
   Description: HTTPS for Cognito JWKS endpoint
   ```

   **Regla 2 - PostgreSQL para RDS:**
   ```
   Type: PostgreSQL
   Protocol: TCP
   Port range: 5432
   Destination: Custom → [Seleccionar Security Group de RDS]
   Description: PostgreSQL access to RDS
   ```

   **Regla 3 - DNS UDP:**
   ```
   Type: Custom UDP
   Protocol: UDP
   Port range: 53
   Destination: 0.0.0.0/0
   Description: DNS resolution UDP
   ```

   **Regla 4 - DNS TCP:**
   ```
   Type: Custom TCP
   Protocol: TCP
   Port range: 53
   Destination: 0.0.0.0/0
   Description: DNS resolution TCP
   ```

5. **Inbound rules:** Ninguna (dejar vacío)

6. **Create security group**

**📝 Anotar:**
```
Lambda SG: sg-lambda123
Outbound rules: HTTPS (443), PostgreSQL (5432 → RDS SG), DNS (53 UDP+TCP)
```

#### **B. Configurar Security Group RDS:**

1. **Security Groups** → Buscar el SG de RDS (ej: `rds-sg`)

2. **Inbound rules** → **Edit inbound rules** → **Add rule**
   ```
   Type: PostgreSQL
   Protocol: TCP
   Port range: 5432
   Source: Custom → sg-lambda123
   Description: Allow Lambda access to RDS
   ```

3. **Save rules**

✅ **Checkpoint VPC:**
- [ ] VPC verificada/creada con Route Table e Internet Gateway
- [ ] Internet Gateway attached a la VPC
- [ ] Route table con ruta a internet (0.0.0.0/0 → igw)
- [ ] 3 Subnets privadas identificadas
- [ ] Subnet pública para Lambdas creada (lambda-public-subnet)
- [ ] lambda-public-subnet asociada al Route Table
- [ ] Elastic IP reservada (NO asignada todavía)
- [ ] Security Group lambda-sg creado con reglas restrictivas
- [ ] RDS SG permite acceso desde lambda-sg
- [ ] ENI ID anotado (después de configurar Lambdas)
- [ ] Elastic IP asignada al ENI (después de configurar Lambdas)

---

## 5. IAM POLICIES PARA STS

### 5.1 Policy para Asumir Tenant Roles

Las Lambdas **businessLogic** y **propagate** necesitan asumir roles de tenant.

1. **IAM Console** → **Policies** → **Create policy**

2. **JSON:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAssumeTenantRoles",
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::ACCOUNT_ID:role/TenantRole-ENVIRONMENT-*"
    }
  ]
}
```

⚠️ **Reemplazar `ACCOUNT_ID`** con tu AWS Account ID.
⚠️ **Reemplazar `ENVIRONMENT`** con tu Environment value.
3. **Next**

4. **Policy name:** `ENVIRONMENT-STS-TenantRolePolicy`

5. **Create policy**

**📝 Anotar:**
```
Policy ARN: arn:aws:iam::ACCOUNT_ID:policy/ENVIRONMENT-STS-TenantRolePolicy
```

Esta policy se adjuntará a businessLogic y propagate en la siguiente sección.

---

## 6. LAMBDAS Y ECR

### 6.1 Crear Repositorios ECR

Cada Lambda tiene su repo Docker.

1. **ECR Console** → **Repositories** → **Create**

**Crear 4 repositorios:**

| Nombre | URI |
|--------|-----|
| `sybol/backoffice` | `ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/backoffice` |
| `sybol/businesslogic` | `ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/businesslogic` |
| `sybol/propagate` | `ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/propagate` |
| `sybol/catalog` | `ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/catalog` |

**Configuración por repo:**
- **Visibility:** Private
- **Tag immutability:** Disabled
- **Scan on push:** Enable
- **Encryption:** AES-256

**📝 Anotar los URIs de cada repo.**

### 6.2 Build y Push Imágenes

#### **Autenticarse en ECR:**

```bash
aws ecr get-login-password --region eu-west-1 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com
```

#### **Backoffice:**

```bash
cd v1/services/backoffice

docker build -t sybol/backoffice:latest .

docker tag sybol/backoffice:latest \
  ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/backoffice:latest

docker push ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/backoffice:latest
```

#### **BusinessLogic:**

```bash
cd v1/services/businessLogic

docker build -t sybol/businesslogic:latest .

docker tag sybol/businesslogic:latest \
  ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/businesslogic:latest

docker push ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/businesslogic:latest
```

#### **Propagate:**

```bash
cd v1/services/propagate

docker build -t sybol/propagate:latest .

docker tag sybol/propagate:latest \
  ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/propagate:latest

docker push ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/propagate:latest
```

#### **Catalog:**

```bash
cd v0/catalog/backend

docker build -t sybol/catalog:latest .

docker tag sybol/catalog:latest \
  ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/catalog:latest

docker push ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/catalog:latest
```

### 6.3 Crear Lambda Functions

#### **A. Backoffice Lambda:**

1. **Lambda Console** → **Create function**
   - **Container image**
   - **Function name:** `backoffice`
   - **Container image URI:** `ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/backoffice:latest`
   - **Architecture:** x86_64

2. **Configuration** → **General:**
   - **Memory:** 512 MB
   - **Timeout:** 30 seconds

3. **Environment variables:**
   ```
   DB_HOST=sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com
   DB_PORT=5432
   DB_NAME=backoffice
   DB_USER=backoffice_admin
   DB_PASSWORD=[PASSWORD o mejor Secrets Manager]
   DB_SSL=true
   AWS_REGION=eu-west-1
   NODE_ENV=production
   DID_DOMAIN=did.develop.sybol.id
   ```
   > **`DID_DOMAIN`** define el dominio que se usa para construir los DIDs `did:web` de los tenants.
   > Valores según entorno: `did.develop.sybol.id` / `did.staging.sybol.id` / `did.sybol.id`

4. **VPC:**
  Primero hay que ir a añadir al rol de la lambda el permiso para createnetworkd etc
   Verificar que el execution role tiene `AWSLambdaVPCAccessExecutionRole`
   - **VPC:** `sybol-vpc`
   - **Subnets:** `sybol-public-subnet-1a`, `sybol-public-subnet-1b`
   - **Security groups:** `lambda-sg`


**�� Anotar:**
```
Lambda: backoffice
ARN: arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:backoffice
Execution Role: backoffice-role-xxxxx

---

#### **6.3.1 Configurar Usuarios de Base de Datos para Backoffice**

El servicio backoffice usa un sistema **dual de acceso a base de datos**:

##### **A. Usuario de Lectura (Variables de Entorno)**

Este usuario se usa para operaciones generales desde las variables de entorno de la Lambda.

**Permisos:**
- ✅ **SELECT** en todas las tablas (`did_documents`, `kyb_verifications`)
- ✅ **INSERT, UPDATE, DELETE** en `kyb_verifications`
- ❌ **NO ESCRITURA** en `did_documents`

**Ejecutar script SQL:**

```bash
# Conectarse a RDS
psql -h sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
     -U postgres \
     -d backoffice

# Ejecutar script de configuración
\i v1/services/backoffice/database/setup_readonly_user.sql
```

El script creará:
- Usuario: `backoffice`
- Password: Cambiar en el script antes de ejecutar

**📝 Actualizar variables de entorno de Lambda backoffice:**
```
SYBOL_DB_USER=backoffice
SYBOL_DB_PASSWORD=[PASSWORD del script]
```

##### **B. Usuario de Escritura para Tenant Sybol (Secrets Manager)**

⚠️ **SOLO PARA EL TENANT `sybol`** - Este usuario permite escritura en `did_documents` mediante autenticación multi-tenant.

**Permisos:**
- ✅ **SELECT, INSERT, UPDATE, DELETE** en `did_documents`
- ✅ **SELECT** en `kyb_verifications` (y otras tablas)
- ❌ **NO ESCRITURA** en `kyb_verifications`

**Paso 1: Ejecutar script SQL:**

```bash
# Conectarse a RDS
psql -h sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
     -U postgres \
     -d backoffice

# Ejecutar script de configuración del tenant sybol
\i v1/services/backoffice/database/setup_sybol_tenant_user.sql
```

El script creará:
- Usuario: `sybol_tenant_writer`
- Password: Cambiar en el script antes de ejecutar

**Paso 2: Crear Secret en AWS Secrets Manager:**

Ver [GUIA_OPERATIVA_MULTI_TENANT.md - Tenant Sybol Especial](#tenant-sybol-acceso-backoffice) para configurar el secret `tenant/sybol/admin-password`.

**Paso 3: Configurar IAM Role del Tenant Sybol:**

Ver [GUIA_OPERATIVA_MULTI_TENANT.md - Tenant Sybol Especial](#tenant-sybol-acceso-backoffice) para adjuntar políticas de Secrets Manager.

**📋 Resumen de Accesos:**

| Usuario | Ubicación | did_documents | kyb_verifications | Uso |
|---------|-----------|---------------|-------------------|-----|
| `backoffice` | Env Vars | ✅ SELECT | ✅ ALL (INSERT/UPDATE/DELETE/SELECT) | General |
| `sybol_tenant_writer` | Secrets Manager | ✅ ALL (INSERT/UPDATE/DELETE/SELECT) | ✅ SELECT | Solo tenant sybol |

**🔐 Flujo de Autenticación Multi-Tenant:**

1. Request con `x-id-token` del tenant `sybol`
2. `authMiddleware` valida token y extrae `tenantId=sybol`
3. `getTenantStsSession()` hace `AssumeRole` a `TenantRole-sybol-admin`
4. `tenantDatabase.getConnection()` obtiene credentials desde `tenant/sybol/admin-password`
5. Conecta usando `sybol_tenant_writer` con permisos de escritura en `did_documents`

**📖 Documentación completa:**
- [AUTH_CONFIG.md](./services/backoffice/AUTH_CONFIG.md) - Guía de autenticación multi-tenant
- [Backoffice_API.postman_collection.json](./services/backoffice/Backoffice_API.postman_collection.json) - Colección Postman

✅ **Checkpoint Usuarios Backoffice:**
- [ ] Usuario `backoffice` creado y configurado en Lambda
- [ ] Permisos de lectura/escritura verificados
- [ ] Usuario `sybol_tenant_writer` creado (para tenant sybol)
- [ ] Secret `tenant/sybol/admin-password` creado (ver GUIA_OPERATIVA)
- [ ] IAM Role `TenantRole-sybol-admin` con acceso al secret

---

---

#### **6.3.1 Configurar Usuarios de Base de Datos para Backoffice**

El servicio backoffice usa un sistema **dual de acceso a base de datos**:

##### **A. Usuario de Lectura (Variables de Entorno)**

Este usuario se usa para operaciones generales desde las variables de entorno de la Lambda.

**Permisos:**
- ✅ **SELECT** en todas las tablas (`did_documents`, `kyb_verifications`)
- ✅ **INSERT, UPDATE, DELETE** en `kyb_verifications`
- ❌ **NO ESCRITURA** en `did_documents`

**Ejecutar script SQL:**

```bash
# Conectarse a RDS
psql -h sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
     -U postgres \
     -d backoffice

# Ejecutar script de configuración
\i v1/services/backoffice/database/setup_readonly_user.sql
```

El script creará:
- Usuario: `backoffice`
- Password: Cambiar en el script antes de ejecutar

**📝 Actualizar variables de entorno de Lambda backoffice:**
```
SYBOL_DB_USER=backoffice
SYBOL_DB_PASSWORD=[PASSWORD del script]
```

##### **B. Usuario de Escritura para Tenant Sybol (Secrets Manager)**

⚠️ **SOLO PARA EL TENANT `sybol`** - Este usuario permite escritura en `did_documents` mediante autenticación multi-tenant.

**Permisos:**
- ✅ **SELECT, INSERT, UPDATE, DELETE** en `did_documents`
- ✅ **SELECT** en `kyb_verifications` (y otras tablas)
- ❌ **NO ESCRITURA** en `kyb_verifications`

**Paso 1: Ejecutar script SQL:**

```bash
# Conectarse a RDS
psql -h sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
     -U postgres \
     -d backoffice

# Ejecutar script de configuración del tenant sybol
\i v1/services/backoffice/database/setup_sybol_tenant_user.sql
```

El script creará:
- Usuario: `sybol_tenant_writer`
- Password: Cambiar en el script antes de ejecutar

**Paso 2: Crear Secret en AWS Secrets Manager:**

Ver [GUIA_OPERATIVA_MULTI_TENANT.md - Tenant Sybol Especial](#tenant-sybol-acceso-backoffice) para configurar el secret `tenant/sybol/admin-password`.

**Paso 3: Configurar IAM Role del Tenant Sybol:**

Ver [GUIA_OPERATIVA_MULTI_TENANT.md - Tenant Sybol Especial](#tenant-sybol-acceso-backoffice) para adjuntar políticas de Secrets Manager.

**📋 Resumen de Accesos:**

| Usuario | Ubicación | did_documents | kyb_verifications | Uso |
|---------|-----------|---------------|-------------------|-----|
| `backoffice` | Env Vars | ✅ SELECT | ✅ ALL (INSERT/UPDATE/DELETE/SELECT) | General |
| `sybol_tenant_writer` | Secrets Manager | ✅ ALL (INSERT/UPDATE/DELETE/SELECT) | ✅ SELECT | Solo tenant sybol |

**🔐 Flujo de Autenticación Multi-Tenant:**

1. Request con `x-id-token` del tenant `sybol`
2. `authMiddleware` valida token y extrae `tenantId=sybol`
3. `getTenantStsSession()` hace `AssumeRole` a `TenantRole-sybol-admin`
4. `tenantDatabase.getConnection()` obtiene credentials desde `tenant/sybol/admin-password`
5. Conecta usando `sybol_tenant_writer` con permisos de escritura en `did_documents`

**📖 Documentación completa:**
- [AUTH_CONFIG.md](./services/backoffice/AUTH_CONFIG.md) - Guía de autenticación multi-tenant
- [Backoffice_API.postman_collection.json](./services/backoffice/Backoffice_API.postman_collection.json) - Colección Postman

✅ **Checkpoint Usuarios Backoffice:**
- [ ] Usuario `backoffice` creado y configurado en Lambda
- [ ] Permisos de lectura/escritura verificados
- [ ] Usuario `sybol_tenant_writer` creado (para tenant sybol)
- [ ] Secret `tenant/sybol/admin-password` creado (ver GUIA_OPERATIVA)
- [ ] IAM Role `TenantRole-sybol-admin` con acceso al secret

---
```

#### **B. BusinessLogic Lambda:**

Mismo proceso:

**Environment variables:**
```
COGNITO_CLIENT_ID=1p3g6hndtpogl1989r76eoapg4
COGNITO_USER_POOL_ID=eu-west-1_Lpg65AWPJ
```

**Permissions adicionales:**
1. Click en execution role → IAM
2. **Add permissions** → **Attach policies**
3. Buscar y adjuntar: `LambdaAssumeTenantRolesPolicy`

**📝 Anotar:**
```
Lambda: businesslogic
ARN: arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:businesslogic
Execution Role: businesslogic-role-xxxxx
```

#### **C. Propagate Lambda:**

**Environment variables:**
```
AWS_REGION=eu-west-1
AWS_ACCOUNT_ID=ACCOUNT_ID
COGNITO_USER_POOL_ID=eu-west-1_XXXXXXXXX
COGNITO_CLIENT_ID=1234567890abcdefghij
TENANT_ROLE_PREFIX=TenantRole-
RDS_HOST=sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com
RDS_PORT=5432
RDS_USER=propagate_system
RDS_PASSWORD=[PASSWORD]
BACKOFFICE_SERVICE_URL=https://backoffice.sybol.id
API_TIMEOUT=10000
NODE_ENV=production
```

**Permissions:** Adjuntar `LambdaAssumeTenantRolesPolicy`

**📝 Anotar:**
```
Lambda: propagate
ARN: arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:propagate
Execution Role: propagate-role-xxxxx
```

#### **D. Catalog Lambda:**

**Environment variables:**
```
DB_HOST=sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=catalog
DB_USER=catalog_admin
DB_PASSWORD=[PASSWORD]
DB_SSL=true
AWS_REGION=eu-west-1
NODE_ENV=production
```

**📝 Anotar:**
```
Lambda: catalog
ARN: arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:catalog
Execution Role: catalog-role-xxxxx
```

### 6.4 Configurar CloudWatch Logs Retention

Para cada Lambda:

1. **CloudWatch** → **Log groups**

2. Buscar: `/aws/lambda/backoffice`, `/aws/lambda/businesslogic`, etc.

3. **Actions** → **Edit retention setting**

4. **Retention:** 7 days (o según política)

5. **Save**

### 6.5 Anotar Execution Role ARNs

⚠️ **IMPORTANTE para Trust Policies de tenant roles:**

```
arn:aws:iam::ACCOUNT_ID:role/service-role/businesslogic-role-xxxxx
arn:aws:iam::ACCOUNT_ID:role/service-role/propagate-role-xxxxx
arn:aws:iam::ACCOUNT_ID:role/Cognito_sybol_Auth_Role
```

✅ **Checkpoint Lambdas:**
- [ ] 4 repos ECR creados
- [ ] 4 imágenes pusheadas
- [ ] 4 Lambdas creadas
- [ ] Environment variables configuradas
- [ ] Lambdas en VPC
- [ ] businessLogic y propagate tienen STS policy
- [ ] Log retention configurado

### 6.6 Crear Lambda Rotation Function para Secrets

⚠️ **IMPORTANTE:** Esta función permite rotación automática de passwords en Secrets Manager.

1. **Secrets Manager Console** → **Secrets** → Cualquier secret → **Rotation configuration**

2. **Edit rotation**

3. **Enable automatic rotation** → **Create a new Lambda function**

4. **Configuración:**
   ```
   Function name: SecretsManagerRDSPostgreSQLRotation
   VPC: sybol-vpc
   Subnets: sybol-public-subnet-1a, sybol-public-subnet-1b
   Security groups: lambda-sg
   ```

5. **Create**

⏱️ Tarda 2-3 minutos. AWS crea automáticamente la función con el código necesario.

**📝 Anotar:**
```
Rotation Function: SecretsManagerRDSPostgreSQLRotation
Function ARN: arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:SecretsManagerRDSPostgreSQLRotation
```

💡 **Nota:** Esta función se usará en [GUIA_OPERATIVA_MULTI_TENANT.md - sección 5](./GUIA_OPERATIVA_MULTI_TENANT.md#5-secrets-manager) para rotar passwords de tenants.

✅ **Checkpoint Rotation:**
- [ ] Lambda rotation function creada
- [ ] Función en VPC correcta
- [ ] Permisos de Secrets Manager configurados automáticamente

---

## 7. API GATEWAY

### 7.1 Crear HTTP API - Backoffice

1. **API Gateway** → **Create API** → **HTTP API** → **Build**

2. **Add integration:**
   - **Lambda:** `backoffice`
   - **Name:** `backoffice-integration`

3. **Configure routes:**
   - **Method:** ANY
   - **Path:** `/{proxy+}`
   - **Integration:** `backoffice-integration`

4. **Stage:** `$default` (auto-deploy)

5. **Create**

**📝 Anotar:**
```
API ID: abc123
Invoke URL: https://abc123.execute-api.eu-west-1.amazonaws.com
```

### 7.2 HTTP API para BusinessLogic, Propagate, Catalog

1. **Create API** → **HTTP API**

2. **API name:** `sybol-api`

3. **Add integrations:**
   - Lambda: `businesslogic` → `businesslogic-integration`
   - Lambda: `propagate` → `propagate-integration`
   - Lambda: `catalog` → `catalog-integration`

4. **Configure routes:**
   ```
   ANY /api/bl/{proxy+}      → businesslogic-integration
   ANY /api/ps/{proxy+}      → propagate-integration
   ANY /api/catalog/{proxy+} → catalog-integration
   ```

5. **Create**

**📝 Anotar:**
```
API ID: xyz789
Invoke URL: https://xyz789.execute-api.eu-west-1.amazonaws.com
```

#### ⚠️ **IMPORTANTE: Configurar CORS**

Para permitir llamadas desde el frontend (browsers):

1. **APIs** → `sybol-api` → **CORS**

2. **Configure:**
   ```
   Access-Control-Allow-Origin: * 
   (o específico: https://tenant.staging.wallet.sybol.id)
   
   Access-Control-Allow-Headers: 
   Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token
   
   Access-Control-Allow-Methods: 
   GET,POST,PUT,DELETE,OPTIONS
   
   Access-Control-Max-Age: 
   86400
   ```

3. **Save**

4. **Repetir** para `backoffice-api`

💡 **Recomendación producción:** Usar origins específicos en lugar de `*`:
```
https://repsol.staging.wallet.sybol.id,https://endesa.staging.wallet.sybol.id
```

### 7.3 Crear Authorizer con Cognito

#### **Para backoffice-api:**

1. **APIs** → `backoffice-api` → **Authorization** → **Create**

2. **Authorizer type:** JWT

3. **Name:** `cognito-authorizer`

4. **Identity source:** `$request.header.Authorization`

5. **Issuer URL:** `https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_XXXXXXXXX`

6. **Audience:** `1234567890abcdefghij` (App Client ID)

7. **Create**

8. **Routes** → `ANY /{proxy+}` → **Attach authorization**
   - **Authorization:** `cognito-authorizer`
   - **Save**

#### **Para sybol-api:**

Repetir mismo proceso para cada ruta de `sybol-api`.

### 7.4 Configurar Custom Domains

⚠️ **IMPORTANTE:** Los custom domains permiten usar URLs amigables en lugar de las URLs generadas por API Gateway.

#### **7.4.1 Solicitar Certificado ACM**

1. **AWS Certificate Manager** (región **eu-west-1**) → **Request certificate**

2. **Request public certificate**

3. **Domain names:**
   ```
   backoffice.sybol.id
   api.sybol.id
   ```
   
   O usar wildcard: `*.sybol.id`

4. **Validation method:** DNS validation

5. **Request**

6. **Create records in Route 53:**
   - Click en el certificado
   - **Create records in Route 53** (botón)
   - Validación automática

⏱️ Tarda 5-10 minutos en validar.

**📝 Anotar:**
```
Certificate ARN: arn:aws:acm:eu-west-1:ACCOUNT_ID:certificate/xxxxx
Domains: backoffice.sybol.id, api.sybol.id
Status: Issued
```

#### **7.4.2 Crear Custom Domain - backoffice.sybol.id**

1. **API Gateway** → **Custom domain names** → **Create**

2. **Configuración:**
   ```
   Domain name: backoffice.sybol.id
   ACM certificate: Seleccionar certificado creado en 7.4.1
   Endpoint type: Regional
   ```

3. **Create domain name**

⏱️ Tarda 30-40 minutos en estar disponible.

**📝 Anotar el API Gateway domain name:**
```
API Gateway domain: d-abc123xyz.execute-api.eu-west-1.amazonaws.com
```

4. **API mappings** → **Configure API mappings** → **Add new mapping**
   ```
   API: backoffice-api
   Stage: $default
   Path: (vacío)
   ```

5. **Save**

#### **7.4.3 Crear Custom Domain - api.sybol.id**

Repetir paso 7.4.2 pero con:
- **Domain name:** `api.sybol.id`
- **API mapping:** `sybol-api` (Stage: `$default`)

**📝 Anotar el API Gateway domain name:**
```
API Gateway domain: d-xyz789abc.execute-api.eu-west-1.amazonaws.com
```

#### **7.4.4 Configurar Route 53**

1. **Route 53** → **Hosted zones** → `sybol.id`

2. **Create record - backoffice.sybol.id:**
   ```
   Record name: backoffice
   Record type: A
   Alias: Yes
   Route traffic to: Alias to API Gateway API
   Region: eu-west-1
   API Gateway endpoint: d-abc123xyz.execute-api.eu-west-1.amazonaws.com
   ```

3. **Create record**

4. **Create record - api.sybol.id:**
   ```
   Record name: api
   Record type: A
   Alias: Yes
   Route traffic to: Alias to API Gateway API
   Region: eu-west-1
   API Gateway endpoint: d-xyz789abc.execute-api.eu-west-1.amazonaws.com
   ```

5. **Create record**

#### **7.4.5 Verificar Custom Domains**

Esperar 2-3 minutos y probar:

```bash
# Test backoffice
curl https://backoffice.sybol.id/health
# Esperado: {"status":"ok"}

# Test API
curl https://api.sybol.id/health
# Esperado: {"status":"ok"}
```

**📝 Anotar:**
```
Backoffice URL: https://backoffice.sybol.id
API URL: https://api.sybol.id
```

✅ **Checkpoint API Gateway:**
- [ ] HTTP API backoffice-api creada
- [ ] HTTP API sybol-api creada
- [ ] Rutas configuradas
- [ ] Integrations funcionando
- [ ] CORS configurado
- [ ] Authorizer Cognito aplicado
- [ ] Certificado ACM emitido para dominios
- [ ] Custom domains configurados
- [ ] API mappings configurados
- [ ] Route 53 records creados (A Alias)
- [ ] Dominios accesibles vía HTTPS

### 7.5 Ruta interna M2M — `POST /api/ps/send/internal`

Esta ruta permite que la Lambda **businessLogic** llame al servicio **propagate** de forma machine-to-machine sin un token Cognito, usando autenticación IAM (SigV4).

#### Crear la ruta en API Gateway

En la misma HTTP API que expone el servicio Propagate (`xyz789.execute-api...`), añadir:

```
Method:      POST
Route:       /api/ps/send/internal
Integration: Lambda (propagate-dev)
Authorizer:  AWS_IAM   ← NO usar el Cognito authorizer aquí
```

> ⚠️ El authorizer de Cognito **no** se aplica a esta ruta. La firma SigV4 es verificada
> directamente por API Gateway antes de invocar la Lambda.

#### Inline policy en el execution role de businessLogic

Añadir la siguiente inline policy al rol IAM de la Lambda businessLogic
(ej. `businesslogic-dev-role` o el nombre que tenga en tu cuenta):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPropagateInternalM2M",
      "Effect": "Allow",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:eu-west-1:ACCOUNT_ID:API_ID/*/POST/api/ps/send/internal"
    }
  ]
}
```

Reemplazar `ACCOUNT_ID` y `API_ID` con los valores reales de la cuenta y del API Gateway
que expone el servicio Propagate.

**Aplicar con AWS CLI:**

```bash
aws iam put-role-policy \
  --role-name businesslogic-dev-role \
  --policy-name PropagateSendInternalInvoke \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "AllowPropagateInternalM2M",
      "Effect": "Allow",
      "Action": "execute-api:Invoke",
      "Resource": "arn:aws:execute-api:eu-west-1:ACCOUNT_ID:API_ID/*/POST/api/ps/send/internal"
    }]
  }' \
  --region eu-west-1
```

#### Checklist

- [ ] Ruta `POST /api/ps/send/internal` creada en API GW con authorizer `AWS_IAM`
- [ ] Inline policy `PropagateSendInternalInvoke` aplicada al execution role de businessLogic
- [ ] Lambda businessLogic desplegada con `sigV4HttpClient.js` y `@smithy/signature-v4`
- [ ] Lambda propagate desplegada con middleware `requireIamAuth` y ruta `/send/internal`

---

### 7.5 Dominio DID (did:web) y Endpoint Público

La plataforma implementa el método `did:web` (W3C-CCG) para los identificadores descentralizados de los tenants. Esto requiere:

1. Un subdominio dedicado (`did.{env}.sybol.id`) que resuelva al API Gateway del backoffice
2. Una ruta pública (sin Cognito) para servir los documentos DID en formato W3C
3. CORS con `Access-Control-Allow-Origin: *` en esa ruta (requerido por la spec)

#### **7.5.1 Solicitar Certificado ACM para did.{env}.sybol.id**

Si no usas wildcard `*.sybol.id`, solicitar certificado adicional:

1. **ACM** → **Request certificate** → **Public**
2. **Domain:** `did.develop.sybol.id` (y/o `did.staging.sybol.id`, `did.sybol.id`)
3. **Validation:** DNS
4. Añadir los CNAME records de validación en Route 53

#### **7.5.2 Crear Custom Domain - did.{env}.sybol.id**

1. **API Gateway** → **Custom domain names** → **Create**
2. **Domain name:** `did.develop.sybol.id`
3. **TLS certificate:** Seleccionar el certificado ACM del paso anterior
4. **Create**

5. **API mappings** → **Configure API mappings**
   - **API:** `backoffice-api`
   - **Stage:** `$default`
   - **Path:** *(vacío — raíz)*
   - **Save**

#### **7.5.3 Crear CNAME en Route 53**

```
Nombre:  did.develop.sybol.id
Tipo:    CNAME  (o A Alias si API GW lo soporta)
Valor:   <API Gateway Domain Name del custom domain anterior>
TTL:     300
```

> 💡 También puedes crear un CNAME simple apuntando al mismo dominio regional del API GW del backoffice: `did.develop.sybol.id → api.develop.wallet.sybol.id`

#### **7.5.4 Añadir ruta pública al API Gateway del Backoffice**

El endpoint de resolución DID debe ser accesible **sin autenticación**:

1. **API Gateway** → `backoffice-api` → **Routes**
2. **Create** → Method: `GET` / Path: `/tenants/{tenantId}/did.json`
3. **Integration:** `backoffice-integration` (Lambda backoffice)
4. ⚠️ **NO añadir el Cognito Authorizer** a esta ruta
5. La ruta `ANY /{proxy+}` SIGUE teniendo el authorizer para el resto de endpoints

**Orden de routing en API GW:**
```
GET  /tenants/{tenantId}/did.json  → backoffice (sin auth) ← NUEVA RUTA
ANY  /{proxy+}                     → backoffice (con auth)  ← ruta existente
```

> Los resolvers externos (herramientas W3C, otros wallets) necesitarán acceder a este endpoint libremente.

#### **7.5.5 Configurar CORS para el endpoint público DID**

La especificación `did:web` exige que el documento DID sea accesible desde cualquier origen (browsers, resolvers externos). El endpoint público **debe** devolver:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

**Opción A — CORS en API Gateway (recomendado para la ruta pública):**

1. **API Gateway** → `backoffice-api` → **CORS**
2. En **Access-Control-Allow-Origin** añadir `*` (ya está configurado en 7.2, verificar que aplica a todas las rutas)

**Opción B — CORS en el código del backoffice (ya implementado):**

El handler `getPublicDidDocument` en `did-document.controller.js` ya envía las cabeceras CORS explícitamente:
```javascript
res.setHeader('Access-Control-Allow-Origin', '*');
res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
```
Esta cabecera se envía independientemente de API Gateway.

> ⚠️ **Sólo el endpoint público `/tenants/:tenantId/did.json` usa `*`.** El resto de endpoints del backoffice usan origins restringidos (Opción B en 7.2).

#### **Verificación del endpoint DID**

```bash
# Resolución pública (sin auth)
curl https://did.develop.sybol.id/tenants/sybol/did.json

# Respuesta esperada:
# {
#   "@context": ["https://www.w3.org/ns/did/v1", ...],
#   "id": "did:web:did.develop.sybol.id:tenants:sybol",
#   "verificationMethod": [...],
#   "authentication": [...],
#   "service": [{"type": "EntityProfileService", ...}]
# }

# Verificar cabecera CORS
curl -I https://did.develop.sybol.id/tenants/sybol/did.json | grep -i "access-control"
# Esperado: access-control-allow-origin: *
```

✅ **Checkpoint DID Domain:**
- [ ] Certificado ACM para `did.{env}.sybol.id` emitido
- [ ] Custom domain `did.{env}.sybol.id` creado en API GW
- [ ] CNAME Route 53 apuntando al API GW
- [ ] Ruta `GET /tenants/{tenantId}/did.json` SIN authorizer
- [ ] CORS `*` en endpoint público
- [ ] Variable `DID_DOMAIN=did.develop.sybol.id` en Lambda backoffice
- [ ] Resolución pública funciona: `curl https://did.develop.sybol.id/tenants/sybol/did.json`

---

## 8. EVENTBRIDGE (Comunicación Cross-Tenant)

⚠️ **UNA SOLA VEZ** - Infraestructura compartida para comunicación asíncrona entre tenants.

### 8.1 Arquitectura

```
Tenant A (businessLogic) → EventBridge Bus → EventBridge Rule → Lambda (propagate) → Tenant B DB
```

**Beneficios:**
- Comunicación asíncrona entre tenants
- Retry automático (3 intentos)
- Dead Letter Queue para eventos fallidos
- Sin polling, event-driven
- $1 por millón de eventos

---

### 8.2 Crear Dead Letter Queue (SQS)

1. **AWS Console** → **SQS** → **Create queue**

2. **Configuración:**
   ```
   Name: cross-tenant-dlq
   Type: Standard
   Visibility timeout: 30 seconds
   Message retention period: 14 days
   Receive message wait time: 20 seconds (long polling)
   Maximum message size: 256 KB
   Delivery delay: 0 seconds
   ```

3. **Encryption:** Enable SQS managed encryption (SSE-SQS)

4. **Access policy:** Default

5. **Create queue**

6. **📝 Anotar el ARN:**
   ```
   ARN: arn:aws:sqs:eu-west-1:ACCOUNT_ID:cross-tenant-dlq
   ```

---

### 8.3 Crear IAM Role - PropagateSystemRole

#### 8.3.1 Crear Role Base

1. **IAM Console** → **Roles** → **Create role**

2. **Trusted entity type:** AWS service

3. **Use case:** Lambda

4. **Next**

#### 8.3.2 Adjuntar Política AWS Managed

1. Buscar: `AWSLambdaVPCAccessExecutionRole`

2. ☑️ Seleccionar

3. **Next**

#### 8.3.3 Configurar Role

```
Role name: PropagateSystemRole
Description: Execution role for cross-tenant Lambda processor with RDS IAM auth
```

4. **Create role**

#### 8.3.4 Crear Política Inline Personalizada

1. En lista de Roles → Buscar **PropagateSystemRole**

2. **Click** en el role → **Permissions** tab

3. **Add permissions** → **Create inline policy**

4. **JSON** tab → Pegar:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowRDSIAMAuth",
      "Effect": "Allow",
      "Action": ["rds-db:connect"],
      "Resource": "arn:aws:rds-db:eu-west-1:ACCOUNT_ID:dbuser:*/propagate_system"
    },
    {
      "Sid": "AllowSecretsManagerRead",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:eu-west-1:ACCOUNT_ID:secret:rds/*"
    },
    {
      "Sid": "AllowBackofficeAPIInvoke",
      "Effect": "Allow",
      "Action": ["execute-api:Invoke"],
      "Resource": "arn:aws:execute-api:eu-west-1:ACCOUNT_ID:*/*/GET/api/did-document/*"
    }
  ]
}
```

5. **Reemplazar** `ACCOUNT_ID` con tu AWS Account ID

6. **Policy name:** `RDSCrossTenantAccess`

7. **Create policy**

**📝 Anotar:**
```
Role ARN: arn:aws:iam::ACCOUNT_ID:role/PropagateSystemRole
```

---

### 8.4 Crear EventBridge Custom Event Bus

1. **AWS Console** → **EventBridge** → **Event buses** → **Create event bus**

2. **Configuración:**
   ```
   Name: cross-tenant-event-bus
   Event archive: Disabled (opcional: habilitar para debugging)
   Schema discovery: Disabled
   Resource-based policy: None
   ```

3. **Create**

**📝 Anotar:**
```
Event Bus Name: cross-tenant-event-bus
ARN: arn:aws:events:eu-west-1:ACCOUNT_ID:event-bus/cross-tenant-event-bus
```

---

### 8.5 Crear EventBridge Rule

1. **EventBridge** → **Rules** → **Create rule**

#### Step 1: Define rule detail

```
Name: contact-events-rule
Description: Routes cross-tenant contact events to Lambda processor
Event bus: cross-tenant-event-bus
Rule type: Rule with an event pattern
```

2. **Next**

#### Step 2: Build event pattern

1. **Event source:** Other

2. **Creation method:** Custom pattern (JSON editor)

3. **Event pattern:**
```json
{
  "source": ["sybol.contacts"],
  "detail-type": [
    "ContactRequest",
    "ContactAccepted",
    "ContactRejected",
    "ContactBlocked"
  ]
}
```

4. **Next**

#### Step 3: Select target(s)

⚠️ **NOTA:** Lambda se creará en siguiente paso. Por ahora:

1. **Target types:** AWS service

2. **Select a target:** Lambda function

3. **Function:** `cross-tenant-processor` (se seleccionará después de crear la Lambda)

4. **Retry policy:**
   - Maximum age of event: 1 hour
   - Retry attempts: 3

5. **Dead-letter queue:** Enabled
   - **Select existing SQS queue:** cross-tenant-dlq

6. **Next**

#### Step 4: Configure tags (opcional)

Dejar vacío o añadir tags según convención.

7. **Next**

#### Step 5: Review and create

8. **Create rule**

⚠️ **La rule quedará sin target hasta crear la Lambda en siguiente paso.**

---

### 8.6 Crear Lambda Function (Placeholder)

⚠️ **NOTA:** Esta Lambda será desplegada posteriormente por el servicio propagate. Aquí creamos solo el placeholder para conectar EventBridge.

#### 8.6.1 Crear Función

1. **AWS Console** → **Lambda** → **Create function**

2. **Configuración:**
   ```
   Option: Author from scratch
   Function name: cross-tenant-processor
   Runtime: Node.js 18.x
   Architecture: x86_64
   Execution role: Use an existing role
   Existing role: PropagateSystemRole
   ```

3. **Create function**

#### 8.6.2 Configurar Settings

1. **Configuration** → **General configuration** → **Edit**
   ```
   Memory: 512 MB
   Timeout: 30 seconds
   Ephemeral storage: 512 MB
   ```

2. **Save**

#### 8.6.3 Configurar VPC

1. **Configuration** → **VPC** → **Edit**

2. **VPC:** Seleccionar la VPC donde está RDS

3. **Subnets:** Seleccionar 2-3 private subnets (mismas que RDS usa)

4. **Security groups:** Seleccionar el security group que permite conexión a RDS (puerto 5432)

5. **Save**

⏱️ Tardará 1-2 minutos en aplicar configuración VPC.

#### 8.6.4 Configurar Variables de Entorno

1. **Configuration** → **Environment variables** → **Edit**

2. **Agregar:**

| Key | Value | Descripción |
|-----|-------|-------------|
| `RDS_HOST` | `sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com` | Endpoint RDS |
| `RDS_PORT` | `5432` | Puerto PostgreSQL |
| `RDS_USER` | `propagate_system` | Usuario IAM |
| `BACKOFFICE_API_URL` | `https://backoffice.sybol.id` | URL backoffice API |
| `NODE_ENV` | `production` | Entorno |

3. **Save**

#### 8.6.5 Código Placeholder

1. **Code** tab

2. En `index.mjs`:

```javascript
export const handler = async (event) => {
  console.log('EventBridge event received:', JSON.stringify(event, null, 2));
  
  // Este código será reemplazado por el deployment del servicio propagate
  return {
    statusCode: 200,
    body: JSON.stringify({ 
      message: 'Event received (placeholder)' 
    })
  };
};
```

3. **Deploy**

---

### 8.7 Configurar Resource Policy en Lambda

Permitir que EventBridge invoque la Lambda:

1. **Lambda** → **cross-tenant-processor** → **Configuration** → **Permissions**

2. **Resource-based policy statements** → **Add permissions**

3. **Configuración:**
   ```
   Statement ID: AllowEventBridgeInvoke
   Principal: events.amazonaws.com
   Source ARN: arn:aws:events:eu-west-1:ACCOUNT_ID:rule/cross-tenant-event-bus/*
   Action: lambda:InvokeFunction
   ```

4. **Reemplazar** `ACCOUNT_ID`

5. **Save**

---

### 8.8 Actualizar EventBridge Rule con Target Lambda

1. **EventBridge** → **Rules** → **contact-events-rule**

2. **Targets** tab → **Edit**

3. **Function:** Seleccionar `cross-tenant-processor`

4. **Save**

---

### 8.9 Crear CloudWatch Alarm para DLQ

1. **CloudWatch** → **Alarms** → **Create alarm**

2. **Select metric:**
   - **Service:** SQS
   - **Metric name:** ApproximateNumberOfMessagesVisible
   - **Queue name:** cross-tenant-dlq

3. **Select metric**

4. **Specify metric and conditions:**
   ```
   Statistic: Average
   Period: 5 minutes
   Threshold type: Static
   Whenever ApproximateNumberOfMessagesVisible is: Greater/Equal
   than: 1
   ```

5. **Next**

6. **Configure actions:**
   - **Alarm state trigger:** In alarm
   - **Select an SNS topic:** Create new topic
     ```
     Topic name: cross-tenant-alerts
     Email endpoints: tu-email@empresa.com
     ```

7. **Create topic**

8. **Next**

9. **Add name and description:**
   ```
   Alarm name: cross-tenant-dlq-messages-alarm
   Alarm description: Alert when failed events appear in DLQ
   ```

10. **Next**

11. **Create alarm**

⚠️ **IMPORTANTE:** Verificar email y confirmar suscripción a SNS.

---

✅ **Checkpoint EventBridge:**
- [ ] SQS DLQ creada
- [ ] PropagateSystemRole creado con políticas
- [ ] EventBridge custom bus creado
- [ ] EventBridge rule creada con pattern
- [ ] Lambda placeholder creada con VPC y variables
- [ ] Resource policy en Lambda configurada
- [ ] EventBridge rule conectada a Lambda
- [ ] CloudWatch alarm para DLQ configurada
- [ ] Email confirmado para alertas

---

## 9. S3 DATA BUCKET Y SQS BATCH IMPORT

Esta sección configura la infraestructura compartida para la funcionalidad de **Batch Credential Import** (`batch_spec.md`). Se realiza **una sola vez** a nivel de core.

---

### 9.1 Crear S3 Data Bucket

El bucket almacena los ficheros Excel subidos por los tenants para la importación masiva. El acceso está segregado por prefijo IAM: cada tenant solo puede escribir en su propio prefijo `{tenantId}/batch-imports/*`.

#### **Consola AWS:**

1. **S3 Console** → **Create bucket**

2. **Configuración:**
   ```
   Bucket name: sybol-data-{env}         (ej: sybol-data-staging, sybol-data-prod)
   Region: eu-west-1
   Object Ownership: ACLs disabled
   Block Public Access: ALL (todos los checkboxes marcados)
   Versioning: Disabled
   Server-side encryption: SSE-S3 (AES-256)
   ```

3. **Create bucket**

4. **Lifecycle rule** para limpiar ficheros de importación automáticamente:
   - **Management** → **Create lifecycle rule**
   ```
   Rule name: delete-batch-imports
   Filter: Prefix = batch-imports/
   Expiration: 30 days
   ```

5. **Create rule**

#### **AWS CLI (alternativa):**

```bash
ENV=staging   # cambiar a prod en producción
REGION=eu-west-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Crear bucket
aws s3api create-bucket \
  --bucket sybol-data-${ENV} \
  --region ${REGION} \
  --create-bucket-configuration LocationConstraint=${REGION}

# Bloquear todo acceso público
aws s3api put-public-access-block \
  --bucket sybol-data-${ENV} \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Cifrado SSE-S3
aws s3api put-bucket-encryption \
  --bucket sybol-data-${ENV} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"},
      "BucketKeyEnabled": true
    }]
  }'

# Lifecycle: borrar batch-imports/ tras 30 días
aws s3api put-bucket-lifecycle-configuration \
  --bucket sybol-data-${ENV} \
  --lifecycle-configuration '{
    "Rules": [{
      "ID": "delete-batch-imports",
      "Status": "Enabled",
      "Filter": {"Prefix": "batch-imports/"},
      "Expiration": {"Days": 30}
    }]
  }'

echo "Bucket creado: sybol-data-${ENV}"
```

**📝 Anotar:**
```
Data Bucket: sybol-data-{env}
ARN: arn:aws:s3:::sybol-data-{env}
Lifecycle: batch-imports/ → delete after 30 days
```

---

### 9.2 Configurar S3 Event Notification hacia businessLogic Lambda

El bucket debe notificar a la Lambda `businessLogic` (handler `s3ParserHandler`) cuando se sube un `.xlsx` al prefijo `*/batch-imports/`.

#### **Prereq:** La Lambda `businessLogic` debe existir (ver sección 6).

#### **Consola AWS:**

1. **S3** → `sybol-data-{env}` → **Properties** → **Event notifications** → **Create event notification**

2. **Configuración:**
   ```
   Event name: batch-import-put
   Prefix: (dejar vacío — el filtro por tenantId lo hace el handler)
   Suffix: .xlsx
   Event types: ✅ PUT
   Destination: Lambda function
   Lambda function: businesslogic
   ```

3. **Save changes**

⚠️ Si AWS pide permisos: añadir resource-based policy en la Lambda (ver paso AWS CLI abajo).

#### **AWS CLI (alternativa):**

```bash
ENV=staging
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=eu-west-1

# 1. Dar permiso al bucket para invocar la Lambda
aws lambda add-permission \
  --function-name businesslogic \
  --statement-id s3-batch-import-invoke \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::sybol-data-${ENV} \
  --source-account ${ACCOUNT_ID}

# 2. Configurar la notificación S3 → Lambda
aws s3api put-bucket-notification-configuration \
  --bucket sybol-data-${ENV} \
  --notification-configuration '{
    "LambdaFunctionConfigurations": [{
      "Id": "batch-import-put",
      "LambdaFunctionArn": "arn:aws:lambda:'${REGION}':'${ACCOUNT_ID}':function:businesslogic",
      "Events": ["s3:ObjectCreated:Put"],
      "Filter": {
        "Key": {
          "FilterRules": [{"Name": "suffix", "Value": ".xlsx"}]
        }
      }
    }]
  }'

echo "S3 event notification configurada"
```

**📝 Anotar:**
```
Event: s3:ObjectCreated:Put on *.xlsx → businesslogic Lambda (s3ParserHandler)
```

---

### 9.3 Actualizar Execution Role de businessLogic Lambda

La Lambda `businessLogic` necesita permisos para leer del bucket (como actor de sistema, no de tenant).

#### **Consola AWS:**

1. **Lambda** → `businesslogic` → **Configuration** → **Permissions** → Click en el execution role

2. **Add permissions** → **Create inline policy** → **JSON:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BatchImportRead",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::sybol-data-{env}/*"
    }
  ]
}
```

3. **Policy name:** `BusinessLogicS3BatchReadPolicy`

#### **AWS CLI (alternativa):**

```bash
ENV=staging
BUSINESSLOGIC_ROLE_NAME=$(aws lambda get-function-configuration \
  --function-name businesslogic \
  --query 'Role' --output text | cut -d'/' -f2)

aws iam put-role-policy \
  --role-name ${BUSINESSLOGIC_ROLE_NAME} \
  --policy-name BusinessLogicS3BatchReadPolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "S3BatchImportRead",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::sybol-data-'${ENV}'/*"
    }]
  }'
```

---

### 9.4 Crear Cola SQS para Batch Worker

#### **Consola AWS:**

1. **SQS Console** → **Create queue**

2. **Configuración DLQ (crear primero):**
   ```
   Type: Standard
   Name: sybol-batch-worker-dlq-{env}
   Visibility timeout: 30s
   Message retention: 14 days
   Encryption: SSE-SQS
   ```
   - **Create queue**

3. **Configuración cola principal:**
   ```
   Type: Standard
   Name: sybol-batch-worker-{env}
   Visibility timeout: 300s          ← 5 minutos (cubre blockchain + DB)
   Message retention: 14 days
   Receive message wait time: 0s
   Encryption: SSE-SQS
   ```
   - **Dead-letter queue**: `sybol-batch-worker-dlq-{env}`
   - **Maximum receives**: 3
   - **Create queue**

#### **AWS CLI (alternativa):**

```bash
ENV=staging
REGION=eu-west-1

# 1. Crear DLQ
DLQ_URL=$(aws sqs create-queue \
  --queue-name sybol-batch-worker-dlq-${ENV} \
  --attributes '{
    "MessageRetentionPeriod": "1209600",
    "SqsManagedSseEnabled": "true"
  }' \
  --query QueueUrl --output text)

DLQ_ARN=$(aws sqs get-queue-attributes \
  --queue-url ${DLQ_URL} \
  --attribute-names QueueArn \
  --query Attributes.QueueArn --output text)

echo "DLQ ARN: ${DLQ_ARN}"

# 2. Crear cola principal con redrive hacia DLQ
QUEUE_URL=$(aws sqs create-queue \
  --queue-name sybol-batch-worker-${ENV} \
  --attributes '{
    "VisibilityTimeout": "300",
    "MessageRetentionPeriod": "1209600",
    "SqsManagedSseEnabled": "true",
    "RedrivePolicy": "{\"deadLetterTargetArn\":\"'${DLQ_ARN}'\",\"maxReceiveCount\":\"3\"}"
  }' \
  --query QueueUrl --output text)

QUEUE_ARN=$(aws sqs get-queue-attributes \
  --queue-url ${QUEUE_URL} \
  --attribute-names QueueArn \
  --query Attributes.QueueArn --output text)

echo "Queue URL: ${QUEUE_URL}"
echo "Queue ARN: ${QUEUE_ARN}"
```

**📝 Anotar:**
```
Queue URL:   https://sqs.eu-west-1.amazonaws.com/{ACCOUNT_ID}/sybol-batch-worker-{env}
Queue ARN:   arn:aws:sqs:eu-west-1:{ACCOUNT_ID}:sybol-batch-worker-{env}
DLQ URL:     https://sqs.eu-west-1.amazonaws.com/{ACCOUNT_ID}/sybol-batch-worker-dlq-{env}
DLQ ARN:     arn:aws:sqs:eu-west-1:{ACCOUNT_ID}:sybol-batch-worker-dlq-{env}
```

---

### 9.5 Conectar businessLogic Lambda con la cola SQS

#### **Consola AWS:**

1. **Lambda** → `businesslogic` → **Configuration** → **Triggers** → **Add trigger**

2. **Configuración (cola principal):**
   ```
   Source: SQS
   SQS queue: sybol-batch-worker-{env}
   Batch size: 1                ← procesar un mensaje a la vez
   Function response type: Report batch item failures
   ```

3. **Add**

4. Repetir para la **DLQ** (`sybol-batch-worker-dlq-{env}`), misma configuración.

#### **AWS CLI (alternativa):**

```bash
ENV=staging
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=eu-west-1

# Cola principal
aws lambda create-event-source-mapping \
  --function-name businesslogic \
  --event-source-arn arn:aws:sqs:${REGION}:${ACCOUNT_ID}:sybol-batch-worker-${ENV} \
  --batch-size 1 \
  --function-response-types ReportBatchItemFailures

# DLQ
aws lambda create-event-source-mapping \
  --function-name businesslogic \
  --event-source-arn arn:aws:sqs:${REGION}:${ACCOUNT_ID}:sybol-batch-worker-dlq-${ENV} \
  --batch-size 1 \
  --function-response-types ReportBatchItemFailures
```

---

### 9.6 Actualizar Execution Role de businessLogic con permisos SQS

```bash
ENV=staging
BUSINESSLOGIC_ROLE_NAME=$(aws lambda get-function-configuration \
  --function-name businesslogic \
  --query 'Role' --output text | cut -d'/' -f2)

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=eu-west-1

aws iam put-role-policy \
  --role-name ${BUSINESSLOGIC_ROLE_NAME} \
  --policy-name BusinessLogicSQSBatchPolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "SQSBatchWorker",
        "Effect": "Allow",
        "Action": [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:SendMessage"
        ],
        "Resource": [
          "arn:aws:sqs:'${REGION}':'${ACCOUNT_ID}':sybol-batch-worker-'${ENV}'",
          "arn:aws:sqs:'${REGION}':'${ACCOUNT_ID}':sybol-batch-worker-dlq-'${ENV}'"
        ]
      }
    ]
  }'
```

---

### 9.7 Actualizar Variables de Entorno de businessLogic Lambda

Añadir las variables de entorno del batch a la Lambda:

#### **Consola AWS:**

**Lambda** → `businesslogic` → **Configuration** → **Environment variables** → **Edit** → añadir:

```
BATCH_QUEUE_URL   = https://sqs.eu-west-1.amazonaws.com/{ACCOUNT_ID}/sybol-batch-worker-{env}
BATCH_S3_BUCKET   = sybol-data-{env}
```

#### **AWS CLI:**

```bash
# Añadir variables (merge con las existentes - obtener primero las actuales)
CURRENT_VARS=$(aws lambda get-function-configuration \
  --function-name businesslogic \
  --query 'Environment.Variables' --output json)

# Editar manualmente: añadir BATCH_QUEUE_URL y BATCH_S3_BUCKET al JSON resultante
# Luego aplicar:
aws lambda update-function-configuration \
  --function-name businesslogic \
  --environment "Variables={
    BATCH_QUEUE_URL=https://sqs.eu-west-1.amazonaws.com/ACCOUNT_ID/sybol-batch-worker-ENV,
    BATCH_S3_BUCKET=sybol-data-ENV
  }"
```

⚠️ **IMPORTANTE:** El comando `update-function-configuration` para `Environment` reemplaza **todas** las variables. Asegúrate de incluir las variables existentes en el JSON.

---

### 9.8 Configurar CORS en el S3 Data Bucket

El frontend sube los ficheros Excel directamente al bucket usando una **presigned URL** generada por el backend (Lambda businessLogic). El browser realiza un `PUT` HTTP con esa URL prefirmada, lo que provoca un preflight `OPTIONS` que S3 debe autorizar. El bucket necesita una política CORS para ello; sin ella el upload falla con `403 Forbidden` antes de llegar al `PUT`.

#### Consola AWS

1. **S3 Console** → `sybol-data-{env}` → **Permissions** → **Cross-origin resource sharing (CORS)** → **Edit**
2. Pegar el siguiente JSON y guardar:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "GET", "HEAD"],
    "AllowedOrigins": [
      "http://localhost:3000",
      "https://app.{env}.wallet.sybol.id"
    ],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

> Ajusta `AllowedOrigins` con los dominios reales del frontal para cada entorno. Para producción elimina `localhost:3000`.

#### AWS CLI

```bash
ENV=dev   # cambiar por staging / prod según corresponda
BUCKET="sybol-data-${ENV}"
FRONTEND_ORIGIN="https://app.${ENV}.wallet.sybol.id"

aws s3api put-bucket-cors \
  --bucket "$BUCKET" \
  --cors-configuration "{
    \"CORSRules\": [{
      \"AllowedHeaders\": [\"*\"],
      \"AllowedMethods\": [\"PUT\", \"GET\", \"HEAD\"],
      \"AllowedOrigins\": [\"${FRONTEND_ORIGIN}\"],
      \"ExposeHeaders\": [\"ETag\"],
      \"MaxAgeSeconds\": 3000
    }]
  }"
```

Verificar que se guardó correctamente:

```bash
aws s3api get-bucket-cors --bucket "$BUCKET"
```

---

✅ **Checkpoint S3 + SQS Batch:**
- [ ] Bucket `sybol-data-{env}` creado con `BlockPublicAccess` total y SSE-S3
- [ ] Lifecycle rule: `batch-imports/` → delete after 30 days
- [ ] S3 Event Notification: `.xlsx` PUT → Lambda `businesslogic`
- [ ] Lambda `businesslogic` tiene `s3:GetObject` en el bucket
- [ ] DLQ `sybol-batch-worker-dlq-{env}` creada
- [ ] Cola `sybol-batch-worker-{env}` creada (visibility 300s, redrive → DLQ, maxReceives 3)
- [ ] Lambda `businesslogic` conectada a la cola (trigger, batch size 1)
- [ ] Lambda `businesslogic` conectada a la DLQ (trigger, batch size 1)
- [ ] Lambda `businesslogic` tiene permisos SQS
- [ ] Variables de entorno `BATCH_QUEUE_URL` y `BATCH_S3_BUCKET` configuradas
- [ ] CORS configurado en el bucket `sybol-data-{env}` con los orígenes del frontal

---

## 10. CREAR USUARIO PROPAGATE_SYSTEM

⚠️ **UNA SOLA VEZ** - Usuario global para Propagate Service.

### 9.1 Propósito del Usuario

Según las **business rules de permisos PostgreSQL**:

- **propagate_system** es un usuario especial que:
  - ✅ Tiene acceso de LECTURA + ESCRITURA a **TODAS** las databases `tenant_*`
  - ❌ NO tiene acceso a `catalog`
  - ❌ NO tiene acceso a `backofficedev`
  
- **Cuándo se usa:**
  - El servicio **Propagate** (`v1/services/propagate`) usa este usuario
  - Propaga credenciales, presentaciones y otros objetos de identidad entre tenants
  - Inserta datos en tablas como `credentials`, `presentations`, `presentation_requests`

- **Permisos en tenants:**
  - Los permisos se otorgan **cada vez que se crea un nuevo tenant**
  - Ver **[GUIA_OPERATIVA_MULTI_TENANT.md - Sección 4.5 y 4.7](#)** para detalles

### 9.2 Crear Usuario

#### **Conectar al cluster:**

```bash
psql -h sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
     -U postgres \
     -p 5432 \
     -d postgres
```

#### **Crear usuario:**

```sql
-- Crear usuario global propagate_system
CREATE USER propagate_system WITH PASSWORD 'PASSWORD_MUY_SEGURA_PROPAGATE_XYZ!';

-- Verificar
\du propagate_system
```

**📝 Anotar:**
```
User: propagate_system
Password: [GUARDAR EN SECRETS MANAGER]
Propósito: Acceso a TODAS las tenant_* databases (lectura+escritura)
Sin acceso: catalog, backofficedev
```

💡 **Nota Importante:** 
- Este usuario NO recibe permisos aquí
- Los permisos se otorgan en cada `tenant_*` cuando se crea
- Ver **GUIA_OPERATIVA_MULTI_TENANT.md - Sección 4** para el flujo completo

### 9.3 Validación

Después de crear tenants, validar permisos con:

```bash
# Desde v1/services/database/
cd /path/to/v1/services/database

# Configurar credenciales en check_permissions.py
vim check_permissions.py  # Editar DB_CONFIG

# Ejecutar validación
python3 check_permissions.py

# Revisar outputs
cat output/compliance_report.txt
```

El sistema validará automáticamente que `propagate_system`:
- ✅ Tiene acceso a todas las `tenant_*`
- ❌ NO tiene acceso a `catalog` ni `backofficedev`

---

## ✅ CHECKLIST FINAL

### Dominio:
- [ ] Dominio registrado en Route 53
- [ ] Hosted zone creada

### Cognito:
- [ ] User Pool con custom attributes
- [ ] App Client configurado
- [ ] Identity Pool creado
- [ ] Rol Cognito_sybol_Auth_Role

### RDS:
- [ ] Cluster PostgreSQL 17.4
- [ ] Database `backofficedev` creada
- [ ] Usuario `sybol_admin` con LECTURA+ESCRITURA en backofficedev y catalog
- [ ] Database `catalog` creada
- [ ] Usuario `catalog` con SOLO LECTURA en catalog
- [ ] Usuario `propagate_system` global creado (sin permisos aún)
- [ ] PUBLIC sin acceso (REVOKE ejecutado en ambas databases)
- [ ] Security group permite lambdas

### VPC:
- [ ] VPC con subnets públicas
- [ ] Internet Gateway
- [ ] Route table configurada
- [ ] Auto-assign IP habilitado
- [ ] Security groups creados

### IAM:
- [ ] Policy `LambdaAssumeTenantRolesPolicy` creada

### SQS + S3 Batch:
- [ ] Bucket `sybol-data-{env}` creado con BlockPublicAccess y SSE-S3
- [ ] Lifecycle rule batch-imports/ → 30 days
- [ ] S3 Event Notification → businesslogic Lambda
- [ ] DLQ + cola batch-worker creadas
- [ ] Lambda triggers SQS + DLQ
- [ ] Permisos S3 y SQS en execution role de businesslogic
- [ ] Variables BATCH_QUEUE_URL y BATCH_S3_BUCKET en Lambda

### Propagate:

### Lambdas:
- [ ] 4 repos ECR
- [ ] 4 imágenes Docker
- [ ] 4 Lambdas creadas
- [ ] Environment variables
- [ ] VPC configurada
- [ ] Policies STS adjuntas

### API Gateway:
- [ ] backoffice-api
- [ ] sybol-api
- [ ] Authorizer Cognito
- [ ] Custom domains (opcional)

---

## 🎯 SIGUIENTE PASO

Continúa con:

📘 **[GUIA_OPERATIVA_MULTI_TENANT.md](./GUIA_OPERATIVA_MULTI_TENANT.md)** - Alta de tenants

---

## 📋 VALORES PARA COPIAR

```bash
# AWS
AWS_REGION=eu-west-1
AWS_ACCOUNT_ID=XXXXXX

# Cognito
USER_POOL_ID=eu-west-1_XXXXXXXXX
APP_CLIENT_ID=1234567890abcdefghij
IDENTITY_POOL_ID=eu-west-1:aaaa-bbbb-cccc-dddd-eeee

# RDS
RDS_ENDPOINT=sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com
RDS_PORT=5432
PROPAGATE_USER=propagate_system

# VPC
VPC_ID=vpc-0abc123
SUBNET_1A=subnet-pub1a
SUBNET_1B=subnet-pub1b
LAMBDA_SG=sg-lambda123
RDS_SG=sg-rds123
IGW_ID=igw-0xyz789

# ECR URIs
BACKOFFICE_ECR=ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/backoffice
BUSINESSLOGIC_ECR=ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/businesslogic
PROPAGATE_ECR=ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/propagate
CATALOG_ECR=ACCOUNT_ID.dkr.ecr.eu-west-1.amazonaws.com/sybol/catalog

# Lambda ARNs
BACKOFFICE_LAMBDA=arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:backoffice
BUSINESSLOGIC_LAMBDA=arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:businesslogic
PROPAGATE_LAMBDA=arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:propagate
CATALOG_LAMBDA=arn:aws:lambda:eu-west-1:ACCOUNT_ID:function:catalog

# Execution Roles (para Trust Policies)
BUSINESSLOGIC_ROLE=arn:aws:iam::ACCOUNT_ID:role/service-role/businesslogic-role-xxxxx
PROPAGATE_ROLE=arn:aws:iam::ACCOUNT_ID:role/service-role/propagate-role-xxxxx
COGNITO_AUTH_ROLE=arn:aws:iam::ACCOUNT_ID:role/Cognito_sybol_Auth_Role

# API Gateway
BACKOFFICE_API_URL=https://backoffice.sybol.id
API_URL=https://api.sybol.id
```

---

## ⚠️ MEJORA FUTURA: SEPARACIÓN DE ACCESO POR APP CLIENT

### Contexto del Problema

Actualmente, **cualquier usuario autenticado** (independientemente de su `custom:tenant_id`) puede llamar a los endpoints de backoffice y API, ya que API Gateway solo valida que el JWT sea válido, no el contenido de los custom claims.

### Solución Recomendada (A Implementar)

Crear **2 App Clients separados** en Cognito para segregar el acceso:

#### **Paso 1: Crear segundo App Client**

1. **Cognito** → **User pools** → `sybol-user-pool` → **App integration** → **App clients** → **Create app client**

2. **Configuración:**
   ```
   Name: sybol-backoffice-client
   Type: Public client
   Client secret: Don't generate
   Authentication flows:
     ✅ ALLOW_USER_SRP_AUTH
     ✅ ALLOW_REFRESH_TOKEN_AUTH
   ```

3. **Anotar App Client IDs:**
   ```
   Backoffice Client: 9876543210zyxwvutsrqp
   Tenant Client: 1234567890abcdefghij (original)
   ```

#### **Paso 2: Actualizar Authorizers**

**backoffice-api:**
```
Authorizer: cognito-backoffice-authorizer
Audience: 9876543210zyxwvutsrqp  ← Solo backoffice client
```

**sybol-api:**
```
Authorizer: cognito-tenant-authorizer
Audience: 1234567890abcdefghij  ← Solo tenant client
```

#### **Paso 3: Lógica en Frontend**

```javascript
// Login diferenciado por tenant
const tenantId = user.attributes['custom:tenant_id'];

if (tenantId === 'sybol') {
  // Usuario sybol: obtener 2 tokens
  const backofficeToken = await getTokenForClient('9876543210zyxwvutsrqp');
  const tenantToken = await getTokenForClient('1234567890abcdefghij');
} else {
  // Usuario normal: solo tenant token
  const tenantToken = await getTokenForClient('1234567890abcdefghij');
}
```

#### **Paso 4: Validación adicional en Lambda (Opcional pero recomendado)**

Añadir middleware en `backoffice` Lambda:

```javascript
// v1/services/backoffice/src/middleware/authMiddleware.js
const jwt = require('jsonwebtoken');

const checkSybolTenant = (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  const decoded = jwt.decode(token);
  
  // Verificar audience (backoffice client)
  if (decoded.aud !== '9876543210zyxwvutsrqp') {
    return res.status(403).json({ 
      error: 'Invalid client',
      message: 'Must use backoffice app client' 
    });
  }
  
  // Verificar tenant_id
  if (decoded['custom:tenant_id'] !== 'sybol') {
    return res.status(403).json({ 
      error: 'Forbidden',
      message: 'Only sybol tenant can access backoffice' 
    });
  }
  
  req.tenantId = 'sybol';
  next();
};

module.exports = { checkSybolTenant };
```

Aplicar en todas las rutas:

```javascript
// v1/services/backoffice/src/app.js
const { checkSybolTenant } = require('./middleware/authMiddleware');

app.use(checkSybolTenant);  // Aplicar globalmente
```

### Ventajas de esta Solución

✅ **Separación clara** de accesos por App Client  
✅ **API Gateway valida `aud`** automáticamente (sin Lambda Authorizer)  
✅ **Doble capa de seguridad**: API Gateway + validación en Lambda  
✅ **Sin Lambda Authorizer** adicional (menor complejidad)  
✅ **Escalable** para futuros roles/permisos

### Cuándo Implementar

- Cuando sea necesario **restringir estrictamente** acceso a backoffice
- Antes de **abrir a producción con múltiples tenants**
- Como parte de **auditoría de seguridad**

📝 **Nota:** Por ahora, la validación en las Lambdas (sección 6) es suficiente para entornos de desarrollo/staging.

---
