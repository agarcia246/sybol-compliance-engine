# KMS Key Lifecycle — API Gateway Integration

Integración de las lambdas de gestión del ciclo de vida de claves KMS en el **WalletApi** (`13xxajdiae`).

---

## Resumen

Se exponen 4 tipos de clave criptográfica a través de la ruta `/api/kms/{keyType}`, securizadas con el autorizador JWT `WalletApiDev` (Cognito User Pool `eu-west-1_Lpg65AWPJ`).

El aislamiento por tenant se implementa en **dos capas independientes** (defensa en profundidad):

1. **Capa IAM (primaria):** cada lambda asume via STS el role `TenantKmsRole-{tenantId}` antes de operar. Ese role tiene condiciones IAM `aws:ResourceTag/tenantId` y `aws:RequestTag/tenantId` que bloquean a nivel de AWS cualquier operación sobre claves de otro tenant — incluso si hubiera un bug en el código.
2. **Capa de código (secundaria):** antes de query/delete, se verifica explícitamente el tag `tenantId` de la clave con `ListResourceTags`. Si no coincide con el JWT → 403 inmediato.

El `tenantId` se extrae **siempre del JWT** (`custom:tenant_id`, validado por el JWT authorizer de API GW) — nunca del body de la request.

| Key Type | Algoritmo | Uso |
|---|---|---|
| `ed25519` | ECC_NIST_EDWARDS25519 | Firmas Hedera DID |
| `p256` | ECC_NIST_P256 | Firmas ECDSA estándar |
| `secp256k1` | ECC_SECG_P256K1 | Firmas EVM/Ethereum |
| `rsa` | RSA (SIGN_VERIFY) | Firmas RSA |

---

## Endpoints

Base URL: `https://13xxajdiae.execute-api.eu-west-1.amazonaws.com`

Todos los endpoints requieren header: `Authorization: Bearer <cognito-jwt>`

### Crear clave

```
POST /api/kms/{keyType}
```

**Body:**
```json
{
  "tenantId": "string",
  "description": "string (opcional)",
  "tags": { "key": "value" }
}
```

**Respuesta 200:**
```json
{
  "success": true,
  "keyId": "mrk-abc123...",
  "keyArn": "arn:aws:kms:eu-west-1:111891094335:key/...",
  "keySpec": "ECC_NIST_EDWARDS25519"
}
```

### Listar claves del tenant

```
GET /api/kms/{keyType}
```

Devuelve todas las claves del tipo indicado pertenecientes al tenant del JWT. No requiere parámetros adicionales — el tenant se extrae del token.

**Respuesta 200:**
```json
{
  "success": true,
  "keys": [
    {
      "keyId": "mrk-abc123...",
      "keyArn": "arn:aws:kms:eu-west-1:111891094335:key/...",
      "keySpec": "ECC_NIST_EDWARDS25519",
      "description": "Hedera DID key - tenant sybol",
      "enabled": true,
      "creationDate": "2026-04-10T12:00:00Z"
    }
  ]
}
```

> **Nota:** solo aparecen claves creadas con la versión actual del código (que añade el tag `keyType` automáticamente). Las claves creadas antes de este cambio no tienen el tag `keyType` y no serán listadas.

### Consultar clave individual

```
GET /api/kms/{keyType}/{keyId}
```

**Respuesta 200:**
```json
{
  "success": true,
  "keyId": "mrk-abc123...",
  "keyArn": "arn:aws:kms:eu-west-1:111891094335:key/...",
  "keySpec": "ECC_NIST_EDWARDS25519",
  "publicKey": "<base64-encoded DER>",
  "enabled": true,
  "creationDate": "2026-04-10T..."
}
```

### Eliminar clave

```
DELETE /api/kms/{keyType}/{keyId}
```

Programa el borrado de la clave con un periodo de espera de **7 días** (política KMS).

**Respuesta 200:**
```json
{
  "success": true,
  "keyId": "mrk-abc123...",
  "deletionDate": "2026-04-17T..."
}
```

---

## Arquitectura

