# ADR-hedera-002: Gestion de claves criptograficas para did:hedera en el contexto de AWS KMS de Sybol

**Estado:** Aceptado
**Fecha:** 2026-03-30
**Autores:** Equipo Sybol
**Rama:** `feature/eddera-poc`

---

## Contexto

La especificacion did:hedera requiere una clave raiz de tipo **Ed25519** para el DID Document (tipo `Ed25519VerificationKey2018`, campo `#did-root-key`). La infraestructura de claves actual de Sybol usa AWS KMS con claves **ECDSA P-256** (`ECC_NIST_P256`, algoritmo `ECDSA_SHA_256`), que es el tipo dominante en el codebase.

Existe una tension fundamental entre:

- El tipo de clave canonico requerido/preferido por did:hedera (Ed25519)
- La infraestructura KMS actual de Sybol (ECDSA P-256 / P-256k1)

Esta ADR analiza las opciones y establece la decision para la POC y la via hacia produccion.

### Estado actual de la infraestructura de claves en Sybol

Del analisis del codebase (`services/businessLogic/src/lib/tenantKmsService.js` y `persistence/kms/signing.js`):

- **Algoritmo de firma activo:** `ECDSA_SHA_256` (AWS KMS)
- **Tipo de clave KMS en uso:** Implicito en `ECC_NIST_P256` segun el algoritmo `ES256` del JWT header
- **Patron de uso:** `SignCommand` con `MessageType: DIGEST` y `SigningAlgorithm: ECDSA_SHA_256`
- **Servicio principal:** `TenantKMSService` en `businessLogic`, instanciado por tenant con credenciales STS
- **Alias KMS:** `alias/tenant/{tenantId}/{userRole}-jwt`

### Soporte de tipos de clave en AWS KMS

| KeySpec KMS | Algoritmo de firma | Curva | Soportado en AWS KMS |
|-------------|-------------------|-------|----------------------|
| `ECC_NIST_P256` | `ECDSA_SHA_256` | P-256 (NIST) | Si |
| `ECC_NIST_P384` | `ECDSA_SHA_384` | P-384 (NIST) | Si |
| `ECC_SECG_P256K1` | `ECDSA_SHA_256` | secp256k1 | Si |
| `ECC_NIST_EDWARDS25519` | `ED25519_SHA_512` | Ed25519 (Edwards) | **Si — desde 2023** |
| RSA (varios) | `RSASSA_PKCS1_V1_5_SHA_*`, `RSASSA_PSS_SHA_*` | N/A | Si |

**Conclusion clave:** AWS KMS soporta Ed25519 de forma nativa desde 2023 mediante `KeySpec=ECC_NIST_EDWARDS25519`. La limitacion historica de "KMS no soporta Ed25519" ya no aplica.

### Soporte de tipos de clave en Hedera

La especificacion did:hedera define:
- **Ed25519** — tipo canonico para `#did-root-key` (`Ed25519VerificationKey2018`)
- **ECDSA secp256k1** — soportado por HIP-222; tipo `EcdsaSecp256k1VerificationKey2019`

Hedera como red soporta ambos tipos de clave para las cuentas y operaciones nativas.

---

## Opciones evaluadas

### Opcion A — Ed25519 via AWS KMS (ECC_NIST_EDWARDS25519)

**Descripcion:** Crear una nueva clave KMS de tipo `ECC_NIST_EDWARDS25519` especificamente para las operaciones DID Hedera del tenant. Esta clave se usa tanto para firmar mensajes HCS como para derivar la clave publica del DID.

**Ventajas:**
- Tipo de clave canonico de did:hedera — maxima compatibilidad con el ecosistema Hedera
- La clave privada jamas sale del HSM de AWS KMS
- `GetPublicKey` devuelve la clave publica en formato DER; se extraen los 32 bytes de la clave raw Ed25519
- Algoritmo de firma: `ED25519_SHA_512` con `MessageType: RAW`
- Compatible con `Ed25519Signature2018` para Verifiable Credentials
- Alineado con las mejores practicas del ecosistema DID

**Desventajas:**
- Requiere nueva logica de firma en `TenantKMSService` (nuevo `SigningAlgorithm: ED25519_SHA_512`)
- La extraccion de la clave publica Ed25519 desde el DER de KMS requiere parsing manual (los ultimos 32 bytes del SubjectPublicKeyInfo)
- Necesita nueva clave KMS por tenant (ademas de las existentes P-256)

