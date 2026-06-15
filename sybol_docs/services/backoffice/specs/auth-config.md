# Configuración de Autenticación - Backoffice API

## Resumen

El servicio backoffice implementa un sistema de **autenticación multi-tenant** donde algunos endpoints pueden usar bases de datos específicas del tenant mediante credenciales STS de AWS.

---

## Tipos de Autenticación

### 🔴 **REQUERIDA** (requireIdToken)
- **Header obligatorio**: `x-id-token` 
- **Comportamiento**: Valida token, obtiene credenciales STS, conecta a BD del tenant
- **Flujo**:
  1. Valida `x-id-token` (JWT de Cognito)
  2. Extrae `custom:tenant_id` y `custom:role` del token
  3. Obtiene credenciales STS vía `AssumeRole` (IAM role: `TenantRole-{tenantId}-{role}`)
  4. Recupera config de BD desde AWS Secrets Manager (`tenant/{tenantId}/{role}-password`)
  5. Conecta a base de datos específica del tenant
  6. Ejecuta operación

### 🟢 **OPCIONAL** (optionalIdToken)
- **Header opcional**: `x-id-token`
- **Comportamiento**:
  - **CON token**: Usa BD del tenant (flujo igual a requerida)
  - **SIN token**: Usa BD general (config.js con variables de entorno)

---

## Endpoints por Tipo

### 🔴 Requieren x-id-token (BD tenant)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/bo/did-document` | Crear documento DID |

**Razón**: La creación de DIDs debe estar aislada por tenant para seguridad y compliance.

---

### 🟢 x-id-token Opcional (BD tenant o general)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/bo/did-document/:did` | Obtener DID por identificador |
| `GET` | `/api/bo/did-document` | Listar DIDs con filtros |
| `POST` | `/api/bo/did-document/:did` | Actualizar documento DID |
| `DELETE` | `/api/bo/did-document/:did` | Eliminar documento DID |
| `POST` | `/api/bo/kyb` | Generar token KYB |
| `GET` | `/api/bo/kyb` | Obtener estado KYB |

**Razón**: Operaciones de lectura/actualización pueden usar BD general para acceso cross-tenant (admin) o BD tenant para acceso aislado.

---

### ⚪ Sin autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/bo/health` | Health check |
| `POST` | `/api/bo/kyb/webhook` | Webhook Sumsub |

---

## Configuración de Base de Datos

### BD General (config.js)
```javascript
database: {
  host: process.env.SYBOL_DB_HOST,
  port: process.env.SYBOL_DB_PORT,
  user: process.env.SYBOL_DB_USER,
  password: process.env.SYBOL_DB_PASSWORD,
  database: process.env.SYBOL_DB_NAME,
  ssl: process.env.SYBOL_DB_SSL === 'true'
}
```

### BD Tenant (AWS Secrets Manager)
**Secret ID**: `tenant/{tenantId}/{userRole}-password`

**Formato del secret**:
```json
{
  "username": "tenant_user",
  "password": "tenant_password",
  "host": "tenant-db.region.rds.amazonaws.com",
  "port": 5432,
  "dbname": "tenant_database"
}
```

---

## Flujo de req.auth

### Con requireIdToken (obligatorio)
```javascript
req.auth = {
  idToken: "eyJhbGciOiJSUzI1...",
  tenantId: "tenant-001",
  userRole: "admin",
  stsCredentials: {
    AccessKeyId: "ASIA...",
    SecretAccessKey: "...",
    SessionToken: "...",
    Expiration: "2026-02-05T..."
  },
  awsCredentials: {
    accessKeyId: "ASIA...",
    secretAccessKey: "...",
    sessionToken: "..."
  }
}
```

### Con optionalIdToken (si se provee token)
```javascript
req.auth = { ... } // Igual que requireIdToken
```

### Con optionalIdToken (sin token)
```javascript
req.auth = null // Usa BD general
```

---

## Implementación en Código

### Routes (did-document.routes.js)
```javascript
const { requireIdToken, optionalIdToken } = require('../middleware/authMiddleware');

// REQUIERE x-id-token
router.post('/', requireIdToken, didDocumentController.createDidDocument);

// OPCIONAL x-id-token
router.get('/', optionalIdToken, didDocumentController.getAllDidDocuments);
router.get('/:did', optionalIdToken, didDocumentController.getDidDocumentByDid);
router.post('/:did', optionalIdToken, didDocumentController.updateDidDocument);
router.delete('/:did', optionalIdToken, didDocumentController.deleteDidDocument);
```

