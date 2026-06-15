# ADR-hedera-003: Ubicacion de la logica DID Hedera en la arquitectura de servicios de Sybol

**Estado:** Aceptado
**Fecha:** 2026-03-30
**Autores:** Equipo Sybol
**Rama:** `feature/eddera-poc`

---

## Contexto

La logica de integracion con Hedera (creacion de HCS topics, publicacion de DID Documents, resolucion via mirror node) debe ubicarse en algun servicio o componente de la arquitectura de Sybol. Esta decision impacta en la cohesion del codigo, la separacion de responsabilidades, el coste de mantenimiento y la facilidad de despliegue.

### Arquitectura de servicios actual (relevante para la decision)

Del analisis del repositorio:

| Servicio | Responsabilidad | Stack | Observacion |
|---------|----------------|-------|-------------|
| `services/businessLogic` | Logica de negocio, emision de VCs, gestion de DIDs (did:sybol), JWT/KMS | Node.js, Express | Ya gestiona DIDs y credenciales; contiene `TenantKMSService`, `JWTCredentialManager`, `didValidationUtils` |
| `services/bm` | Blockchain Manager — transacciones EVM, signers KMS para EVM, gestion de contratos | Node.js, Express | Especializado en EVM (ethers.js, `KmsSigner`, `chainRegistry`); NO tiene logica DID; es un servicio interno |
| `services/svault` | Gestion segura de secretos/vault | Node.js | Almacenamiento de material sensible |
| `services/backoffice` | API del panel de administracion | Node.js | Frontend backend; delega a businessLogic |
| `services/catalog` | Gestion de catalogo de credenciales | Node.js | Dominio especifico |
| `lambdas/` | Funciones Lambda puntuales | Node.js | `setupAlastriaIdentity` (existente, para Alastria EVM) |

### Opciones de ubicacion

Las opciones viables son:

1. **`services/businessLogic`** — Añadir modulo Hedera DID dentro del servicio de logica de negocio
2. **`services/bm`** — Ampliar el Blockchain Manager con soporte Hedera
3. **Nuevo servicio `hedera-did`** — Microservicio dedicado exclusivamente a Hedera DID
4. **Lambda nueva** — Funcion Lambda para operaciones Hedera DID (similar a `setupAlastriaIdentity`)

---

## Opciones evaluadas

### Opcion 1 — `services/businessLogic` (recomendada)

**Descripcion:** Añadir un modulo `hedera/` dentro de `services/businessLogic/src/`, integrando la logica de Hedera DID junto a la gestion de DIDs existente.

**Justificacion tecnica:**
- `businessLogic` ya es el dueno del dominio DID en Sybol: contiene `didValidationUtils.js`, `jwtCredentialManager.js`, `tenantKmsService.js` y el flujo de emision de VCs
- La creacion de un did:hedera es logicamente equivalente a la creacion de un did:sybol — mismo dominio, mismos actores (tenant, issuer), mismo contexto de KMS
- El flujo completo (provisionar clave → crear topic HCS → publicar DID Document → emitir VC) ya tiene su mitad posterior implementada en `businessLogic`
- Evita dependencia inter-servicio para operaciones que conceptualmente pertenecen al mismo dominio
- Menor overhead de despliegue y comunicacion (sin llamadas HTTP adicionales)

**Estructura propuesta:**
```
services/businessLogic/src/hedera/
├── hederaDid.service.js      ← orquestacion: crear topic, registrar DID, resolver DID
├── hederaDid.utils.js        ← parse del DID string, extraccion base58/topicId
└── hederaClient.js           ← factory del cliente @hashgraph/sdk por tenant
services/businessLogic/src/controllers/
└── hederaDid.controller.js   ← endpoints REST para la POC
services/businessLogic/src/routes/
└── hederaDid.routes.js       ← definicion de rutas
```

**Ventajas:**
- Maxima cohesion — toda la logica DID en un solo servicio
- Sin nuevas dependencias inter-servicio
- Reutiliza directamente `TenantKMSService`, `JWTCredentialManager` y el middleware de autenticacion existente
- Menor esfuerzo de implementacion y despliegue para la POC
- La emision de VCs con did:hedera funciona con el `JWTCredentialManager` existente sin modificaciones, solo registrando el nuevo DID