**Implementacion:**
```javascript
// Creacion de clave
const createKeyCommand = new CreateKeyCommand({
  KeySpec: 'ECC_NIST_EDWARDS25519',
  KeyUsage: 'SIGN_VERIFY',
  Description: `Hedera DID key for tenant ${tenantId}`
});

// Firma de mensajes HCS
const signCommand = new SignCommand({
  KeyId: kmsKeyId,
  Message: messageBytes,           // mensaje raw, NO digest
  SigningAlgorithm: 'ED25519_SHA_512',
  MessageType: 'RAW'               // Ed25519 requiere RAW, no DIGEST
});

// Extraccion de clave publica Ed25519 (32 bytes) desde DER
// El DER de una clave Ed25519 tiene la clave publica en los ultimos 32 bytes
const publicKeyDer = getPublicKeyResult.PublicKey; // Buffer
const ed25519PublicKeyBytes = publicKeyDer.slice(-32);
const base58PublicKey = bs58.encode(ed25519PublicKeyBytes);
// DID string: did:hedera:testnet:<base58PublicKey>_<topicId>
```

**Valoracion:** Opcion preferida para produccion.

### Opcion B — Ed25519 via par de claves software (Secrets Manager)

**Descripcion:** Generar el par de claves Ed25519 con el SDK de Hedera (`PrivateKey.generateED25519()`) o con `@noble/ed25519`. Almacenar la clave privada cifrada en AWS Secrets Manager.

**Ventajas:**
- Implementacion mas simple — no requiere cambios en `TenantKMSService`
- Compatible al 100% con `@hashgraph/sdk` y `@hashgraph/did-sdk-js` (que esperan objetos `PrivateKey` nativos)
- Sin coste adicional de KMS por operacion de firma
- Rapido de implementar para la POC

**Desventajas:**
- La clave privada existe fuera del HSM (aunque cifrada en Secrets Manager)
- Menor nivel de seguridad que KMS (sin HSM dedicado para Ed25519 DID)
- Requiere gestion de rotacion de claves en Secrets Manager
- No alineado con la politica de "claves privadas solo en KMS" de Sybol

**Implementacion:**
```javascript
const { PrivateKey } = require('@hashgraph/sdk');

// Generacion
const privateKey = PrivateKey.generateED25519();
const publicKey = privateKey.publicKey;
const base58PublicKey = bs58.encode(publicKey.toBytes());

// Almacenamiento
await secretsManager.createSecret({
  Name: `hedera/did/${tenantId}`,
  SecretString: JSON.stringify({
    privateKeyHex: Buffer.from(privateKey.toBytes()).toString('hex'),
    publicKeyBase58: base58PublicKey
  })
});
```

**Valoracion:** Aceptable para POC; no aceptable para produccion.

### Opcion C — ECDSA secp256k1 via AWS KMS (ECC_SECG_P256K1)

**Descripcion:** Reutilizar el tipo de clave secp256k1 que ya se usa en Sybol (o en la infraestructura EVM de `bm`) para la identidad Hedera, usando `EcdsaSecp256k1VerificationKey2019` como tipo en el DID Document.

**Ventajas:**
- Reutiliza el patron de uso de KMS ya implementado (`ECDSA_SHA_256`)
- La clave secp256k1 puede usarse tanto para DIDs Hedera como para cuentas EVM (Ethereum)
- Menor cambio en la infraestructura

**Desventajas:**
- `EcdsaSecp256k1VerificationKey2019` es el tipo secundario en did:hedera; algunos resolvers y herramientas solo implementan Ed25519
- No usa el tipo canonico de did:hedera, lo que puede generar problemas de interoperabilidad
- El SDK `@hashgraph/did-sdk-js` esta optimizado para Ed25519
- `ECC_SECG_P256K1` no es igual a P-256 NIST: es secp256k1 (Bitcoin/Ethereum), no secp256r1 (NIST P-256)

**Valoracion:** No recomendado — deuda tecnica de interoperabilidad.

### Opcion D — ECDSA P-256 (ECC_NIST_P256) — tipo actual de Sybol

**Descripcion:** Usar la clave P-256 existente del tenant para el DID Hedera.

**Ventajas:**
- Sin cambios en KMS ni en `TenantKMSService`