### Controller (did-document.controller.js)
```javascript
exports.createDidDocument = async (req, res) => {
  // Preparar tenantAuth desde req.auth
  const tenantAuth = req.auth ? {
    tenantId: req.auth.tenantId,
    userRole: req.auth.userRole,
    awsCredentials: req.auth.awsCredentials
  } : null;

  await didDocumentService.createDidDocument(did, tenant, key, entity, tenantAuth);
};
```

### Service (did-document.service.js)
```javascript
async createDidDocument(did, tenant, key, entity = null, tenantAuth = null) {
  await didDocumentRepository.createDidDocument(documentData, tenantAuth);
}
```

### Repository (did-document.repository.js)
```javascript
async createDidDocument(didDocument, tenantAuth = null) {
  let res;
  if (tenantAuth) {
    // Usar BD del tenant
    const client = await tenantDatabase.getConnection(
      tenantAuth.tenantId, 
      tenantAuth.userRole, 
      tenantAuth.awsCredentials
    );
    res = await client.query(query, values);
  } else {
    // Usar BD general
    res = await pool.query(query, values);
  }
}
```

---

## Arquitectura AWS

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ x-id-token (JWT)
       ↓
┌─────────────────┐
│  authMiddleware │
│  - validateToken│
│  - extractClaims│
└──────┬──────────┘
       │
       ↓
┌──────────────────┐
│ tenantSts        │
│ - AssumeRole     │──→ arn:aws:iam::ACCOUNT:role/TenantRole-{tenant}-{role}
└──────┬───────────┘
       │ STS Credentials
       ↓
┌─────────────────────┐
│ tenantDatabase      │
│ - getSecretValue    │──→ tenant/{tenantId}/{role}-password
│ - getConnection     │
└──────┬──────────────┘
       │
       ↓
┌─────────────────┐
│  Tenant DB      │
│  (PostgreSQL)   │
└─────────────────┘
```

---

## Archivos Clave

| Archivo | Descripción |
|---------|-------------|
| `middleware/authMiddleware.js` | requireIdToken, optionalIdToken |
| `lib/tenantStsCredentials/index.js` | AssumeRole con IAM |
| `lib/tenantDatabase.js` | Secrets Manager + PostgreSQL |
| `routes/did-document.routes.js` | Configuración de middlewares |
| `controllers/did-document.controller.js` | Preparación de tenantAuth |
| `repositories/did-document.repository.js` | Lógica de BD dual |

---

## Testing

### Crear DID (requiere token)
```bash
curl -X POST http://localhost:3000/api/bo/did-document \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "x-id-token: $ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant": "tenant-001",
    "initialPublicKey": { "id": "key-1", "algorithm": "ES256", "publicKey": "..." }
  }'
```

### Obtener DID (sin token - BD general)
```bash
curl -X GET http://localhost:3000/api/bo/did-document/did:sybol:123... \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Obtener DID (con token - BD tenant)
```bash
curl -X GET http://localhost:3000/api/bo/did-document/did:sybol:123... \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "x-id-token: $ID_TOKEN"
```

---

## Variables de Entorno Necesarias

```bash
# AWS
SYBOL_AWS_REGION=eu-west-1
SYBOL_AWS_ACCOUNT_ID=123456789012

# Base de datos general
SYBOL_DB_HOST=localhost
SYBOL_DB_PORT=5432
SYBOL_DB_USER=postgres
SYBOL_DB_PASSWORD=password
SYBOL_DB_NAME=backoffice_db
SYBOL_DB_SSL=false

# Cognito (para validación de tokens)
SYBOL_COGNITO_USER_POOL_ID=eu-west-1_XXXXXXX
SYBOL_COGNITO_REGION=eu-west-1
```

---

## Notas de Seguridad

1. **STS Session Duration**: 1 hora por defecto (configurable en AssumeRole)
2. **Connection Pooling**: Cacheo de conexiones por `{tenantId}-{userRole}`
3. **Secrets Rotation**: Compatible con AWS Secrets Manager rotation
4. **IAM Permissions**: Cada tenant role debe tener:
   - `secretsmanager:GetSecretValue` para su secret
   - `rds:Connect` para su base de datos
5. **Token Validation**: JWT validado contra Cognito User Pool

---

Generado: 2026-02-05