**Desventajas:**
- Añade dependencias npm de Hedera (`@hashgraph/sdk`) al servicio `businessLogic`, que actualmente no tiene dependencias blockchain
- Potencial aumento del tamano del bundle/imagen Docker

**Valoracion:** Alta — opcion recomendada para la POC y produccion inicial.

### Opcion 2 — `services/bm` (Blockchain Manager)

**Descripcion:** Ampliar `bm` con un modulo Hedera, siguiendo el patron que tiene para EVM.

**Justificacion:**
- `bm` ya abstrae la interaccion con redes blockchain (EVM)
- Podria establecerse como el "multi-chain manager" que soporta tanto EVM como Hedera

**Por que NO se selecciona para la POC:**
- `bm` esta completamente orientado a EVM: `chainRegistry.service.js`, `contract.service.js`, `transaction.service.js`, `KmsSigner`, etc.
- Hedera NO es una red EVM — usa el SDK nativo de Hedera, no ethers.js ni contratos Solidity
- Añadir Hedera en `bm` rompe su abstraccion actual y requiere refactorizacion significativa
- La logica DID (crear/resolver DIDs) es semanticamente distinta de "ejecutar transacciones blockchain"
- Crearia una dependencia nueva: `businessLogic` → `bm` → Hedera, cuando `businessLogic` ya puede ir directamente a Hedera
- Mayor overhead para la POC sin beneficio claro

**Valoracion:** Media — viable a largo plazo si `bm` evoluciona a multi-chain manager, pero no para la POC.

### Opcion 3 — Nuevo microservicio `hedera-did`

**Descripcion:** Crear un nuevo servicio dedicado exclusivamente a operaciones Hedera DID.

**Ventajas:**
- Separacion de responsabilidades maxima
- Escala de forma independiente

**Por que NO se selecciona:**
- Overhead de infraestructura desproporcionado para una POC
- Requiere nuevo repositorio/directorio, Dockerfile, CI/CD, service discovery
- La logica Hedera DID no justifica un microservicio separado en esta etapa
- Fragmenta la logica DID que actualmente reside en `businessLogic`

**Valoracion:** Baja para POC; consideracion futura si el volumen lo justifica.

### Opcion 4 — Lambda nueva (similar a setupAlastriaIdentity)

**Descripcion:** Crear una Lambda `setupHederaDID` analoga a la Lambda `setupAlastriaIdentity` existente.

**Ventajas:**
- Patron conocido en el proyecto
- Sin impacto en servicios existentes

**Por que NO se selecciona para la logica DID:**
- Las Lambdas del proyecto son para operaciones puntuales de setup one-shot
- La resolucion de DIDs requiere un endpoint REST persistente, no una Lambda
- El patron Lambda es adecuado para registro inicial pero no para el ciclo completo de gestion de DIDs
- No reutilizaria la infraestructura de autenticacion de `businessLogic`

**Valoracion:** Baja para el ciclo DID completo. Sin embargo, **las Lambdas son el patron correcto para la gestion de claves KMS** — ver §5.2 del spec y ADR-002 para las Lambdas `kms-key-*`.

### Componente adicional — Contenedor proxy Hedera

**Descripcion:** Un contenedor Docker dedicado que actua como proxy de red hacia Hedera. Todo el trafico de `businessLogic` hacia Hedera (consensus nodes y mirror node) pasa por este proxy. El cambio entre testnet y mainnet se realiza exclusivamente via configuracion del contenedor.

**Por que se añade:**
- Permite cambiar de testnet a mainnet modificando una sola variable de entorno (`HEDERA_NETWORK`)
- Encapsula el cliente `@hashgraph/sdk` y las credenciales de operador Hedera fuera de `businessLogic`
- Facilita pruebas: en desarrollo apunta a testnet; en produccion a mainnet sin cambiar codigo
- Centraliza el manejo de reconexiones y errores de red hacia Hedera
- Permite inspeccionar y depurar el trafico hacia Hedera en un punto unico

