# �� GUÍA OPERATIVA MULTI-TENANT - ALTA DE TENANTS

Esta guía detalla paso a paso el proceso de alta de un nuevo tenant en el sistema Sybol. **Esta operación se ejecuta N veces, una por cada tenant**.

⚠️ **PREREQUISITOS:** Asegúrate de haber completado primero **[CORE_SETUP.md](./CORE_SETUP.md)** antes de proceder con esta guía.

---

## 📋 ÍNDICE

1. [Preparación - Dominio y Certificado](#1-preparación-dominio-y-certificado)
2. [CloudFront y S3](#2-cloudfront-y-s3)
3. [Usuario en Cognito](#3-usuario-en-cognito)
4. [Database RDS](#4-database-rds)
5. [Secrets Manager](#5-secrets-manager)
6. [IAM Roles del Tenant](#6-iam-roles-del-tenant)
7. [KMS Keys](#7-kms-keys)
8. [DID Document](#8-did-document)
9. [Despliegue Frontend](#9-despliegue-frontend)

---

## 📝 NOMENCLATURA

Para este ejemplo usaremos:
- **Tenant ID:** `repsol`
- **Roles:** `admin`, `reader`

Sustituir según corresponda para cada tenant.

---

## 1. PREPARACIÓN - DOMINIO Y CERTIFICADO

### 1.1 Crear Subdominio

1. **Route 53** → **Hosted zones** → Seleccionar `sybol.id`

2. **Create record**
   ```
   Record name: repsol.staging.wallet
   Record type: A - IPv4 address
   Value: (Temporal - se actualizará después con CloudFront)
   ```

**Formato:** `{tenantId}.staging.wallet.sybol.id`

**📝 Anotar:**
```
Domain: repsol.staging.wallet.sybol.id
```

### 1.2 Solicitar Certificado ACM

1. **AWS Certificate Manager** → **Request certificate**

2. **Request public certificate**

3. **Domain name:** `repsol.staging.wallet.sybol.id`

4. **Validation method:** DNS validation

5. **Request**

6. **Create records in Route 53:**
   - Copiar CNAME record
   - Route 53 → Hosted zones → sybol.id
   - Create record → Pegar valores CNAME
   - Create

⏱️ Tarda 5-15 minutos en validar.

**📝 Anotar:**
```
Certificate ARN: arn:aws:acm:us-east-1:ACCOUNT_ID:certificate/xxxxx
Status: Issued
```

⚠️ **IMPORTANTE:** Certificados para CloudFront deben estar en **us-east-1**.

✅ **Checkpoint Dominio:**
- [ ] Subdominio creado en Route 53
- [ ] Certificado ACM solicitado
- [ ] Certificado validado y estado "Issued"

---

## 2. CLOUDFRONT Y S3

### 2.1 Crear S3 Bucket
El bucket que se usara es sybol-statics/wwc-staging/{tenantid}
1. **S3 Console** → **Create bucket**

2. **Configuración:**
   ```
   Bucket name: repsol-staging-wallet-frontend
   Region: eu-west-1
   Block all public access: ✅ Enable (CloudFront accederá via OAI)
   Versioning: Disable
   Encryption: SSE-S3
   ```

3. **Create**

**📝 Anotar:**
```
Bucket: repsol-staging-wallet-frontend
Region: eu-west-1
```

### 2.2 Crear CloudFront Distribution

1. **CloudFront Console** → **Create distribution**

2. **Origin settings:**
   - **Origin domain:** `repsol-staging-wallet-frontend.s3.eu-west-1.amazonaws.com`
   - **Origin access:** Origin access control (OAC)
   - **Create new OAC** → Create

3. **Default cache behavior:**
   - **Viewer protocol policy:** Redirect HTTP to HTTPS
   - **Allowed HTTP methods:** GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
   - **Cache key and origin requests:**
     - **Cache policy:** CachingOptimized
     - **Origin request policy:** CORS-S3Origin (para headers CORS)

4. **Settings:**
   - **Price class:** Use only North America and Europe
   - **Alternate domain names (CNAME):** `repsol.staging.wallet.sybol.id`
   - **Custom SSL certificate:** Seleccionar certificado creado en paso 1.2
   - **Default root object:** `index.html`

5. **Error pages:** (SPA routing)
   - **Create custom error response**
     ```
     HTTP error code: 403
     Response page path: /index.html
     HTTP response code: 200
     ```
   - Repetir para error 404

6. **Create distribution**

⏱️ Tarda 10-15 minutos en desplegar.

**📝 Anotar:**
```
Distribution ID: E123456789ABCD
Domain name: d111111abcdef8.cloudfront.net
Status: Enabled
```

### 2.3 Actualizar S3 Bucket Policy

CloudFront te dará un mensaje para actualizar bucket policy. Copiar y aplicar en:

**S3** → Bucket → **Permissions** → **Bucket policy**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Service": "cloudfront.amazonaws.com"
    },
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::repsol-staging-wallet-frontend/*",
    "Condition": {
      "StringEquals": {
        "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/E123456789ABCD"
      }
    }
  }]
}
```

### 2.4 Actualizar Route 53

1. **Route 53** → **Hosted zones** → `sybol.id`

2. **Edit record:** `repsol.staging.wallet.sybol.id`
   ```
   Record type: A
   Alias: Yes
   Alias target: d111111abcdef8.cloudfront.net (CloudFront distribution)
   ```

3. **Save**

✅ **Checkpoint CloudFront:**
- [ ] S3 bucket creado
- [ ] CloudFront distribution desplegada
- [ ] Bucket policy configurada
- [ ] Dominio apuntando a CloudFront
- [ ] HTTPS funcionando

---

## 3. USUARIO EN COGNITO

### 3.1 Crear Usuario en User Pool

1. **Cognito** → **User pools** → `sybol-user-pool`

2. **Users** → **Create user**

3. **Configuración:**
   ```
   Email: usuario@repsol.com
   Send email invitation: ✅ Yes
   Temporary password: [AUTO-GENERADA]
   ```

4. **Custom attributes:** ⚠️ **CRÍTICO**
   ```
   custom:tenant_id = repsol
   custom:role = admin
   ```


### 3.2 Verificar Configuración

1. Usuario debe aparecer en **Users** con status `FORCE_CHANGE_PASSWORD`

2. Usuario recibe email con contraseña temporal

3. Al primer login, debe cambiar password

✅ **Checkpoint Cognito:**
- [ ] Usuario(s) creado(s) en User Pool
- [ ] Custom attributes tenant_id y role configurados
- [ ] Email de invitación enviado
- [ ] Usuario puede hacer login

---

## 4. DATABASE RDS

⚠️ **IMPORTANTE - BUSINESS RULES DE PERMISOS:**

Esta sección configura la database y usuarios del tenant siguiendo las **Business Rules** del sistema:

**Lo que vas a crear:**
- Database `tenant_{tenantId}` (ej: tenant_repsol)
- Usuario `{tenantId}_admin` (lectura + escritura en su tenant)
- Usuario `{tenantId}_user` (solo lectura en su tenant)


**Permisos que configurarás:**
1. ✅ Escritura/Lectura en `tenant_{tenant}` propio
2. ✅ Lectura en `catalog` (sección 4.8)
3. ✅ Lectura en `backoffice` (sección 4.8)
4. ✅ Acceso para `propagate_system` (sección 4.7)
5. ❌ SIN acceso a otros `tenant_*`

---

### 4.1 Crear Database del Tenant

⚠️ **IMPORTANTE:** El nombre de la database DEBE seguir el patrón `tenant_{tenantId}` para que el sistema de compliance automático funcione correctamente.

#### **Crear database:**

```sql
-- Crear database (nombre DEBE ser tenant_{tenantId})
CREATE DATABASE tenant_repsol;

-- Conectar a la nueva database
\c tenant_repsol

-- PASO CRÍTICO: REVOCAR acceso público
-- Por defecto PostgreSQL da CONNECT a PUBLIC, esto DEBE eliminarse
REVOKE CONNECT ON DATABASE tenant_repsol FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;


💡 **Nota sobre PUBLIC:** El REVOKE es crítico porque:
- PostgreSQL otorga acceso CONNECT a PUBLIC por defecto
- Esto permitiría a cualquier usuario conectarse a la database
- Debes otorgar permisos explícitamente solo a usuarios autorizados

### 4.2 Crear Usuarios PostgreSQL

⚠️ **NAMING PATTERN CRÍTICO:** Los nombres de usuarios DEBEN seguir el patrón:
- `{tenantId}_admin`: Usuario administrador
- `{tenantId}_user`: Usuario de solo lectura

#### **Crear usuarios:**

```sql
-- Conectar a la database del tenant
\c tenant_repsol

-- Crear usuarios con contraseñas seguras
-- IMPORTANTE: Respetar naming pattern {tenantId}_admin y {tenantId}_user
CREATE USER repsol_admin WITH PASSWORD 'GENERAR_PASSWORD_SEGURA_1';
CREATE USER repsol_user WITH PASSWORD 'GENERAR_PASSWORD_SEGURA_2';

```

**💡 Generar passwords seguras:**
```bash
openssl rand -base64 32
```

**📝 Anotar:**
```
Tenant: repsol
Admin User: repsol_admin
Admin Password: [GUARDAR PARA SECRETS]
Reader User: repsol_user
Reader Password: [GUARDAR PARA SECRETS]
```

### 4.3 Configurar Permisos {tenant}_admin

```sql
-- Conectado a tenant_repsol
\c tenant_repsol

-- PASO 1: Permisos completos para admin en SU PROPIA tenant database
GRANT CONNECT ON DATABASE tenant_repsol TO repsol_admin;
GRANT ALL PRIVILEGES ON DATABASE tenant_repsol TO repsol_admin;
GRANT ALL PRIVILEGES ON SCHEMA public TO repsol_admin;

-- Permisos en tablas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO repsol_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO repsol_admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO repsol_admin;

-- Permisos en tablas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
  GRANT ALL ON TABLES TO repsol_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
  GRANT ALL ON SEQUENCES TO repsol_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
  GRANT ALL ON FUNCTIONS TO repsol_admin;

-- Verificar permisos
\z
```

💡 **Nota:** Los permisos de LECTURA en `catalog` y `backoffice` se otorgarán en la **sección 4.8** más adelante.

### 4.4 Configurar Permisos {tenant}_user

```sql
-- Conectado a tenant_repsol
\c tenant_repsol

-- PASO 1: Permisos de SOLO LECTURA para user en SU PROPIA tenant database
GRANT CONNECT ON DATABASE tenant_repsol TO repsol_user;
GRANT USAGE ON SCHEMA public TO repsol_user;

-- Permisos en tablas existentes (solo SELECT)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO repsol_user;

-- Permisos en tablas futuras (solo SELECT)
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
  GRANT SELECT ON TABLES TO repsol_user;

```

💡 **Nota:** Los permisos de LECTURA en `catalog` y `backoffice` se otorgarán en la **sección 4.8** más adelante.

### 4.5 Preparar Acceso para Propagate System

⚠️ El usuario `propagate_system`:
- ✅ Tiene LECTURA + ESCRITURA en **TODAS** las databases `tenant_*`
- ❌ NO tiene acceso a `catalog` ni `backoffice`
- 🎯 Usado por el servicio Propagate para insertar credenciales, presentaciones, etc.

**🔄 Proceso:**
1. El usuario `propagate_system` ya fue creado globalmente en CORE_SETUP
2. Aquí solo otorgamos permisos de CONEXIÓN (los permisos de escritura se otorgan en sección 4.7)

```sql
-- Conectado a tenant_repsol
\c tenant_repsol

-- Permisos básicos de conexión
GRANT CONNECT ON DATABASE tenant_repsol TO propagate_system;
GRANT USAGE ON SCHEMA public TO propagate_system;
```

💡 **Nota:** Los permisos completos de INSERT/UPDATE/DELETE se otorgarán en la **sección 4.7** después de crear las tablas.

### 4.6 Ejecutar Schemas

#### **Copiar schema al servidor:**

#### **Ejecutar schema:**

-- Tablas esperadas:
-- credentials
-- credential_status
-- presentations
-- presentation_status
-- presentation_requests
-- presentation_request_status
-- contacts
-- events
-- delegates
-- batch_processes             ← nuevo (Batch Credential Import)
-- batch_process_log           ← nuevo (Batch Credential Import)
-- batch_credential_intents    ← nuevo (Didless credential staging)


### 4.6.1 Insertar Contacto Propio (Self-Contact)

⚠️ **IMPORTANTE:** Después de crear las tablas, debes insertar los datos de contacto de la empresa propia. Esto permite que el tenant aparezca en su propia lista de contactos con estado 'accepted'.

```sql
-- Como repsol_admin, conectado a tenant_repsol
\c tenant_repsol repsol_admin

-- Insertar el contacto propio del tenant
-- Sustituir con los datos reales del tenant:
 INSERT INTO contacts (
    tenant_id,
    did,
    business_name,
    cif,
    email,
    status,
    tel,
    created_at,
    updated_at
) VALUES (
    'repsol',                                    -- tenant_id propio
    'did:elsi:VATES-A28887011',                  -- DID del tenant (obtener del DID Document)
    'Repsol S.A.',                               -- business_name del tenant
    'A28887011',                                 -- CIF del tenant
    'contacto@repsol.com',                       -- email del tenant
    'accepted',                                  -- status: accepted (contacto propio siempre aceptado)
    '+34912345678',                              -- tel del tenant (opcional)
    NOW(),
    NOW()
);
```

**📝 Datos necesarios para el INSERT:**
- `tenant_id`: ID del tenant (ej: repsol)
- `did`: DID del tenant creado en el paso 8 (DID Document)
- `business_name`: Nombre comercial de la empresa
- `cif`: NIF/CIF de la empresa
- `email`: Email de contacto corporativo
- `tel`: Teléfono de contacto (opcional)


### 4.7 Configurar Permisos Propagate en Tablas

⚠️ **Según Business Rules:** Después de crear las tablas, `propagate_system` necesita permisos completos de LECTURA + ESCRITURA en las tablas de identity objects.

**🎯 Tablas objetivo:**
- `credentials`, `credential_status`
- `presentations`, `presentation_status`
- `presentation_requests`, `presentation_request_status`

```sql
-- Conectado a tenant_repsol
\c tenant_repsol

-- Permisos completos en tablas de identity objects
GRANT ALL PRIVILEGES ON TABLE credentials TO propagate_system;
GRANT ALL PRIVILEGES ON TABLE credential_status TO propagate_system;
GRANT ALL PRIVILEGES ON TABLE presentations TO propagate_system;
GRANT ALL PRIVILEGES ON TABLE presentation_status TO propagate_system;
GRANT ALL PRIVILEGES ON TABLE presentation_requests TO propagate_system;
GRANT ALL PRIVILEGES ON TABLE presentation_request_status TO propagate_system;

-- Permisos en sequences (necesarios para INSERT con IDs autoincrementales)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO propagate_system;
```

**📝 Anotar:**
```
Database: tenant_repsol
propagate_system: LECTURA + ESCRITURA en tablas de identity objects
✅ Puede insertar credentials y presentations
✅ Puede acceder a sequences
❌ NO puede acceder a tablas como contacts, events, delegates (permisos no otorgados)
```

### 4.7.1 Otorgar Permisos de las Tablas Batch al Tenant Admin

Las tablas `batch_processes`, `batch_process_log` y `batch_credential_intents` se crean en el schema de cada tenant con `schema_v2.sql`. El usuario `{tenant}_admin` necesita permisos completos para que la Lambda `businessLogic` (que asume `TenantRole-{tenant}-admin`) pueda operar sobre ellas.

```sql
-- Conectado a tenant_repsol como superuser
\c tenant_repsol

-- Reemplazar repsol_admin con el nombre real del usuario admin del tenant
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE batch_processes          TO repsol_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE batch_process_log        TO repsol_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE batch_credential_intents TO repsol_admin;

-- Secuencia del campo SERIAL en batch_process_log
GRANT USAGE, SELECT ON SEQUENCE batch_process_log_id_seq               TO repsol_admin;
```

**Verificación:**

```sql
-- Verificar que repsol_admin tiene permisos en las tablas batch
\z batch_processes
\z batch_process_log
\z batch_credential_intents
```

**📝 Anotar:**
```
Tablas batch: batch_processes, batch_process_log, batch_credential_intents
Usuario: repsol_admin → SELECT, INSERT, UPDATE, DELETE
Secuencia: batch_process_log_id_seq → USAGE, SELECT
```

### 4.8 Otorgar Permisos de Lectura en Catalog y backoffice

⚠️ **PASO CRÍTICO:** Según las business rules, todos los usuarios `{tenant}_admin` y `{tenant}_user` deben tener permisos de LECTURA en las databases core `catalog` y `backoffice`.

#### **4.8.1 Permisos en Catalog**

```sql
-- Conectar a catalog
\c catalog

-- Otorgar permisos de LECTURA a repsol_admin
GRANT CONNECT ON DATABASE catalog TO repsol_admin;
GRANT USAGE ON SCHEMA public TO repsol_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO repsol_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO repsol_admin;

-- Otorgar permisos de LECTURA a repsol_user
GRANT CONNECT ON DATABASE catalog TO repsol_user;
GRANT USAGE ON SCHEMA public TO repsol_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO repsol_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO repsol_user;

-- Verificar permisos
\z
\du repsol_admin
\du repsol_user
```

> 💡 **Nota sobre migraciones de schema:** los `GRANT SELECT ON ALL TABLES` otorgados aquí cubren automáticamente cualquier columna nueva añadida a tablas existentes (incluyendo las migraciones v1→v2 de `forms`, `form_sections`, `form_fields`). No es necesario re-ejecutar estos grants cuando se apliquen migraciones de schema en `catalog`. Ver sección 3.3.1 de `core-setup.md` para los scripts de migración.

#### **4.8.2 Permisos en backoffice**

```sql
-- Conectar a backoffice
\c backoffice

-- Otorgar permisos de LECTURA a repsol_admin
GRANT CONNECT ON DATABASE backoffice TO repsol_admin;
GRANT USAGE ON SCHEMA public TO repsol_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO repsol_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO repsol_admin;

-- Otorgar permisos de LECTURA a repsol_user
GRANT CONNECT ON DATABASE backoffice TO repsol_user;
GRANT USAGE ON SCHEMA public TO repsol_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO repsol_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO repsol_user;

```

**📝 Resumen de permisos finales para tenant repsol:**

| Usuario | tenant_repsol | catalog | backoffice | Otros tenant_* |
|---------|---------------|---------|---------------|----------------|
| repsol_admin | ✅ Lectura + Escritura | ✅ Lectura | ✅ Lectura | ❌ Sin acceso |
| repsol_user | ✅ Lectura | ✅ Lectura | ✅ Lectura | ❌ Sin acceso |
| propagate_system | ✅ Lectura + Escritura (tablas específicas) | ❌ Sin acceso | ❌ Sin acceso | ✅ Todos los tenant_* |

### 4.9 Validación con Sistema de Compliance

⚠️ **IMPORTANTE:** Después de configurar todos los permisos, debes validar que cumplen con las business rules usando el sistema de compliance automático.

#### **Ejecutar validación:**

```bash
# Desde v1/services/database/
cd /path/to/v1/services/database

# Configurar credenciales en check_permissions.py (si no lo has hecho)
vim check_permissions.py  # Editar DB_CONFIG con host, port, user, password

# Ejecutar script de compliance
python3 check_permissions.py

# El script genera 3 archivos en output/:
# 1. reporte_permisos.xlsx - Excel con matriz de permisos
# 2. compliance_report.txt - Resumen de violaciones
# 3. fix_permissions.sql - SQL para corregir violaciones
```

#### **Si hay violaciones:**

```bash
# Revisar el SQL generado
cat output/fix_permissions.sql

# Aplicar correcciones
psql -h sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com \
     -U postgres \
     -p 5432 \
     -d postgres \
     -f output/fix_permissions.sql

# Volver a ejecutar validación
python3 check_permissions.py

# Verificar que ahora muestra 0 violaciones
cat output/compliance_report.txt
```

**📝 Anotar:**
```
Database: tenant_repsol
Admin User: repsol_admin
Admin Password: [GUARDAR PARA SECRETS]
User User: repsol_user
User Password: [GUARDAR PARA SECRETS]
Compliance: ✅ CUMPLE (0 violaciones)
```

✅ **Checkpoint Database:**
- [ ] Database tenant_repsol creada
- [ ] PUBLIC sin acceso (REVOKE ejecutado)
- [ ] Usuarios repsol_admin y repsol_user creados
- [ ] Permisos configurados en tenant_repsol
- [ ] Permisos de lectura en catalog otorgados
- [ ] Permisos de lectura en backoffice otorgados
- [ ] Propagate_system tiene permisos en tenant_repsol
- [ ] Schema ejecutado
- [ ] Tablas creadas
- [ ] Contacto propio insertado en tabla contacts
- [ ] Compliance validado (0 violaciones)

---

## 5. SECRETS MANAGER

### 5.1 Crear Secret Admin

1. **Secrets Manager** → **Store a new secret**

2. **Secret type:** Credentials for Amazon RDS database

3. **Credentials:**
   ```
   Username: repsol_admin
   Password: [PASSWORD GENERADA EN PASO 4.2]
   ```

4. **Database:** Select `sybol-cluster`

5. **Secret name:** `tenant/repsol/admin-password`

6. **Description:** Database credentials for tenant repsol admin role

7. **Configure rotation:**
   - ✅ Enable automatic rotation
   - **Rotation schedule:** 30 days
   - **Select rotation function:** Usar función existente de RDS (SecretsManagerpostgres-rotation-lambda)

8. **Next** → **Store**

⚠️ **IMPORTANTE:** AWS Secrets Manager crea el secret con los campos básicos (username, password, host, port, engine). 

- Para tenant repsol: configurar `DB_NAME=tenant_repsol` en las Lambdas

**Secret JSON creado automáticamente:**
```json
{
  "username": "repsol_admin",
  "password": "PASSWORD_SEGURA",
  "engine": "postgres",
  "host": "sybol-cluster.cluster-xxxxx.eu-west-1.rds.amazonaws.com",
  "port": 5432,
  "dbClusterIdentifier": "sybol-cluster"
}
```
✅ **El campo `dbname`  debe incluirse en el secret.
Pegar '"dbname": "tenant_tritemius"' en el plaintext del secret
### 5.2 Crear Secret User

Repetir el proceso completo:
- **Username:** `repsol_user`
- **Password:** [PASSWORD GENERADA EN PASO 4.2]
- **Secret name:** `tenant/repsol/user-password`
- **Añadir campo `dbname` igual que en el anterior** 

**📝 Anotar:**
```
Admin Secret ARN: arn:aws:secretsmanager:eu-west-1:ACCOUNT_ID:secret:tenant/repsol/admin-password-xxxxx
User Secret ARN: arn:aws:secretsmanager:eu-west-1:ACCOUNT_ID:secret:tenant/repsol/user-password-xxxxx
```

✅ **Checkpoint Secrets:**
- [ ] Secret admin creado
- [ ] Secret user creado
- [ ] Campo `dbname` incluido
- [ ] Rotación automática habilitada
- [ ] Secrets accesibles vía CLI/SDK

---

## 6. IAM ROLES DEL TENANT

### 6.1 Crear TenantRole-repsol-admin

1. **IAM Console** → **Roles** → **Create role**

2. **Trusted entity type:** Custom trust policy

3. **Trust policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": [
        "arn:aws:iam::ACCOUNT_ID:role/Cognito_sybol_Auth_Role",
        "arn:aws:iam::ACCOUNT_ID:role/service-role/businesslogic-role-xxxxx",
        "arn:aws:iam::ACCOUNT_ID:role/service-role/propagate-role-xxxxx",
        "arn:aws:iam::ACCOUNT_ID:role/service-role/backoffice-role-xxxxx"
      ]
    },
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "aws:RequestedRegion": "eu-west-1"
      }
    }
  }]
}
```

⚠️ **Reemplazar:**
- `ACCOUNT_ID` con tu AWS Account ID
- `businesslogic-role-xxxxx` con ARN real (ver CORE_SETUP.md)
- `propagate-role-xxxxx` con ARN real (ver CORE_SETUP.md)
- `backoffice-role-xxxxx` con ARN real del rol del backoffice

4. **Next**

5. **Permissions:** No añadir policies aquí (se harán inline)

6. **Next**

7. **Role details:**
   ```
   Role name: TenantRole-repsol-admin
   Description: Admin role for tenant repsol - can access admin database and keys
   ```

8. **Create role**

### 6.2 Añadir Permissions Policy Inline

1. Click en rol recién creado → **Add permissions** → **Create inline policy**

2. **JSON:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecretsAccess",
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:eu-west-1:ACCOUNT_ID:secret:tenant/repsol/admin-password*"
    },
    {
      "Sid": "KMSAccess",
      "Effect": "Allow",
      "Action": [
        "kms:Sign",
        "kms:GetPublicKey",
        "kms:DescribeKey"
      ],
      "Resource": "arn:aws:kms:eu-west-1:ACCOUNT_ID:key/*",
      "Condition": {
        "StringEquals": {
          "kms:RequestAlias": "alias/tenant/repsol/admin-jwt"
        }
      }
    }
  ]
}
```

3. **Next**

4. **Policy name:** `TenantAccessPolicy-repsol-admin`

5. **Create policy**

**📝 Anotar:**
```
Role Name: TenantRole-repsol-admin
Role ARN: arn:aws:iam::ACCOUNT_ID:role/TenantRole-repsol-admin
```

### 6.3 Crear TenantRole-repsol-reader

Repetir pasos 6.1 y 6.2 pero con:
- **Role name:** `TenantRole-repsol-reader`
- **Secrets resource:** `tenant/repsol/reader-password*`
- **KMS condition:** `alias/tenant/repsol/reader-jwt`
- **Policy name:** `TenantAccessPolicy-repsol-reader`

✅ **Checkpoint IAM:**
- [ ] TenantRole-repsol-admin creado
- [ ] TenantRole-repsol-reader creado
- [ ] Trust policies configuradas (Cognito, businessLogic, propagate)
- [ ] Permissions policies inline configuradas
- [ ] Roles pueden ser asumidos por businessLogic

### 6.4 Añadir EventBridge Permissions (Cross-Tenant Communication)

⚠️ **Requisito:** EventBridge infrastructure debe estar configurada (ver CORE_SETUP.md sección 8).

Esta política permite al tenant enviar eventos cross-tenant al bus compartido.

1. En **TenantRole-repsol-admin** → **Add permissions** → **Create inline policy**

2. **JSON:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPutEventsToBus",
      "Effect": "Allow",
      "Action": ["events:PutEvents"],
      "Resource": "arn:aws:events:eu-west-1:ACCOUNT_ID:event-bus/cross-tenant-event-bus"
    }
  ]
}
```

3. **Reemplazar** `ACCOUNT_ID` con tu AWS Account ID

4. **Policy name:** `EventBridgeCrossTenantAccess`

5. **Create policy**

6. **Repetir para TenantRole-repsol-reader** (misma política)

**📝 Anotar:**
```
EventBridge Bus ARN: arn:aws:events:eu-west-1:ACCOUNT_ID:event-bus/cross-tenant-event-bus
Inline Policy añadida: EventBridgeCrossTenantAccess
```

**Automatización (opcional):**

```bash
# Admin role
aws iam put-role-policy \
  --role-name TenantRole-repsol-admin \
  --policy-name EventBridgeCrossTenantAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "AllowPutEventsToBus",
      "Effect": "Allow",
      "Action": ["events:PutEvents"],
      "Resource": "arn:aws:events:eu-west-1:ACCOUNT_ID:event-bus/cross-tenant-event-bus"
    }]
  }'

# Reader role
aws iam put-role-policy \
  --role-name TenantRole-repsol-reader \
  --policy-name EventBridgeCrossTenantAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "AllowPutEventsToBus",
      "Effect": "Allow",
      "Action": ["events:PutEvents"],
      "Resource": "arn:aws:events:eu-west-1:ACCOUNT_ID:event-bus/cross-tenant-event-bus"
    }]
  }'
```

⚠️ **Reemplazar** `ACCOUNT_ID` en los comandos.

✅ **Checkpoint IAM:**
- [ ] TenantRole-repsol-admin creado
- [ ] TenantRole-repsol-reader creado
- [ ] Trust policies configuradas (Cognito, businessLogic, propagate)
- [ ] Permissions policies inline configuradas
- [ ] EventBridge permissions añadidas (admin y reader)
- [ ] S3 batch-imports permissions añadidas (admin)
- [ ] Roles pueden ser asumidos por businessLogic

---

### 6.5 Añadir Permisos S3 Batch Import al Tenant Admin

⚠️ **Requisito:** El bucket `sybol-data-{env}` debe estar creado (ver CORE_SETUP.md sección 9.1).

El role `TenantRole-repsol-admin` (asumido por la Lambda `businessLogic` cuando actúa en nombre del tenant) necesita permiso para subir ficheros Excel al prefijo propio del tenant. El frontend obtiene credenciales temporales con este role vía Cognito Identity Pool y hace el PUT directamente a S3.

**La restricción por prefijo en la policy garantiza aislamiento cross-tenant**: el role de repsol solo puede escribir en `repsol/batch-imports/*`, nunca en el prefijo de otro tenant.

1. En **TenantRole-repsol-admin** → **Add permissions** → **Create inline policy**

2. **JSON** (reemplazar `ACCOUNT_ID`, `ENV` y `repsol`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BatchImportUpload",
      "Effect": "Allow",
      "Action": ["s3:PutObject"],
      "Resource": "arn:aws:s3:::sybol-data-{env}/repsol/batch-imports/*"
    }
  ]
}
```

3. **Policy name:** `S3BatchImportPolicy-repsol`

4. **Create policy**

**Automatización (AWS CLI):**

```bash
ENV=staging   # cambiar a prod en producción
TENANT=repsol

aws iam put-role-policy \
  --role-name TenantRole-${TENANT}-admin \
  --policy-name S3BatchImportPolicy-${TENANT} \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "S3BatchImportUpload",
      "Effect": "Allow",
      "Action": ["s3:PutObject"],
      "Resource": "arn:aws:s3:::sybol-data-'${ENV}'/'${TENANT}'/batch-imports/*"
    }]
  }'

echo "S3 batch import policy añadida a TenantRole-${TENANT}-admin"
```

**📝 Anotar:**
```
Role: TenantRole-repsol-admin
Policy añadida: S3BatchImportPolicy-repsol
Permisos: s3:PutObject en sybol-data-{env}/repsol/batch-imports/*
```

---

### 6.6 ⚠️ CONFIGURACIÓN ESPECIAL PARA TENANT SYBOL

El tenant **sybol** tiene requisitos especiales debido al servicio **backoffice**, que permite gestionar DID Documents de usuarios del sistema.

#### **Contexto**

El servicio backoffice necesita:
- **Lectura general** de datos: usuario `backoffice` (configurado en variables de entorno Lambda)
- **Escritura en `did_documents`**: usuario `sybol_admin` (usuario admin del tenant sybol vía Secrets Manager)

Este usuario admin del tenant sybol permite que cuando un usuario autenticado del tenant sybol llame al endpoint `POST /api/bo/did-document` con `x-id-token`, el servicio pueda escribir en la tabla `did_documents` de la base de datos del tenant sybol.

📘 **Ver:** [CORE_SETUP.md - Sección 6.3.1](./CORE_SETUP.md#6-3-1-configurar-usuarios-de-base-de-datos-para-backoffice) para detalles de la arquitectura de acceso dual del servicio backoffice.

---

#### **6.5.1 Otorgar Permisos al Usuario Admin del Tenant Sybol**

⚠️ **IMPORTANTE:** NO se crea un nuevo usuario. Se otorgan permisos al usuario **admin existente** del tenant sybol (`sybol_admin`).

1. **Conectar a la base de datos `backoffice`:**

```bash
psql -h <RDS_ENDPOINT> -U admin -d backoffice
```

2. **Ejecutar script SQL:**

```bash
# Desde la raíz del repositorio
psql -h <RDS_ENDPOINT> -U admin -d backoffice \
  -f v1/services/backoffice/database/setup_sybol_tenant_user.sql
```

3. **Verificar permisos:**

```sql
-- Comprobar que el usuario tiene los permisos correctos
\dp did_documents
\dp kyb_verifications

-- Debe mostrar:
-- did_documents: sybol_admin = arwdDxt (INSERT/UPDATE/DELETE)
-- kyb_verifications: sybol_admin = r (SELECT only)
```

📄 **Script ubicación:** `v1/services/backoffice/database/setup_sybol_tenant_user.sql`

---

#### **6.5.2 Crear Secret en Secrets Manager**

1. **AWS Console** → **Secrets Manager** → **Store a new secret**

2. **Secret type:** Other type of secret

3. **Key/value pairs:**

```json
{
  "username": "sybol_admin",
  "password": "PASSWORD_DEL_TENANT_ADMIN",
  "host": "CLUSTER_ENDPOINT.eu-west-1.rds.amazonaws.com",
  "port": 5432
}
```

⚠️ **IMPORTANTE:**
- **NO incluir `dbname` en el secret**
- Usar el **secret existente** `tenant/sybol/admin-password` (ya creado al configurar el tenant sybol)
- El secret contiene las credenciales del usuario `sybol_admin`
- El nombre de la base de datos se configura mediante variable de entorno **`DB_NAME=tenant_sybol`** en la Lambda backoffice
- Esta variable debe configurarse al desplegar la Lambda

⚠️ **Nota:** No es necesario crear un nuevo secret. El secret `tenant/sybol/admin-password` ya existe.

4. **Encryption key:** aws/secretsmanager (default)

5. **Next**

6. **Secret name:** `tenant/sybol/admin-password`

   ⚠️ **IMPORTANTE:** 
   - Este secret **YA EXISTE** (fue creado al configurar el tenant sybol en la sección 5)
   - Solo necesitas verificar que contiene las credenciales de `sybol_admin`
   - **NO crear un nuevo secret**

7. **Verificar que el secret existe:**

```bash
aws secretsmanager get-secret-value \
  --secret-id tenant/sybol/admin-password \
  --query 'SecretString' --output text | jq .
```

**📝 Anotar:**
```
Secret ARN: arn:aws:secretsmanager:eu-west-1:ACCOUNT_ID:secret:tenant/sybol/admin-password-XXXXXX
```

---

#### **6.5.3 Configurar IAM Role TenantRole-sybol-admin**

El rol `TenantRole-sybol-admin` (creado en sección 6.1) necesita permisos para acceder a este secret.

1. **IAM Console** → **Roles** → Buscar `TenantRole-sybol-admin`

2. **Verificar Trust Policy** (debe incluir rol de backoffice):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": [
        "arn:aws:iam::ACCOUNT_ID:role/Cognito_sybol_Auth_Role",
        "arn:aws:iam::ACCOUNT_ID:role/service-role/businesslogic-role-xxxxx",
        "arn:aws:iam::ACCOUNT_ID:role/service-role/propagate-role-xxxxx",
        "arn:aws:iam::ACCOUNT_ID:role/service-role/backoffice-role-xxxxx"
      ]
    },
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "aws:RequestedRegion": "eu-west-1"
      }
    }
  }]
}
```

3. **Verificar Inline Policy** `TenantAccessPolicy-sybol-admin` (debe incluir el secret):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecretsAccess",
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:eu-west-1:ACCOUNT_ID:secret:tenant/sybol/admin-password*"
    },
    {
      "Sid": "KMSAccess",
      "Effect": "Allow",
      "Action": [
        "kms:Sign",
        "kms:GetPublicKey",
        "kms:DescribeKey"
      ],
      "Resource": "arn:aws:kms:eu-west-1:ACCOUNT_ID:key/*",
      "Condition": {
        "StringEquals": {
          "kms:RequestAlias": "alias/tenant/sybol/admin-jwt"
        }
      }
    }
  ]
}
```

✅ Si ya está configurado correctamente, no requiere modificaciones.

---

#### **6.5.4 Flujo de Autenticación Backoffice → Tenant Sybol**

```
┌─────────────────┐
│ Usuario Cliente │
│ (tenant sybol)  │
└────────┬────────┘
         │ x-id-token (JWT firmado con KMS)
         ▼
┌─────────────────────────────────────────┐
│ Lambda: backoffice                       │
│ ┌─────────────────────────────────────┐ │
│ │ authMiddleware.requireIdToken       │ │
│ │ - Valida JWT                        │ │
│ │ - Extrae tenantId = "sybol"        │ │
│ │ - AssumeRole → TenantRole-sybol-admin│ │
│ └──────────────┬──────────────────────┘ │
│                ▼                          │
│ ┌─────────────────────────────────────┐ │
│ │ lib/tenantDatabase.getConnection    │ │
│ │ - GetSecretValue(tenant/sybol/admin)│ │
│ │ - Credenciales: sybol_admin         │ │
│ │ - Pool PostgreSQL                   │ │
│ └──────────────┬──────────────────────┘ │
│                ▼                          │
│ ┌─────────────────────────────────────┐ │
│ │ repositories/didDocumentRepository  │ │
│ │ - INSERT INTO did_documents         │ │
│ │ - PERMITIDO ✅                       │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ RDS PostgreSQL - backoffice             │
│ - Usuario: sybol_admin                  │
│ - Tabla: did_documents (INSERT/UPDATE)  │
└─────────────────────────────────────────┘
```

**Endpoints afectados:**
- ✅ `POST /api/bo/did-document` → **Requiere** x-id-token → Escribe en did_documents
- ℹ️ `GET /api/bo/did-document/:id` → Opcional x-id-token → Lee desde BD general o tenant
- ℹ️ `GET /api/bo/kyb-verifications` → Opcional x-id-token → Lee desde BD general o tenant

---

#### **6.5.5 Testing**

1. **Test 1: Conexión desde backoffice Lambda**

```bash
# Configurar AWS CLI con credenciales temporales del rol TenantRole-sybol-admin
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/TenantRole-sybol-admin \
  --role-session-name test-backoffice

# Obtener secret
aws secretsmanager get-secret-value \
  --secret-id tenant/sybol/admin-password \
  --query 'SecretString' --output text | jq .

# Debe retornar las credenciales de sybol_tenant_writer
```

2. **Test 2: Inserción en did_documents**

```bash
# Conectar con el usuario sybol_admin
psql -h <RDS_ENDPOINT> -U sybol_admin -d backoffice

# Intentar INSERT en did_documents
INSERT INTO did_documents (id, did, document, created_at, updated_at) 
VALUES ('test-id', 'did:sybol:test', '{}', NOW(), NOW());

-- Debe ejecutarse correctamente ✅
```

3. **Test 3: Restricción en kyb_verifications**

```bash
# Misma conexión
INSERT INTO kyb_verifications (id, status, created_at) 
VALUES ('test-kyb', 'pending', NOW());

-- Debe FALLAR con: ERROR: permission denied for table kyb_verifications ❌
```

---

#### **Checkpoint 6.5 - Configuración Especial Sybol**

- [ ] Usuario `sybol_admin` tiene permisos en base de datos `backoffice`
- [ ] Permisos verificados: INSERT/UPDATE did_documents ✅, SELECT kyb_verifications ✅
- [ ] Secret `tenant/sybol/admin-password` existe y contiene credenciales correctas
- [ ] IAM Role `TenantRole-sybol-admin` tiene acceso al secret
- [ ] Trust policy incluye rol `backoffice-role-xxxxx`
- [ ] Test de inserción en did_documents exitoso
- [ ] Test de restricción en kyb_verifications exitoso

📘 **Referencia cruzada:** Esta configuración está sincronizada con [CORE_SETUP.md - Sección 6.3.1](./CORE_SETUP.md#6-3-1-configurar-usuarios-de-base-de-datos-para-backoffice).

## 7. KMS KEYS

### 7.1 Crear KMS Key Admin

1. **KMS Console** → **Customer managed keys** → **Create key**

2. **Configure key:**
   ```
   Key type: Asymmetric
   Key usage: Sign and verify
   Key spec: ECC_NIST_P256
   ```

3. **Labels:**
   ```
   Alias: tenant/repsol/admin-jwt
   Description: JWT signing key for tenant repsol admin role
   ```

4. **Key administrators:** Tu usuario AWS admin

5. **Key users:** ⚠️ Dejar vacío (configuramos por policy)

6. **Review and create**

**📝 Anotar:**
```
Key ID: 12345678-1234-1234-1234-123456789012
Key ARN: arn:aws:kms:eu-west-1:ACCOUNT_ID:key/12345678-1234-1234-1234-123456789012
Alias: alias/tenant/repsol/admin-jwt
```

### 7.2 Configurar Key Policy Admin

1. Click en key → **Key policy** → **Edit**

2. **Key policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "KeyAdministration",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:user/tu-usuario-admin"
      },
      "Action": [
        "kms:Create*",
        "kms:Describe*",
        "kms:Enable*",
        "kms:List*",
        "kms:Put*",
        "kms:Update*",
        "kms:Revoke*",
        "kms:Disable*",
        "kms:Get*",
        "kms:Delete*",
        "kms:ScheduleKeyDeletion",
        "kms:CancelKeyDeletion"
      ],
      "Resource": "*"
    },
    {
      "Sid": "TenantSpecificAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:role/TenantRole-repsol-admin"
      },
      "Action": [
        "kms:Sign",
        "kms:GetPublicKey",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    }
  ]
}
```

3. **Save changes**

### 7.3 Extraer Public Key

```bash
aws kms get-public-key \
  --key-id alias/tenant/repsol/admin-jwt \
  --region eu-west-1 \
  --output text \
  --query 'PublicKey' | base64 -d > repsol_admin_public.der

# Convertir a PEM
openssl ec -pubin -inform DER -in repsol_admin_public.der -outform PEM -out repsol_admin_public.pem

# Ver contenido
cat repsol_admin_public.pem
```

**Salida esperada:**
```
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
-----END PUBLIC KEY-----
```

**📝 Guardar este public key para el DID document (siguiente paso).**

### 7.4 Crear KMS Key Reader

Repetir pasos 7.1, 7.2, 7.3 pero con:
- **Alias:** `tenant/repsol/reader-jwt`
- **Description:** JWT signing key for tenant repsol reader role
- **Key policy Principal:** `TenantRole-repsol-reader`

### 7.5 Verificar KMS Access

```bash
# Test desde CLI con tenant role
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/TenantRole-repsol-admin \
  --role-session-name test-session

# Usar credenciales temporales
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...

# Test sign
echo "test message" | aws kms sign \
  --key-id alias/tenant/repsol/admin-jwt \
  --message fileb:///dev/stdin \
  --message-type RAW \
  --signing-algorithm ECDSA_SHA_256

# Debe funcionar sin error
```

✅ **Checkpoint KMS:**
- [ ] KMS key admin creada (ECC_NIST_P256)
- [ ] KMS key reader creada
- [ ] Aliases configurados
- [ ] Key policies restringen acceso
- [ ] Public keys extraídas
- [ ] Tenant roles pueden firmar

---

## 8. DID DOCUMENT

> **Método:** `did:web` (W3C-CCG) — resolución pública sin infraestructura adicional.
> El DID es **determinístico por tenant**: `did:web:did.develop.sybol.id:tenants:{tenantId}`
> No se genera ningún UUID — el tenant ID es el identificador permanente.

### 8.1 Formato del DID

```
did:web:did.develop.sybol.id:tenants:{tenantId}
```

**Resolución pública (spec §2.5.2):**
```
GET https://did.develop.sybol.id/tenants/{tenantId}/did.json
```

El documento devuelto es el DID document W3C. **No contiene** businessName ni CIF — esos datos se sirven desde el endpoint autenticado `GET /api/bo/entities/{tenantId}`.

### 8.2 Registrar DID Document en Backoffice

El DID document se crea al dar de alta el tenant. El `did` se deriva automáticamente del `tenant` — no es necesario generar UUIDs.

```bash
curl -X POST https://backoffice.develop.sybol.id/api/bo/did-document \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT" \
  -H "x-id-token: $ID_TOKEN" \
  -d '{
    "tenant": "repsol",
    "initialPublicKey": {
      "id": "5a38b335-69ff-43a2-92ef-eaf9e12cf6b6",
      "algorithm": "ECC_NIST_P256",
      "publicKey": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----"
    },
    "service": [
      {
        "id": "did:web:did.develop.sybol.id:tenants:repsol#propagate",
        "type": "SybolPropagateService",
        "serviceEndpoint": "https://api.develop.wallet.sybol.id/api/ps/receive"
      }
    ]
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "did": "did:web:did.develop.sybol.id:tenants:repsol",
  "message": "DID document created successfully"
}
```

> El campo `entity` (businessName/CIF) se registra por separado en el paso 8.3.

### 8.3 Registrar Perfil de Entidad (businessName / CIF)

Los datos privados de la entidad se almacenan en la tabla `entities` del backoffice. Este endpoint **requiere autenticación**.

```bash
curl -X PUT https://backoffice.develop.sybol.id/api/bo/entities/repsol \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT" \
  -H "x-id-token: $ID_TOKEN" \
  -d '{
    "businessName": "RESPOL S.L.",
    "cif": "12345678Z"
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "Entity profile saved successfully",
  "data": {
    "tenant": "repsol",
    "businessName": "RESPOL S.L.",
    "cif": "12345678Z"
  }
}
```

> ℹ️ Ver `entities2.json` en la raíz del repositorio para los bodies de los 3 tenants actuales.

### 8.4 Verificar Resolución Pública del DID

```bash
# Sin autenticación — accesible por cualquier resolver externo
curl https://did.develop.sybol.id/tenants/repsol/did.json
```

**Respuesta esperada:**
```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/jws-2020/v1"
  ],
  "id": "did:web:did.develop.sybol.id:tenants:repsol",
  "verificationMethod": [
    {
      "id": "did:web:did.develop.sybol.id:tenants:repsol#5a38b335-69ff-43a2-92ef-eaf9e12cf6b6",
      "type": "ECC_NIST_P256",
      "controller": "did:web:did.develop.sybol.id:tenants:repsol",
      "publicKey": "-----BEGIN PUBLIC KEY-----\nMFkw...\n-----END PUBLIC KEY-----"
    }
  ],
  "authentication": [
    "did:web:did.develop.sybol.id:tenants:repsol#5a38b335-69ff-43a2-92ef-eaf9e12cf6b6"
  ],
  "service": [
    {
      "id": "did:web:did.develop.sybol.id:tenants:repsol#propagate",
      "type": "SybolPropagateService",
      "serviceEndpoint": "https://api.develop.wallet.sybol.id/api/ps/receive"
    },
    {
      "id": "did:web:did.develop.sybol.id:tenants:repsol#entity-profile",
      "type": "EntityProfileService",
      "serviceEndpoint": "/api/bo/entities/repsol"
    }
  ]
}
```

```bash
# Verificar cabecera CORS (obligatoria por spec did:web)
curl -I https://did.develop.sybol.id/tenants/repsol/did.json | grep -i access-control
# Esperado: access-control-allow-origin: *
```

### 8.5 Verificar Perfil de Entidad (autenticado)

```bash
curl https://backoffice.develop.sybol.id/api/bo/entities/repsol \
  -H "Authorization: Bearer $JWT" \
  -H "x-id-token: $ID_TOKEN"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "tenant": "repsol",
    "businessName": "RESPOL S.L.",
    "cif": "12345678Z"
  }
}
```

**📝 Anotar:**
```
DID:            did:web:did.develop.sybol.id:tenants:repsol
DID público:    https://did.develop.sybol.id/tenants/repsol/did.json
Key ID:         did:web:did.develop.sybol.id:tenants:repsol#5a38b335-69ff-43a2-92ef-eaf9e12cf6b6
KMS Key ARN:    arn:aws:kms:eu-west-1:ACCOUNT_ID:key/...
```

✅ **Checkpoint DID:**
- [ ] DID document creado en backoffice (`POST /api/bo/did-document`)
- [ ] Perfil de entidad creado en backoffice (`PUT /api/bo/entities/:tenantId`)
- [ ] Resolución pública funciona sin auth (`curl https://did.develop.sybol.id/tenants/{tenant}/did.json`)
- [ ] Cabecera CORS `Access-Control-Allow-Origin: *` presente en la respuesta pública
- [ ] `authentication` contiene referencias absolutas (no `#key-uuid` relativo)
- [ ] `id` del DID document coincide con el DID solicitado
- [ ] `EntityProfileService` present en el array `service`

---

## 9. DESPLIEGUE FRONTEND

### 9.1 Configurar Frontend para Tenant

#### **Variables de entorno:**

Crear archivo `.env.production` en `v1/wwc/`:

```bash
REACT_APP_TENANT_ID=repsol
REACT_APP_AWS_REGION=eu-west-1
REACT_APP_COGNITO_USER_POOL_ID=eu-west-1_XXXXXXXXX
REACT_APP_COGNITO_APP_CLIENT_ID=1234567890abcdefghij
REACT_APP_IDENTITY_POOL_ID=eu-west-1:aaaa-bbbb-cccc-dddd-eeee
REACT_APP_API_BASE_URL=https://api.sybol.id
REACT_APP_BACKOFFICE_API_URL=https://backoffice.sybol.id
```

#### **Branding (Opcional):**

Personalizar look & feel del tenant:
- Logo: `src/assets/tenants/repsol/logo.png`
- Colores: `src/themes/repsol.js`
- Favicon: `public/tenants/repsol/favicon.ico`

### 9.2 Build Frontend

```bash
cd v1/wwc

# Install dependencies
npm install

# Build para producción
npm run build

# Output en: build/
```

### 9.3 Deploy a S3

```bash
# Sincronizar build con S3
aws s3 sync build/ s3://repsol-staging-wallet-frontend/ \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "index.html" \
  --exclude "service-worker.js"

# index.html sin cache (SPA routing)
aws s3 cp build/index.html s3://repsol-staging-wallet-frontend/index.html \
  --cache-control "no-cache, no-store, must-revalidate"
```

### 9.4 Invalidar CloudFront Cache

```bash
aws cloudfront create-invalidation \
  --distribution-id E123456789ABCD \
  --paths "/*"
```

⏱️ Tarda 1-3 minutos.

### 9.5 Verificar Despliegue

1. **Abrir:** `https://repsol.staging.wallet.sybol.id`

2. **Verificar:**
   - [ ] HTTPS funcionando (certificado válido)
   - [ ] Página carga correctamente
   - [ ] Logo y branding correcto
   - [ ] Login redirect a Cognito

3. **Test login:**
   - Usuario: `usuario@repsol.com`
   - Password: [La que configuraste]
   - Debe redirigir al dashboard

✅ **Checkpoint Frontend:**
- [ ] Build compilado sin errores
- [ ] Deploy a S3 exitoso
- [ ] CloudFront invalidado
- [ ] HTTPS funcionando
- [ ] Aplicación accesible
- [ ] Login funciona
- [ ] API calls exitosas

---

## ✅ CHECKLIST FINAL

### Infraestructura:
- [ ] Dominio `{tenant}.staging.wallet.sybol.id` creado
- [ ] Certificado ACM emitido y validado
- [ ] CloudFront distribution desplegada
- [ ] S3 bucket creado y configurado
- [ ] Route 53 apuntando a CloudFront

### Identidad y Acceso:
- [ ] Usuario(s) en Cognito con custom attributes
- [ ] Custom attributes tenant_id y role correctos
- [ ] Usuario puede hacer login

### Base de Datos:
- [ ] Database `tenant_{tenant}` creada
- [ ] Usuarios PostgreSQL `{tenant}_admin` y `{tenant}_reader`
- [ ] Schemas ejecutados
- [ ] Tablas creadas
- [ ] Permisos configurados (admin, reader, propagate_system)

### Secrets:
- [ ] Secret `tenant/{tenant}/admin-password`
- [ ] Secret `tenant/{tenant}/reader-password`
- [ ] Campo database configurado
- [ ] Rotación automática habilitada

### IAM:
- [ ] `TenantRole-{tenant}-admin` creado
- [ ] `TenantRole-{tenant}-reader` creado
- [ ] Trust policies (Cognito, businessLogic, propagate)
- [ ] Permissions policies (Secrets, KMS)

### KMS:
- [ ] Keys asimétricas ECC_NIST_P256
- [ ] Aliases `tenant/{tenant}/{role}-jwt`
- [ ] Key policies configuradas
- [ ] Public keys extraídas

### DID:
- [ ] DID generado
- [ ] DID document registrado en backoffice
- [ ] DID verificable públicamente
- [ ] kmsKeyId y tenant correctos

### Frontend:
- [ ] Build compilado
- [ ] Deploy a S3
- [ ] Aplicación accesible vía HTTPS
- [ ] Login funcional

---

## 🧪 PRUEBA END-TO-END

### Test 1: Login y JWT

```bash
# 1. Login como usuario
curl -X POST https://cognito-idp.eu-west-1.amazonaws.com/ \
  -H "X-Amz-Target: AWSCognitoIdentityProviderService.InitiateAuth" \
  -H "Content-Type: application/x-amz-json-1.1" \
  -d '{
    "AuthFlow": "USER_PASSWORD_AUTH",
    "ClientId": "1234567890abcdefghij",
    "AuthParameters": {
      "USERNAME": "usuario@repsol.com",
      "PASSWORD": "password123"
    }
  }'

# 2. Obtener IdToken del response

# 3. Decodificar JWT (jwt.io)
# Verificar claims:
#   "custom:tenant_id": "repsol"
#   "custom:role": "admin"
```

### Test 2: Crear Credential

```bash
curl -X POST https://api.sybol.id/api/bl/credentials \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "credentialSubject": {
      "name": "John Doe",
      "email": "john@repsol.com"
    }
  }'
```

**Verificar:**
- [ ] Credential creado exitosamente
- [ ] JWT firmado con KMS key del tenant
- [ ] Credential almacenado en `tenant_repsol` database
- [ ] Solo usuarios de tenant "repsol" pueden acceder

### Test 3: Aislamiento de Tenants

```bash
# Login como usuario de OTRO tenant
curl -X POST https://api.sybol.id/api/bl/credentials \
  -H "Authorization: Bearer OTHER_TENANT_TOKEN" \
  -H "Content-Type: application/json"

# Debe fallar: 403 Forbidden
```

---

## 🚨 TROUBLESHOOTING

### Error: "CloudFront 403 Forbidden"
- **Causa:** S3 bucket policy no permite CloudFront OAI
- **Solución:** Verificar bucket policy (paso 2.3)

### Error: "Certificate not valid"
- **Causa:** Certificado ACM en región incorrecta
- **Solución:** CloudFront requiere certificados en us-east-1

### Error: "Failed to assume role"
- **Causa:** Trust relationship incorrecto
- **Solución:** Verificar ARNs exactos en trust policy (paso 6.1)

### Error: "Access denied to KMS key"
- **Causa:** Key policy o IAM permissions incorrectos
- **Solución:** Verificar key policy (paso 7.2) y IAM inline policy (paso 6.2)

### Error: "Database connection failed"
- **Causa:** Secret name incorrecto o campo database faltante
- **Solución:** Verificar secret format (paso 5.1) y database field

### Error: "DID not found"
- **Causa:** DID no registrado o tenant field incorrecto
- **Solución:** Verificar DID en backoffice (paso 8.4)

### Error: "Invalid JWT signature"
- **Causa:** KMS key ID incorrecto en DID document
- **Solución:** Verificar kmsKeyId matches KMS key ARN (paso 8.2)

---

## 📋 PLANTILLA DE VARIABLES

```bash
# CONFIGURACIÓN DEL TENANT
TENANT_ID="repsol"
AWS_ACCOUNT_ID="123456789012"
AWS_REGION="eu-west-1"

# DOMINIO
DOMAIN="${TENANT_ID}.staging.wallet.sybol.id"

# S3 Y CLOUDFRONT
S3_BUCKET="${TENANT_ID}-staging-wallet-frontend"
CLOUDFRONT_DIST_ID="E123456789ABCD"

# COGNITO
USER_EMAIL="usuario@${TENANT_ID}.com"
USER_POOL_ID="eu-west-1_XXXXXXXXX"
APP_CLIENT_ID="1234567890abcdefghij"

# DATABASE
DB_NAME="tenant_${TENANT_ID}"
ADMIN_USER="${TENANT_ID}_admin"
READER_USER="${TENANT_ID}_reader"

# SECRETS
ADMIN_SECRET="tenant/${TENANT_ID}/admin-password"
READER_SECRET="tenant/${TENANT_ID}/reader-password"

# IAM ROLES
ADMIN_ROLE="TenantRole-${TENANT_ID}-admin"
READER_ROLE="TenantRole-${TENANT_ID}-reader"

# KMS
ADMIN_KMS_ALIAS="alias/tenant/${TENANT_ID}/admin-jwt"
READER_KMS_ALIAS="alias/tenant/${TENANT_ID}/reader-jwt"

# DID
DID="did:sybol:$(uuidgen | tr '[:upper:]' '[:lower:]')"
KEY_ID="${DID}#$(uuidgen | tr '[:upper:]' '[:lower:]')"
```

---