```
Cliente
  │
  │  Authorization: Bearer <JWT>
  ▼
API Gateway HTTP — WalletApi (13xxajdiae)
  │  Authorizer: WalletApiDev (JWT / Cognito eu-west-1_Lpg65AWPJ)
  │
  ├── POST   /api/kms/ed25519          ──► sybol-kms-key-ed25519-dev
  ├── GET    /api/kms/ed25519/{keyId}  ──► sybol-kms-key-ed25519-dev
  ├── DELETE /api/kms/ed25519/{keyId}  ──► sybol-kms-key-ed25519-dev
  │
  ├── POST   /api/kms/p256             ──► sybol-kms-key-p256-dev
  ├── GET    /api/kms/p256/{keyId}     ──► sybol-kms-key-p256-dev
  ├── DELETE /api/kms/p256/{keyId}     ──► sybol-kms-key-p256-dev
  │
  ├── POST   /api/kms/secp256k1        ──► sybol-kms-key-secp256k1-dev
  ├── GET    /api/kms/secp256k1/{keyId}──► sybol-kms-key-secp256k1-dev
  ├── DELETE /api/kms/secp256k1/{keyId}──► sybol-kms-key-secp256k1-dev
  │
  ├── POST   /api/kms/rsa              ──► sybol-kms-key-rsa-dev
  ├── GET    /api/kms/rsa/{keyId}      ──► sybol-kms-key-rsa-dev
  └── DELETE /api/kms/rsa/{keyId}      ──► sybol-kms-key-rsa-dev
```

---

## Recursos AWS

| Recurso | ID / Nombre |
|---|---|
| API Gateway | `WalletApi` — `13xxajdiae` |
| Authorizer | `WalletApiDev` — `7hizg9` |
| Cognito User Pool | `eu-west-1_Lpg65AWPJ` |
| Lambda ed25519 | `sybol-kms-key-ed25519-dev` |
| Lambda p256 | `sybol-kms-key-p256-dev` |
| Lambda secp256k1 | `sybol-kms-key-secp256k1-dev` |
| Lambda rsa | `sybol-kms-key-rsa-dev` |
| IAM Role (lambdas) | `sybol-kms-lambda-dev-role` |
| Región | `eu-west-1` |
| Cuenta | `111891094335` |

### Integraciones API GW → Lambda

| Key Type | Integration ID |
|---|---|
| `ed25519` | `lyb40zp` |
| `p256` | `40cspyq` |
| `secp256k1` | `x591tw4` |
| `rsa` | `0zv12r6` |

---

## Modelo de seguridad — Aislamiento por tenant

### Flujo por request

```
Cliente (JWT con custom:tenant_id = "tenant-a")
  │
  ▼
API GW JWT Authorizer (WalletApiDev)
  │  Valida el JWT contra Cognito — si inválido → 401
  │  Inyecta claims en event.requestContext.authorizer.jwt.claims
  ▼
Lambda handler
  │  Extrae tenantId de claims['custom:tenant_id']  ← no del body
  │  Si no hay tenantId en claims → 403
  ▼
getTenantKmsCredentials(tenantId)
  │  sts:AssumeRole → TenantKmsRole-tenant-a
  │  Si el role no existe (tenant no provisionado) → 500
  ▼
KMSClient con credenciales scopadas
  │  query/delete: ListResourceTags → verifica tag  (defensa-en-código)
  │  Si tag ≠ tenantId → 403 inmediato (sin llamar a KMS)
  │
  │  Si pasa, la operación KMS se ejecuta con credenciales de TenantKmsRole-tenant-a
  │  AWS IAM evalúa la condition aws:ResourceTag/tenantId = "tenant-a"
  │  Si la clave tiene otro tenantId → AccessDeniedException  (defensa-en-IAM)
  ▼
Respuesta al cliente
```

### Políticas IAM del TenantKmsRole-{tenantId}

```json
// CreateKey: el tag que se va a asignar DEBE ser el del tenant
{
  "Effect": "Allow",
  "Action": ["kms:CreateKey"],
  "Resource": "*",
  "Condition": { "StringEquals": { "aws:RequestTag/tenantId": "{tenantId}" } }
}

// Resto de operaciones: la clave DEBE estar tagueada con el tenant
{
  "Effect": "Allow",
  "Action": ["kms:DescribeKey", "kms:GetPublicKey", "kms:ScheduleKeyDeletion",
             "kms:ListResourceTags", "kms:TagResource"],
  "Resource": "*",
  "Condition": { "StringEquals": { "aws:ResourceTag/tenantId": "{tenantId}" } }
}
```

### Provisioning de roles

```bash
# Modo normal: auto-descubre tenants desde Cognito (custom:tenant_id) y provisiona un role por cada uno
./lambdas/setup-tenant-kms-roles.sh --env dev

# Añadir un nuevo tenant sin reprocesar todos (provisiona solo ese)
./lambdas/setup-tenant-kms-roles.sh --env dev --tenant tenant-nuevo

# Especificar pool explícitamente (útil en sta/pro antes de rellenar el mapa del script)
./lambdas/setup-tenant-kms-roles.sh --env sta --user-pool-id eu-west-1_XxxxxXXX
```