**Desventajas:**
- La especificacion did:hedera NO define `EcdsaSecp256r1VerificationKey2019` (P-256) como tipo soportado
- No compatible con los resolvers y SDKs de did:hedera
- Rompe la conformidad con la especificacion

**Valoracion:** No viable — incompatible con did:hedera.

---

## Tabla comparativa

| Opcion | Tipo de clave | KMS HSM | Compatible did:hedera | Complejidad POC | Para produccion |
|--------|---------------|---------|----------------------|-----------------|-----------------|
| A: Ed25519 KMS | `ECC_NIST_EDWARDS25519` | Si | Total (canonico) | Media | Si |
| B: Ed25519 software | Ed25519 (software) | No (Secrets Manager) | Total (canonico) | Baja | No recomendado |
| C: secp256k1 KMS | `ECC_SECG_P256K1` | Si | Parcial (secundario) | Baja | Compromiso |
| D: P-256 KMS | `ECC_NIST_P256` | Si | No | N/A | No viable |

---

## Decision

**Para la POC (fase inicial): Opcion B — Ed25519 via par de claves software en Secrets Manager.**

**Para produccion (post-POC): Opcion A — Ed25519 via AWS KMS (`ECC_NIST_EDWARDS25519`), gestionado mediante Lambda Node.js dedicada.**

### Justificacion de la decision dual

**POC con Opcion B:**
- La POC debe demostrar el flujo tecnico end-to-end, no la seguridad HSM
- La Opcion B es la mas rapida de implementar y la mas compatible con los SDKs de Hedera
- Permite validar el flujo completo (HCS, DID Document, resolucion, VC) sin bloqueos
- El riesgo de seguridad es aceptable en testnet con claves de prueba

**Produccion con Opcion A + Lambda:**
- AWS KMS soporta Ed25519 de forma nativa (`ECC_NIST_EDWARDS25519`) desde 2023
- Mantiene la invariante de seguridad de Sybol: "las claves privadas nunca salen del HSM"
- La gestion del ciclo de vida de claves se encapsula en una Lambda Node.js dedicada (`kms-key-ed25519`), no en `TenantKMSService` directamente
- Esto permite escalar, testear y desplegar la logica de claves de forma independiente del servicio principal

### Lambdas KMS de produccion — una por tipo de clave

Se crea **una Lambda Node.js por cada tipo de clave soportado** por Sybol. Cada Lambda expone el ciclo de vida completo: `create`, `query`, `delete`. No son POCs — usan el motor KMS directamente.

| Lambda | KeySpec KMS | Algoritmo | Notas |
|--------|-------------|-----------|-------|
| `lambdas/kms-key-ed25519` | `ECC_NIST_EDWARDS25519` | `ED25519_SHA_512` | Ed25519; soporta import externo |
| `lambdas/kms-key-secp256k1` | `ECC_SECG_P256K1` | `ECDSA_SHA_256` | secp256k1 (Bitcoin/Ethereum) |
| `lambdas/kms-key-p256` | `ECC_NIST_P256` | `ECDSA_SHA_256` | P-256; tipo ya en uso en Sybol para JWTs |
| `lambdas/kms-key-rsa` | `RSA_4096` | `RSASSA_PKCS1_V1_5_SHA_256` | RSA; para integraciones legacy |

**Patron de implementacion de cada Lambda:**

```javascript
// handler.js — estructura común a todas las kms-key-* Lambdas
exports.handler = async (event) => {
  const { operation, keyId, tenantId, description } = event;

  switch (operation) {
    case 'create': return await createKey(tenantId, description);
    case 'query':  return await queryKey(keyId);
    case 'delete': return await deleteKey(keyId);
    default: throw new Error(`Unknown operation: ${operation}`);
  }
};
```

### Caso especial: Lambda `kms-key-ed25519` — importacion de material externo

Para casos donde se requiere importar una clave Ed25519 generada externamente (ej. compatibilidad con material existente), la Lambda ejecuta el algoritmo fuera de KMS y carga el material vía `ImportKeyMaterial`:

