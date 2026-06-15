# POC: Integración DID Hedera Hashgraph — generación y gestión de did:hedera desde Sybol

**Estado:** Borrador
**Fecha:** 2026-03-30
**Autores:** Equipo Sybol
**Rama:** `feature/eddera-poc`

---

## 1. Objetivo

Esta POC demuestra que Sybol puede **generar, anclar y gestionar DIDs en la red Hedera Hashgraph** de forma integrada con la infraestructura de claves existente de Sybol, produciendo DIDs conformes con la especificación W3C DID Core 1.0 y el método `did:hedera`.

El resultado concreto de la POC es un flujo end-to-end funcional que:

1. Genera o reutiliza un par de claves Ed25519 (o secp256k1) para un tenant.
2. Crea un HCS topic en Hedera para anclar el DID Document.
3. Publica el DID Document como mensaje en el topic HCS correspondiente.
4. Obtiene el DID resultante con formato `did:hedera:testnet:<base58-public-key>_<topic-id>`.
5. Resuelve el DID Document consultando el mirror node de Hedera.
6. Emite una Verifiable Credential W3C firmada con ese DID como `issuer`.

---

## 2. Red objetivo — Hedera Hashgraph

### 2.1 Identificación de la red

**Hedera Hashgraph** es una red de libro mayor distribuido de acceso público, gestionada por el Hedera Governing Council. Usa el algoritmo de consenso hashgraph (aBFT), con finality en segundos y costes de transacción muy bajos (~$0.0001 USD por transacción).

Hedera opera las siguientes redes:

| Red | Tipo | Uso | Chain ID (CAIP-2) |
|-----|------|-----|------------------|
| **mainnet** | Productiva | Producción | `hedera:mainnet` |
| **testnet** | Pruebas persistente | Desarrollo / POC | `hedera:testnet` |
| **previewnet** | Preview de features | Experimental | `hedera:previewnet` |
| **devnet** | Desarrollo interno | Uso de Hedera | `hedera:devnet` |

Para la POC se usará **testnet**, que es gratuita con faucet de HBAR.

### 2.2 Método DID — did:hedera