**Diferencia con Opcion 3 (microservicio):** El proxy no tiene logica de dominio — solo enruta peticiones HTTP internas hacia la red Hedera correcta. No almacena estado ni tiene base de datos. Es un componente de infraestructura, no un servicio de negocio.

**Valoracion:** Recomendado para produccion. Para la POC puede omitirse y conectar directamente a testnet desde `businessLogic`.

```yaml
# Variable de entorno que controla toda la red
HEDERA_NETWORK: testnet   # cambiar a "mainnet" para produccion
```

---

## Tabla comparativa

| Opcion | Cohesion DID | Esfuerzo POC | Reutiliza infraestructura | Impacto arquitectura | Recomendacion |
|--------|-------------|-------------|--------------------------|---------------------|---------------|
| businessLogic | Alta | Bajo | Total | Minimo | Seleccionada |
| bm | Media | Alto | Parcial | Medio-alto | Largo plazo |
| Nuevo servicio | Alta | Muy alto | Minima | Alto | No POC |
| Lambda | Baja | Medio | Parcial | Bajo | No completo |

---

## Decision

**Logica DID Hedera en `services/businessLogic` (modulo `hedera/`) + contenedor proxy Hedera + Lambdas KMS por tipo de clave.**

La arquitectura completa de produccion distribuye responsabilidades entre tres capas:

| Componente | Responsabilidad |
|-----------|----------------|
| `services/businessLogic` | Logica de dominio DID — orquestacion, API REST, autenticacion, emision de VCs |
| `hedera-proxy` (contenedor) | Infraestructura de red — enrutamiento a testnet/mainnet, encapsulacion del SDK Hedera |
| `lambdas/kms-key-*` (x4) | Ciclo de vida de claves — create/query/delete para cada tipo de clave KMS soportado |

### Justificacion

`businessLogic` es el servicio dueno del dominio DID en Sybol. La logica de DID Hedera pertenece aqui por coherencia con el dominio existente (did:sybol, JWTs, VCs). El proxy Hedera y las Lambdas KMS son componentes de infraestructura que separan la red y las claves del dominio de negocio.

Esta separacion permite:
- Cambiar de testnet a mainnet modificando solo la config del proxy
- Desplegar, testear y escalar la gestion de claves de forma independiente
- Auditar cada operacion de firma o ciclo de vida de clave en un punto centralizado

---

## Consecuencias

### Positivas
- Minimo tiempo de implementacion para la POC (businessLogic conecta directo a testnet)
- El flujo de emision de VCs con did:hedera reutiliza `JWTCredentialManager` sin modificacion
- Un solo servicio para auditar y mantener toda la logica DID
- El proxy permite el switching testnet/mainnet sin tocar codigo
- Las Lambdas KMS son componentes de produccion reutilizables por cualquier servicio Sybol

### Negativas / Compromisos
- `businessLogic` adquiere dependencias de `@hashgraph/sdk` (aumento de tamano de imagen) — mitigado a largo plazo delegando al proxy
- Cuatro Lambdas adicionales a mantener
- Un contenedor adicional en la infraestructura (hedera-proxy)

### Plan de migracion futuro (post-POC)

Una vez validada la POC, `businessLogic` puede delegarle todas las llamadas al SDK Hedera al proxy (en lugar de usar el SDK directamente), eliminando la dependencia de `@hashgraph/sdk` del servicio principal. El modulo `hedera/` quedaría como cliente HTTP del proxy.

---

## Referencias

- `services/businessLogic/src/lib/tenantKmsService.js` — KMS service actual
- `services/businessLogic/src/utils/jwtCredentialManager.js` — VC emission service
- `services/businessLogic/src/utils/didValidationUtils.js` — DID validation utilities
- `services/bm/src/services/signer.service.js` — EVM signer service (patron bm)
- `services/bm/src/services/chainRegistry.service.js` — Chain registry (patron bm)
- `docs/poc/spec-hedera-did-poc.md` — Especificacion completa de la POC
- `docs/poc/adr-hedera-002-key-management.md` — Decision sobre gestion de claves