```javascript
// Generacion fuera de KMS (solo en memoria del proceso Lambda)
const { randomBytes } = require('crypto'); // o @noble/curves/ed25519
const privateKeyBytes = generateEd25519PrivateKey(); // algoritmo externo

// Importacion a KMS
const { ImportToken, PublicKey: wrappingKey } = await kms.getParametersForImport({
  KeyId: keyId,
  WrappingAlgorithm: 'RSAES_OAEP_SHA_256',
  WrappingKeySpec: 'RSA_4096'
});
const encryptedMaterial = wrapWithRSA(privateKeyBytes, wrappingKey);
await kms.importKeyMaterial({ KeyId: keyId, ImportToken, EncryptedKeyMaterial: encryptedMaterial });
// privateKeyBytes se descarta — nunca persiste fuera de la Lambda
```

Para el caso estandar (clave nueva sin material previo), KMS genera el material Ed25519 internamente y no es necesario el flujo de import.

### Firma Ed25519 con KMS en TenantKMSService

Cuando `businessLogic` necesite firmar con una clave Ed25519 de KMS, usara:

```javascript
// Ed25519 KMS requiere MessageType: RAW (no digest)
const signCommand = new SignCommand({
  KeyId: kmsKeyId,
  Message: rawMessageBytes,
  SigningAlgorithm: 'ED25519_SHA_512',
  MessageType: 'RAW'
});
```

Esta extension se implementa como metodo separado en `TenantKMSService` para no afectar la firma JWT existente (ECDSA P-256).

---

## Estado actual de despliegue (dev/testnet)

La configuración activa en `businesslogic-dev` usa **Opción B** para las claves DID de tenant (Secrets Manager) y tiene el operador Hedera configurado como variable de entorno en la Lambda:

```
HEDERA_NETWORK=testnet
HEDERA_OPERATOR_ID=0.0.8570019
HEDERA_OPERATOR_KEY=0x4aa1...   ← env var en Lambda (testnet)
HEDERA_KEY_TYPE=ecdsa
```

> ⚠️ **Warning — producción:**
> `HEDERA_OPERATOR_KEY` es una clave privada que da acceso a la cuenta operadora de Hedera (la que paga las transacciones HCS). En el entorno dev/testnet se acepta como variable de entorno Lambda porque es una cuenta de prueba sin valor real.
>
> **Antes de pasar a producción esta clave debe migrarse a AWS Secrets Manager** (o AWS KMS si se usa una cuenta Hedera con clave Ed25519 compatible). El patrón de lectura desde Secrets Manager ya está implementado en `hederaDid.service.js` para las claves de tenant y puede replicarse directamente en `hederaClient.js`:
>
> ```javascript
> // hederaClient.js — versión producción
> const { SecretsManagerClient, GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');
>
> async function buildClient() {
>   const sm = new SecretsManagerClient({ region: process.env.AWS_REGION || 'eu-west-1' });
>   const { SecretString } = await sm.send(
>     new GetSecretValueCommand({ SecretId: 'hedera/operator/mainnet' })
>   );
>   const { operatorId, operatorKey, keyType } = JSON.parse(SecretString);
>   // ... resto igual
> }
> ```
>
> El secreto debe seguir el patrón de naming existente: `hedera/operator/{network}`.

---

## Consecuencias

### Positivas
- La POC puede arrancar rapidamente con claves software
- La via hacia produccion esta claramente definida y es tecnicamente viable
- Las Lambdas KMS encapsulan toda la gestion de claves: bajo acoplamiento, facil de testear y desplegar
- Un modelo uniforme de ciclo de vida para todos los tipos de clave soportados

### Negativas / Compromisos
- La POC usa un nivel de seguridad inferior (Secrets Manager vs KMS HSM)
- Cuatro Lambdas adicionales a mantener (una por tipo de clave)
- Dos tipos de clave Ed25519 para DIDs y ECDSA P-256 para JWTs implica gestion de multiples claves por tenant

---

## Referencias

- [AWS KMS Key Spec Reference](https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-choose-key-spec.html)
- [AWS KMS CreateKey API](https://docs.aws.amazon.com/kms/latest/APIReference/API_CreateKey.html)
- [Hedera Keys and Signatures](https://docs.hedera.com/hedera/core-concepts/keys-and-signatures)
- [HIP-222: Support ECDSA(secp256k1) keys](https://hips.hedera.com/hip/hip-222)
- [Meeco/hedera-did-method — Especificacion](https://github.com/Meeco/hedera-did-method)
- `services/businessLogic/src/lib/tenantKmsService.js` — Implementacion actual de KMS
- `services/businessLogic/src/persistence/kms/signing.js` — Interfaz de firma KMS
- `docs/poc/spec-hedera-did-poc.md` — Especificacion completa de la POC