| Propiedad | Valor |
|-----------|-------|
| Método | `did:hedera` |
| Especificación oficial | [hashgraph/did-method (GitHub)](https://github.com/hashgraph/did-method) |
| Especificación Meeco (actualizada W3C DID Core 1.0) | [Meeco/hedera-did-method (GitHub)](https://github.com/Meeco/hedera-did-method) |
| HIP relevante | [HIP-27](https://hips.hedera.com/hip/hip-27), [HIP-19](https://hips.hedera.com/hip/hip-19), [HIP-1219](https://hips.hedera.com/hip/hip-1219) |
| Sintaxis canónica | `did:hedera:<network>:<base58-did-root-public-key>_<hcs-topic-id>` |
| Ejemplo mainnet | `did:hedera:mainnet:7Prd74ry1Uct87nZqL3ny7aR7Cg46JamVbJgk8azVgUm_0.0.29656231` |
| Ejemplo testnet | `did:hedera:testnet:z6Mkk...base58key..._0.0.4896158` |

**Componentes del DID:**
- `hedera` — nombre del método
- `<network>` — `mainnet` o `testnet`
- `<base58-did-root-public-key>` — codificación base58 de la clave pública raíz del DID
- `<hcs-topic-id>` — identificador del topic HCS donde se anclan las operaciones sobre el DID (formato `shard.realm.num`, ej. `0.0.29656231`)

### 2.3 Estructura del DID Document

Un DID Document conforme al método did:hedera tiene la siguiente estructura:

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://ns.did.ai/transmute/v1"
  ],
  "id": "did:hedera:testnet:<base58-public-key>_0.0.12345",
  "verificationMethod": [
    {
      "id": "did:hedera:testnet:<base58-public-key>_0.0.12345#did-root-key",
      "type": "Ed25519VerificationKey2018",
      "controller": "did:hedera:testnet:<base58-public-key>_0.0.12345",
      "publicKeyBase58": "<base58-encoded-ed25519-public-key>"
    }
  ],
  "authentication": [
    "did:hedera:testnet:<base58-public-key>_0.0.12345#did-root-key"
  ],
  "assertionMethod": [
    "did:hedera:testnet:<base58-public-key>_0.0.12345#did-root-key"
  ]
}
```

**Requisitos obligatorios:**
- El DID Document DEBE contener una clave de id `#did-root-key` de tipo `Ed25519VerificationKey2018`.
- El identificador base58 del DID es la codificación de esta clave pública.
- Las operaciones CRUD se envían como mensajes HCS al topic del DID.
- La resolución se realiza consultando el mirror node de Hedera (sin estado on-chain complejo, solo lectura de mensajes HCS).

---

## 3. Arquitectura Hedera DID — Cómo funciona did:hedera

### 3.1 Hedera Consensus Service (HCS)

El HCS es el servicio de Hedera que proporciona timestamping y ordenación de mensajes con finality aBFT. A diferencia de las blockchains EVM (donde el estado se almacena en contratos), **did:hedera no usa smart contracts**: todo el ciclo de vida del DID se gestiona mediante mensajes en un topic HCS.

```
Flujo de anclaje:
──────────────────────────────────────────────────────────────
1. Se crea un HCS Topic (una vez, coste: ~$0.01 USD)
2. Las operaciones DID (create/update/delete) se envían como
   mensajes JSON firmados a ese topic (coste: ~$0.0001 USD/msg)
3. Los mensajes son ordenados y timestampados por los nodos Hedera
4. Para resolver un DID, se consulta el mirror node (HTTP/grpc)
   recuperando el historial de mensajes del topic
5. El estado actual del DID Document se reconstruye aplicando
   los mensajes en orden
──────────────────────────────────────────────────────────────
```

### 3.2 Operaciones DID sobre HCS

| Operación | Mecanismo | Coste aprox. |
|-----------|-----------|--------------|
| CREATE | Mensaje HCS con DID Document inicial | ~$0.0001 |
| UPDATE | Mensaje HCS con patches al DID Document | ~$0.0001 |
| DEACTIVATE | Mensaje HCS con flag de desactivación | ~$0.0001 |
| READ/RESOLVE | Consulta al mirror node (lectura) | Gratis |
| Crear topic | `TopicCreateTransaction` en Hedera | ~$0.01 |

### 3.3 Tipos de clave soportados por Hedera

Hedera soporta nativamente:
- **Ed25519** — recomendado para DIDs (tipo `Ed25519VerificationKey2018`)
- **ECDSA secp256k1** — soportado por HIP-222, compatible con Ethereum

La especificación did:hedera actual define `Ed25519VerificationKey2018` como tipo canónico para `#did-root-key`.

---

## 4. Alcance de la POC

### Dentro del alcance

- Provisioning de clave Ed25519 para un tenant (AWS KMS `ECC_NIST_EDWARDS25519` o par de claves software para la POC).
- Creación de HCS topic en Hedera testnet para el DID del tenant.
- Publicación del DID Document inicial en el topic HCS (operación CREATE).
- Generación del DID string resultante en formato canónico `did:hedera:testnet:...`.
- Registro del DID en el sistema interno de Sybol (base de datos del tenant).
- Resolución del DID Document consultando el mirror node de Hedera testnet.
- Emisión de una Verifiable Credential W3C usando el DID Hedera como `issuer`.
- API endpoint interno en el servicio `businessLogic` para orquestar el flujo.

### Fuera del alcance de la POC

- Despliegue en mainnet (solo testnet para la POC; mainnet vía cambio de config del proxy).
- Optimización de costes HBAR.
- Revocación de claves DID on-chain (operación UPDATE/DEACTIVATE completa).
- Publicación en universal resolver público (DIF Universal Resolver).
- Integración con wallet móvil de usuario final.
- Alta disponibilidad del cliente Hedera.
- Soporte para did:hedera con smart contracts (HIP-32+).

> **Nota:** Las Lambdas KMS por tipo de clave (`kms-key-*`) y el contenedor proxy Hedera son **componentes de producción**, no de POC. Se desarrollan en paralelo a la POC y forman parte del mismo entregable de la rama `feature/eddera-poc`.

---

## 5. Arquitectura propuesta en Sybol

La arquitectura de producción consta de tres capas nuevas además de la lógica principal en `businessLogic`:

```
Tenant Admin / Backoffice
        │
        ▼
[businessLogic] POST /api/bl/hedera/setup-did
        │
        ├── Valida tenant y permisos (authMiddleware)
        ├── Invoca Lambda KMS para provisionar clave Ed25519 del tenant
        │     (Lambda: kms-key-ed25519 — ver §5.2)
        │
        ▼
[HederaDIDService] (nuevo módulo en businessLogic)
        │
        ├── Envía todas las peticiones Hedera al contenedor proxy
        │     (Hedera Proxy Container — ver §5.3)
        ├── Crea HCS topic (TopicCreateTransaction)
        ├── Construye DID Document JSON
        ├── Publica mensaje CREATE en el topic HCS
        ├── Genera DID string: did:hedera:testnet:<base58Key>_<topicId>
        │
        ▼
[Persistencia]
        ├── Almacena DID, topicId, kmsKeyId en base de datos del tenant
        │
        ▼
[DID Resolution]
        ├── GET /api/bl/hedera/did-document?did=did:hedera:testnet:...
        ├── Via proxy → mirror.hedera.com/api/v1/topics/{topicId}/messages
        └── Reconstruye DID Document desde mensajes HCS
```

### 5.1 Componentes involucrados

| Componente | Tipo | Rol |
|-----------|------|-----|
| `services/businessLogic` | Servicio Express | Orquesta el flujo, expone la API DID |
| `lambdas/kms-key-ed25519` | Lambda Node.js | Ciclo de vida clave Ed25519 — genera fuera de KMS, importa a KMS |
| `lambdas/kms-key-secp256k1` | Lambda Node.js | Ciclo de vida clave secp256k1 vía KMS directo |
| `lambdas/kms-key-p256` | Lambda Node.js | Ciclo de vida clave P-256 vía KMS directo |
| `lambdas/kms-key-rsa` | Lambda Node.js | Ciclo de vida clave RSA vía KMS directo |
| `hedera-proxy` | Contenedor Docker | Proxy de red para Hedera — switching testnet/mainnet por config |
| `@hashgraph/sdk` | npm | SDK oficial de Hedera — HCS y mirror node |
| `@hashgraph/did-sdk-js` | npm | SDK DID de Hedera — gestión del DID Document sobre HCS |
| AWS KMS | Servicio AWS | Custodia de claves criptográficas (todas las curvas) |
| AWS Secrets Manager | Servicio AWS | `operatorId` y material de clave transitorio en importación |
| Hedera testnet/mainnet | Red externa | Ancla los topics y mensajes HCS |

---

### 5.2 Lambdas KMS — Ciclo de vida de claves por tipo

#### Diseño general

Se crea **una Lambda Node.js por tipo de clave soportado**. Cada Lambda expone tres operaciones: `create`, `query` y `delete`. No son POCs — son Lambdas de producción que usan el motor KMS directamente.

| Lambda | KeySpec KMS | Algoritmo | Observación |
|--------|-------------|-----------|-------------|
| `kms-key-ed25519` | `ECC_NIST_EDWARDS25519` | `ED25519_SHA_512` | Requiere import de material (ver abajo) |
| `kms-key-secp256k1` | `ECC_SECG_P256K1` | `ECDSA_SHA_256` | KMS nativo directo |
| `kms-key-p256` | `ECC_NIST_P256` | `ECDSA_SHA_256` | KMS nativo directo — tipo ya en uso en Sybol |
| `kms-key-rsa` | `RSA_4096` | `RSASSA_PKCS1_V1_5_SHA_256` | KMS nativo directo |

#### Interfaz de invocación (evento Lambda)

```json
{
  "operation": "create" | "query" | "delete",
  "keyId": "<kms-key-id>",       // requerido para query/delete
  "tenantId": "<tenant-uuid>",
  "description": "<descripción>", // solo para create
  "tags": { "key": "value" }      // solo para create
}
```

#### Respuesta

```json
{
  "success": true,
  "keyId": "<kms-key-id>",
  "keyArn": "<arn:aws:kms:...>",
  "publicKey": "<DER base64>",    // solo en create/query
  "keySpec": "ECC_NIST_EDWARDS25519"
}
```

#### Caso especial: `kms-key-ed25519` — importación de material de clave

AWS KMS no puede generar material Ed25519 internamente para importar — el algoritmo `ECC_NIST_EDWARDS25519` se genera directamente por KMS sin necesidad de importar. Sin embargo, si se requiere importar una clave generada externamente (por compatibilidad con material existente), la Lambda soporta el flujo de import:

```javascript
// 1. Generar par de claves Ed25519 fuera de KMS (en memoria, nunca persistido en disco)
const { ed25519 } = require('@noble/ed25519'); // o @noble/curves/ed25519
const privateKeyBytes = ed25519.utils.randomPrivateKey();
const publicKeyBytes = await ed25519.getPublicKey(privateKeyBytes);

// 2. Crear contenedor de importación en KMS
const { ImportToken, PublicKey: wrappingKey } = await kms.getParametersForImport({
  KeyId: keyId,
  WrappingAlgorithm: 'RSAES_OAEP_SHA_256',
  WrappingKeySpec: 'RSA_4096'
});

// 3. Cifrar la clave privada con la wrapping key
const encryptedKeyMaterial = wrapKeyWithRSA(privateKeyBytes, wrappingKey);

// 4. Importar el material cifrado a KMS
await kms.importKeyMaterial({
  KeyId: keyId,
  ImportToken,
  EncryptedKeyMaterial: encryptedKeyMaterial
});

// La clave privada raw se descarta de memoria — nunca sale del proceso Lambda
```

**Para el caso estándar (generación nueva)**, la Lambda simplemente invoca `CreateKey` con `KeySpec: ECC_NIST_EDWARDS25519` y KMS genera el material internamente:

```javascript
// Operación create estándar — KMS genera el material Ed25519 internamente
const result = await kms.createKey({
  KeySpec: 'ECC_NIST_EDWARDS25519',
  KeyUsage: 'SIGN_VERIFY',
  Description: `Hedera DID key - tenant ${tenantId}`,
  Tags: [{ TagKey: 'tenantId', TagValue: tenantId }]
});
```

#### Operaciones por Lambda

| Operación | Descripción | AWS KMS API |
|-----------|-------------|-------------|
| `create` | Crea nueva clave en KMS del tipo correspondiente | `CreateKey` |
| `query` | Obtiene metadatos y clave pública | `DescribeKey` + `GetPublicKey` |
| `delete` | Programa borrado de la clave (espera 7 días mínimo en KMS) | `ScheduleKeyDeletion` |

---

### 5.3 Hedera Proxy Container

#### Propósito

Todas las peticiones hacia la red Hedera (tanto hacia los nodos consensus como hacia el mirror node) pasan a través de un contenedor proxy. El cambio entre **testnet** y **mainnet** se realiza exclusivamente mediante configuración del proxy — sin cambios en `businessLogic`.

#### Diseño

```
businessLogic / Lambda
        │
        │ HTTP (interno VPC)
        ▼
[hedera-proxy container]
        │
        ├── HEDERA_NETWORK=testnet  →  testnet.hedera.com
        │                              testnet.mirrornode.hedera.com
        │
        └── HEDERA_NETWORK=mainnet  →  mainnet.hedera.com
                                       mainnet.mirrornode.hedera.com
```

#### Configuración del proxy

```yaml
# docker-compose.yml / ECS task definition
environment:
  HEDERA_NETWORK: testnet        # testnet | mainnet — único cambio necesario
  HEDERA_MIRROR_URL: https://testnet.mirrornode.hedera.com
  HEDERA_NODE_ENDPOINT: testnet.hedera.com:50211
  PORT: 3900
```

#### Interfaz del proxy (REST)

```
POST /hedera/topic/create          → TopicCreateTransaction
POST /hedera/topic/:topicId/message → TopicMessageSubmitTransaction
GET  /hedera/topic/:topicId/messages → Mirror node — historial de mensajes
GET  /hedera/health                 → Estado de la conexión con la red
```

El proxy encapsula el cliente `@hashgraph/sdk`, gestiona las reconexiones y expone una API HTTP interna independiente de la red subyacente. El `operatorId` y `operatorKey` se inyectan como variables de entorno en el contenedor y no son visibles desde `businessLogic`.

---

## 6. Flujo técnico paso a paso

### Paso 1 — Provisioning de la clave DID (Ed25519)

```
Opcion A — AWS KMS nativo (recomendado para produccion):
  AWS KMS: CreateKey(KeySpec=ECC_NIST_EDWARDS25519, KeyUsage=SIGN_VERIFY)
    → KMS devuelve: { KeyId, KeyArn }
  AWS KMS: GetPublicKey(KeyId)
    → DER SubjectPublicKeyInfo con clave Ed25519 de 32 bytes
    → base58(publicKeyBytes) = did-root-key para el DID string

Opcion B — Par de claves software (valido para POC inicial):
  PrivateKey.generateED25519() via @hashgraph/sdk
    → privateKey.publicKey.toBytes()
    → base58(publicKey) = did-root-key
  Clave privada almacenada en AWS Secrets Manager
```

> Ver ADR-hedera-002 para la decision sobre Ed25519 vs secp256k1 y KMS vs software.

### Paso 2 — Inicializar cliente Hedera

```javascript
const { Client } = require('@hashgraph/sdk');

const client = Client.forTestnet();
client.setOperator(
  process.env.HEDERA_OPERATOR_ID,    // 0.0.XXXXX
  process.env.HEDERA_OPERATOR_KEY    // clave privada Ed25519 del operador (HBAR para pagar fees)
);
```

El `operatorId` y `operatorKey` son credenciales de la cuenta Hedera del tenant/operador que paga los fees en HBAR. Se obtienen creando una cuenta testnet en el [Hedera Portal](https://portal.hedera.com).

### Paso 3 — Crear HCS topic para el DID

```javascript
const { TopicCreateTransaction } = require('@hashgraph/sdk');

const transaction = await new TopicCreateTransaction()
  .setSubmitKey(operatorPublicKey) // solo el operador puede publicar mensajes
  .execute(client);

const receipt = await transaction.getReceipt(client);
const topicId = receipt.topicId.toString(); // "0.0.XXXXX"
```

### Paso 4 — Construir y publicar el DID Document (CREATE)

```javascript
const { HcsDid } = require('@hashgraph/did-sdk-js');

const did = new HcsDid({
  privateKey: didPrivateKey,       // clave Ed25519 del DID
  client: client,
  topicId: topicId
});

// Registra el DID Document en HCS
await did.register();

// DID string resultante:
const didString = did.getIdentifier();
// "did:hedera:testnet:<base58Key>_0.0.XXXXX"
```

### Paso 5 — Almacenar DID en Sybol

```javascript
// Base de datos del tenant:
await db.query(`
  INSERT INTO hedera_identities (tenant_id, did, topic_id, kms_key_id, network, created_at)
  VALUES ($1, $2, $3, $4, $5, NOW())
`, [tenantId, didString, topicId, kmsKeyId, 'testnet']);
```

### Paso 6 — Resolución del DID Document

```javascript
// Opcion 1: via @hashgraph/did-sdk-js
const resolvedDid = await HcsDidResolver.resolve(didString, client);
const didDocument = resolvedDid.toJson();

// Opcion 2: via mirror node HTTP (sin SDK)
const topicId = extractTopicId(didString); // "0.0.XXXXX"
const response = await fetch(
  `https://testnet.mirrornode.hedera.com/api/v1/topics/${topicId}/messages`
);
const messages = await response.json();
// Reconstruir DID Document desde mensajes en orden cronologico
```

### Paso 7 — Emisión de Verifiable Credential W3C

El DID Hedera se registra como `issuerKey` en el servicio `businessLogic` y puede usarse en el flujo de `JWTCredentialManager.generateCredential()` existente, firmando con la clave KMS Ed25519 del Paso 1 (algoritmo `EdDSA` / `Ed25519Signature2018`).

---

## 7. Librerías npm identificadas

| Librería | Versión | Rol | Estado |
|---------|---------|-----|--------|
| `@hashgraph/sdk` | ^2.x | Cliente oficial Hedera — HCS, cuentas, transacciones | Por instalar |
| `@hashgraph/did-sdk-js` | ^0.1.x | SDK DID Hedera — gestión del DID Document sobre HCS | Por instalar |
| `@aws-sdk/client-kms` | ^3.500.0 | Firma con KMS (Ed25519 / ECC_NIST_EDWARDS25519) | Ya en uso |
| `@aws-sdk/client-secrets-manager` | ^3.0.0 | Almacenamiento de operatorKey y material de claves | Ya en uso |
| `bs58` | ^5.0.0 | Codificacion base58 de la clave publica para el DID string | Por evaluar |
| `did-resolver` | ^4.x | Interfaz estandar W3C para resolvers de DID | Por evaluar |

> **Nota sobre @hashgraph/did-sdk-js:** El paquete oficial publicado en npm puede estar desactualizado respecto a la especificacion W3C DID Core 1.0. La version mantenida por Meeco (`Meeco/hedera-did-sdk-js` en GitHub) puede ser mas reciente. Evaluar ambas al inicio de la implementacion.

> **Nota sobre hiero-sdk-js:** Hedera esta en proceso de transicion al proyecto open-source Hiero (`hiero-ledger/hiero-sdk-js`). Para la POC, `@hashgraph/sdk` es suficiente y mas estable.

---

## 8. Integracion con Sybol

### 8.1 Servicio anfitri&oacute;n

La logica de la POC residira en el servicio `businessLogic`, que ya contiene la infraestructura de KMS, autenticacion de tenants y gestion de DIDs (did:sybol). Se añade un modulo `hedera/` bajo `services/businessLogic/src/`:

```
services/businessLogic/src/hedera/
├── hederaDid.service.js     ← orquestacion: crear topic, registrar DID, resolver
├── hederaDid.utils.js       ← parse del DID string, extraccion de topicId/publicKey
└── hederaClient.js          ← factory del cliente @hashgraph/sdk por tenant
```

### 8.2 Endpoints API necesarios

```
POST /api/bl/hedera/setup-did
  Body:    { network?: "testnet" | "mainnet" }
  Headers: Authorization (tenant auth)
  Response: {
    did: "did:hedera:testnet:<base58Key>_0.0.XXXXX",
    topicId: "0.0.XXXXX",
    network: "testnet",
    status: "registered"
  }

GET /api/bl/hedera/did-document
  Query:   ?did=did:hedera:testnet:...
  Response: { didDocument: { "@context": [...], "id": "...", ... } }
```

### 8.3 Base de datos

Nueva tabla para las identidades Hedera del tenant:

```sql
CREATE TABLE hedera_identities (
  id          SERIAL PRIMARY KEY,
  tenant_id   UUID NOT NULL REFERENCES tenants(id),
  did         TEXT NOT NULL UNIQUE,
  topic_id    TEXT NOT NULL,           -- "0.0.XXXXX"
  kms_key_id  TEXT,                    -- ARN de la clave KMS Ed25519
  network     TEXT NOT NULL DEFAULT 'testnet',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 9. Criterios de exito de la POC

La POC se considera exitosa cuando:

- [ ] Se crea un HCS topic en Hedera testnet sin errores.
- [ ] El DID Document inicial se publica en el topic HCS con exito.
- [ ] El DID string generado tiene formato correcto: `did:hedera:testnet:<base58Key>_0.0.XXXXX`.
- [ ] El DID Document se puede resolver consultando el mirror node de Hedera testnet.
- [ ] El DID Document resuelto contiene la clave publica correcta (`#did-root-key`).
- [ ] Una Verifiable Credential W3C se puede emitir usando el DID Hedera como `issuer`.
- [ ] Las claves privadas nunca salen del perimetro seguro (KMS o Secrets Manager).
- [ ] El flujo es idempotente (segunda invocacion detecta DID ya registrado).
- [ ] Los logs de CloudTrail reflejan cada operacion de firma KMS.

---

## 10. Esfuerzo estimado

### POC — Integración DID Hedera

| Actividad | Estimación |
|-----------|-----------|
| Configuración de cuenta Hedera testnet y faucet HBAR | 0.5 días |
| Integración `@hashgraph/sdk` y `@hashgraph/did-sdk-js` en businessLogic | 1-2 días |
| Módulo `hederaDid.service.js`: crear topic + registrar DID | 2-3 días |
| Módulo de resolución via mirror node | 1-2 días |
| Endpoints API y persistencia en base de datos | 1-2 días |
| Integración con flujo de emisión de Verifiable Credential | 1-2 días |
| Tests unitarios e integración | 2-3 días |
| **Subtotal POC** | **8-14 días** |

### Producción — Infraestructura de claves y proxy

| Actividad | Estimación |
|-----------|-----------|
| Lambda `kms-key-ed25519` (create/query/delete + import flow) | 2-3 días |
| Lambda `kms-key-secp256k1` (create/query/delete via KMS directo) | 1 día |
| Lambda `kms-key-p256` (create/query/delete via KMS directo) | 1 día |
| Lambda `kms-key-rsa` (create/query/delete via KMS directo) | 1 día |
| Contenedor proxy Hedera (config-driven testnet/mainnet) | 2-3 días |
| Tests de las Lambdas KMS + proxy | 2-3 días |
| **Subtotal producción** | **9-11 días** |

| **Total estimado** | **17-25 días** |

---

## 11. Riesgos y dependencias

| Riesgo | Impacto | Mitigacion |
|--------|---------|-----------|
| AWS KMS no soporta Ed25519 en todas las regiones | Medio | Verificar disponibilidad en `eu-west-1`; alternativa: par de claves software para POC almacenado en Secrets Manager |
| `@hashgraph/did-sdk-js` desactualizado respecto a W3C DID Core 1.0 | Medio | Evaluar fork Meeco (`Meeco/hedera-did-sdk-js`); implementacion manual del protocolo HCS es factible |
| Acceso HBAR testnet (faucet) | Bajo | Faucet gratuito en Hedera Portal; el testnet es estable |
| Formato de clave KMS Ed25519 vs formato esperado por Hedera SDK | Alto | La clave publica DER del KMS necesita extraccion de los 32 bytes raw Ed25519; requiere parsing DER manual |
| Mirror node latencia en testnet | Bajo | Reintentos con backoff; aceptable para POC |
| Compatibilidad `Ed25519VerificationKey2018` vs `Ed25519VerificationKey2020` | Bajo | Usar la version indicada en la especificacion did:hedera activa |
| Costes HBAR en mainnet | Bajo (solo testnet en POC) | Crear topic: ~$0.01; mensaje HCS: ~$0.0001; totalmente asumible |

---

## Referencias

- [hashgraph/did-method — Especificacion oficial](https://github.com/hashgraph/did-method)
- [Meeco/hedera-did-method — Especificacion actualizada W3C DID Core 1.0](https://github.com/Meeco/hedera-did-method)
- [hashgraph/did-sdk-js — SDK JavaScript](https://github.com/hashgraph/did-sdk-js)
- [@hashgraph/did-sdk-js en npm](https://www.npmjs.com/package/@hashgraph/did-sdk-js)
- [@hashgraph/sdk en npm](https://www.npmjs.com/package/@hashgraph/sdk)
- [HIP-27: DID improvements](https://hips.hedera.com/hip/hip-27)
- [HIP-19: Decentralized Identifiers in Memo Fields](https://hips.hedera.com/hip/hip-19)
- [HIP-1219: Hedera DID Method v2.0](https://hips.hedera.com/hip/hip-1219)
- [Hedera Consensus Service — Blog](https://hedera.com/blog/decentralized-identity-on-the-hedera-consensus-service/)
- [W3C DID Core 1.0](https://www.w3.org/TR/did-core/)
- [Hedera Portal (cuentas testnet)](https://portal.hedera.com)
- [Hedera mirror node testnet](https://testnet.mirrornode.hedera.com)
- [AWS KMS Key Spec Reference](https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-choose-key-spec.html)