El script pagina `cognito-idp list-users` hasta agotar todos los usuarios, extrae los valores únicos del atributo `custom:tenant_id` y crea o actualiza `TenantKmsRole-{tenantId}` para cada uno.

### Garantía de aislamiento — matriz de ataques

Cada vector de ataque posible y el control que lo bloquea:

| Vector de ataque | ¿Cómo se intenta? | Control que lo bloquea | Capa |
|---|---|---|---|
| **Falsificar tenantId en el body** | `POST /api/kms/ed25519` con `"tenantId": "otro-tenant"` en el JSON | El handler ignora el body para el tenantId — lo extrae del JWT, validado por API GW antes de llegar a la lambda | Código |
| **Usar JWT de otro tenant** | Enviar un JWT perteneciente a otro usuario/tenant | JWT authorizer de API GW valida firma y expiración contra Cognito — un JWT de otro tenant es válido pero su `custom:tenant_id` es el correcto para ese tenant, no el atacante | Cognito / API GW |
| **JWT manipulado (claim falso)** | Modificar el payload del JWT para cambiar `custom:tenant_id` | La firma JWT deja de ser válida — API GW rechaza con 401 antes de invocar la lambda | API GW JWT Authorizer |
| **Query de clave ajena conociendo su keyId** | `GET /api/kms/ed25519/{keyId-de-otro-tenant}` | 1. El `KMSClient` usa credenciales de `TenantKmsRole-{mi-tenant}` que solo permite `kms:ListResourceTags` en claves tagueadas con `tenantId=mi-tenant` → `AccessDeniedException` de IAM. 2. Incluso si IAM fallase, el check de tag en código devuelve 403. | IAM (primaria) + Código (secundaria) |
| **Delete de clave ajena conociendo su keyId** | `DELETE /api/kms/ed25519/{keyId-de-otro-tenant}` | Igual que query: las credenciales scopadas de `TenantKmsRole-{mi-tenant}` son rechazadas por IAM sobre claves de otro tenant | IAM (primaria) + Código (secundaria) |
| **Crear clave con tag de otro tenant** | `POST /api/kms/ed25519` intentando inyectar `tenantId: "otro-tenant"` en tags | El tenantId del JWT es el que se usa para crear la clave. Adicionalmente, la condición `aws:RequestTag/tenantId = {mi-tenant}` del role impide crear claves con tags de otro tenant | Código + IAM |
| **Acceso directo a KMS con credenciales propias** | Llamar a AWS KMS directamente con credenciales del usuario (no de la lambda) | Los usuarios de Cognito no tienen credenciales IAM directas sobre KMS — las credenciales scopadas existen solo en memoria de la lambda durante la invocación | Arquitectura |
| **Adivinanza de keyId** | Iterar UUIDs para descubrir keyIds ajenos | Los keyIds son UUIDs v4 (2^122 posibilidades) — inviable. Y aunque se adivinase, el control anterior bloquea el acceso | IAM |
| **Tenant no provisionado** | Llamar con un JWT cuyo tenant no tiene `TenantKmsRole` creado | `sts:AssumeRole` falla — la lambda devuelve 500 sin ejecutar ninguna operación KMS | STS |

### Qué NO protege este modelo (fuera de alcance)

- **Compromiso de credenciales Cognito de otro tenant:** si un atacante obtiene las credenciales de login de un usuario de otro tenant, tendrá acceso legítimo a sus claves. Esto está fuera del alcance de la capa de aplicación y se mitiga con MFA en Cognito.
- **Acceso de administradores AWS:** los administradores de la cuenta pueden operar sobre cualquier clave KMS directamente. Esto es inherente a la arquitectura cloud y se controla mediante AWS CloudTrail + alertas en CloudWatch.
- **Invocación directa de la lambda (legacy):** el path de invocación directa (sin API GW) no aplica STS ni verifica JWT — existe para uso interno/tests y no debe exponerse públicamente.

---

## Fuentes (código)

| Archivo | Descripción |
|---|---|
| `lambdas/kms-key-*/src/handler.js` | Extrae `tenantId` del JWT, asume TenantKmsRole via STS, enruta método HTTP |
| `lambdas/kms-key-*/src/lib/tenantKmsCredentials.js` | `getTenantKmsCredentials(tenantId)` — STS AssumeRole sobre TenantKmsRole-{tenantId} |
| `lambdas/kms-key-*/src/operations/create.js` | Llama a `KMS.CreateKey`, añade tags `tenantId` + `keyType` automáticamente |
| `lambdas/kms-key-*/src/operations/list.js` | Resource Groups Tagging API filtrada por `tenantId`+`keyType`, luego `KMS.DescribeKey` |
| `lambdas/kms-key-*/src/operations/query.js` | Verifica tag + `KMS.DescribeKey` + `KMS.GetPublicKey` con credenciales scopadas |
| `lambdas/kms-key-*/src/operations/delete.js` | Verifica tag + `KMS.ScheduleKeyDeletion` (7 días) con credenciales scopadas |
| `lambdas/setup-tenant-kms-roles.sh` | Crea `TenantKmsRole-{tenantId}` en IAM y concede `sts:AssumeRole` al lambda role |
| `lambdas/deploy-kms-lambdas.sh` | Script de despliegue ZIP — `--env dev\|sta\|pro` |

---

## Despliegue

### Actualizar código de lambdas

```bash
cd /path/to/sybolRelases
./lambdas/deploy-kms-lambdas.sh --env dev
```

### Añadir rutas a un nuevo entorno

Las rutas se crearon con AWS CLI directamente sobre `WalletApi`. Para replicar en otro API GW:

```bash
API_ID="<api-id>"
AUTH_ID="<authorizer-id>"
REGION="eu-west-1"
ACCOUNT="111891094335"

for TYPE in ed25519 p256 secp256k1 rsa; do
  FN="sybol-kms-key-${TYPE}-dev"   # cambiar sufijo por entorno

  INT_ID=$(aws apigatewayv2 create-integration \
    --api-id $API_ID \
    --integration-type AWS_PROXY \
    --integration-uri "arn:aws:lambda:${REGION}:${ACCOUNT}:function:${FN}" \
    --payload-format-version "2.0" \
    --region $REGION \
    --query 'IntegrationId' --output text)

  aws apigatewayv2 create-route --api-id $API_ID \
    --route-key "POST /api/kms/${TYPE}" \
    --target "integrations/${INT_ID}" \
    --authorization-type JWT --authorizer-id $AUTH_ID --region $REGION

  aws apigatewayv2 create-route --api-id $API_ID \
    --route-key "GET /api/kms/${TYPE}" \
    --target "integrations/${INT_ID}" \
    --authorization-type JWT --authorizer-id $AUTH_ID --region $REGION

  aws apigatewayv2 create-route --api-id $API_ID \
    --route-key "GET /api/kms/${TYPE}/{keyId}" \
    --target "integrations/${INT_ID}" \
    --authorization-type JWT --authorizer-id $AUTH_ID --region $REGION

  aws apigatewayv2 create-route --api-id $API_ID \
    --route-key "DELETE /api/kms/${TYPE}/{keyId}" \
    --target "integrations/${INT_ID}" \
    --authorization-type JWT --authorizer-id $AUTH_ID --region $REGION

  aws lambda add-permission \
    --function-name $FN \
    --statement-id "apigateway-${API_ID}-kms-${TYPE}" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT}:${API_ID}/*/*/api/kms/*" \
    --region $REGION
done
```

---

## Ejemplo de uso

```bash
# Obtener token Cognito
TOKEN=$(aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id <client-id> \
  --auth-parameters USERNAME=<user>,PASSWORD=<pass> \
  --region eu-west-1 \
  --query 'AuthenticationResult.IdToken' --output text)

BASE="https://13xxajdiae.execute-api.eu-west-1.amazonaws.com"

# Crear clave ed25519 (tenantId se toma del JWT — no hace falta enviarlo en el body)
curl -s -X POST "$BASE/api/kms/ed25519" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description":"DID signing key"}' | jq .

# Listar todas las claves ed25519 del tenant (tenantId viene del JWT)
curl -s "$BASE/api/kms/ed25519" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Consultar clave individual (incluye clave pública)
curl -s "$BASE/api/kms/ed25519/<keyId>" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Eliminar clave (programa borrado 7 días)
curl -s -X DELETE "$BASE/api/kms/ed25519/<keyId>" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## Notas

- Las claves KMS **no se borran inmediatamente** al hacer DELETE — se programa con 7 días de ventana cancelable.
- La clave pública devuelta en `query` está en formato DER codificado en base64.
- Los handlers mantienen compatibilidad con invocación directa (sin API GW) para uso interno o tests. En ese path no se aplica STS ni verificación JWT — no debe exponerse públicamente.
- El role de ejecución de la lambda (`sybol-kms-lambda-dev-role`) solo necesita `sts:AssumeRole` sobre `TenantKmsRole-*`. Los permisos KMS efectivos los tiene el role del tenant, no la lambda directamente.
- Para que el aislamiento funcione, cada tenant debe tener su `TenantKmsRole-{tenantId}` provisionado con `setup-tenant-kms-roles.sh` antes de que sus usuarios puedan operar.
