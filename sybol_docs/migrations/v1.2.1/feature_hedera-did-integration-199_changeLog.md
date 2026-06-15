# Changelog — feature/hedera-did-integration-199

**Version:** v1.2.1
**Branch:** `feature/hedera-did-integration-199`
**Base:** `develop`
**Date:** 2026-04-21

---

## 1. Base de datos

### Nuevas migraciones

| Fichero | Servicio | Descripcion |
|---------|----------|-------------|
| `001_add_default_did_method.sql` | backoffice | Agrega columna `default_did_method` a la tabla `entities` para persistir la preferencia de metodo DID por tenant. |
| `003_create_hedera_credential_anchors.sql` | businessLogic | Crea tabla `hedera_credential_anchors` para almacenar el anclaje HCS (topic_id, sequence_number, chunk_info) de credenciales emitidas con `did:hedera`. |
| `004_create_tenant_settings.sql` | businessLogic | Crea tabla `tenant_settings` (clave/valor por tenant) utilizada por la API de settings. |

### Cambios en vistas y esquema existente

- Correccion de vistas de catalogo (`forms_with_schema`): se ejecuta DROP/RECREATE antes del DROP COLUMN para evitar dependencias rotas (`8f4ec35`, `e8613e2`).
- Eliminacion de la columna `cs.notes` de la query `getById` porque no existe en DEV (`c562463`).

---

## 2. Infraestructura frontal (webApps/wwc)

### Nuevas funcionalidades

- **Selector de metodo DID** en Settings — permite al usuario elegir `did:web` o `did:hedera` como metodo por defecto; se persiste en BD via API de settings (`cbf4b21`, `ad7f470`).
- **Copia de DID Document** — boton "Copy DID Document" en la seccion Identity de Settings (`a6e4636`).
- **Copia de JWT** — boton "Copy JWT" en el InfoDrawer de credenciales (`da9db21`).
- **Red DID y enlace HashScan** — el InfoDrawer muestra la red Hedera y un enlace a HashScan para credenciales ancladas (`7e83dd1`).
- **Red DID en modales** — Issue Modal y Request Modal muestran la red asociada al DID seleccionado (`25f9673`).
- **Banner de credenciales no propagadas** — aviso visual cuando una credencial no ha sido propagada al destinatario (`81db417`).
- **Upload de logo personalizado** — subida de logo del tenant desde Settings con almacenamiento en S3 via Cognito (`3a9af83`, `365b69c`, `375b528`).
- **Tab de gestion DID/KMS** — nueva pestana en Settings para listar claves KMS y opciones de clave Hedera, con soft-delete y exportacion de clave publica (`7bdd4e8`, `d24facd`).
- **display_name** del tenant — nuevo setting de nombre visible del emisor que aparece en las credenciales (`20c9b77`).

### Correcciones

- Resolucion de nombres de issuer/subject para `did:hedera` en listas de credenciales y en InfoDrawer (`4eccfa7`, `952c245`).
- Cumplimiento i18n: todos los textos visibles pasan por la funcion de traduccion; estandarizacion de colores CSS (`c0c9e92`).
- Reemplazo de etiquetas HTML crudas por componentes MUI `Typography` (`e556d1c`).
- Fix de contactos que no se renderizan por double-unwrap de respuesta axios + parametros incorrectos (`93010b3`, `bc65504`, `d70f961`).
- Fallback de `USER_POOL_ID` en configuracion de staging (`d47e733`).

---

## 3. Infraestructura backend

### services/shared (nueva libreria compartida)

- Creacion de `services/shared` con modulos reutilizables: DID factory, payload builders (credential, presentation, presentationRequest), resolvers (`didResolver`, `didWebResolver`, `hederaDidResolver`), algoritmos de clave y mapa de idiomas (`3aec390`).
- Integracion en todos los servicios via symlinks + actualizacion de Dockerfiles y scripts de deploy (`1c92a9e`).
- Refactor de businessLogic para importar desde shared library en lugar de utils locales duplicados (`b7b4755`).

### services/businessLogic

#### Nuevas funcionalidades

- **API de settings** — `GET/POST /api/bl/settings` con scope por tenant para almacenar preferencias (metodo DID, display_name, etc.) (`ffe7811`).
- **Dispatcher universal de DID** — `didResolver.js` que enruta a `did:web` o `did:hedera` segun el prefijo del DID (`6eebb28`).
- **Validadores multi-metodo** — actualizacion de validadores para aceptar DIDs `did:hedera` ademas de `did:web` (`86d783a`).
- **Firma EdDSA (Ed25519)** — soporte de firma EdDSA via KMS para claves Ed25519 utilizadas por Hedera (`39319cd`).
- **Mapeo JWK Ed25519/EdDSA** — extension del mapping de algoritmos JWK para incluir Ed25519 (`0a1648b`).
- **Anclaje HCS** — registro de credenciales en Hedera Consensus Service (HCS), sincrono y transaccional con la creacion de la credencial (`1e90f99`, `4a345e1`).
- **Reensamblaje de chunks HCS** — lectura de mensajes HCS fragmentados usando `chunk_info.number` en lugar del orden de consenso (`4efe561`).
- **Creacion de did:web** — endpoint `POST /api/bl/web/setup-did` para crear documentos `did:web` desde businessLogic (`30c2727`).
- **Identidad W3C VC 2.0 multilingue** — nombre y descripcion del emisor en multiples idiomas dentro del DID Document (`861e52a`).
- **.well-known en DID Documents** — inclusion automatica + auto-refresh al cambiar la configuracion de issuer (`d57d9c9`).
- **Filtro multi-DID** — busqueda de credenciales por issuer/subject con multiples DIDs en una sola query, con paginacion server-side (`d9425ba`).
- **Centralizacion de algoritmos JWT** — mapeo unificado de algoritmos JWT con fix para `ED25519_SHA_512` (`65c1e4c`).
- **Migracion a Lambda KMS unificada** — Hedera Option 3 migrado a la Lambda KMS unificada (`6195815`).
- **Fallback KMS GetPublicKey** — para DID Documents W3C-pure cuando no hay DID registrado (`3fcfb38`).

#### Correcciones

- `publishCredentialHash` retorna datos correctamente; `Credential.create` persiste el anchor (`46d78ee`).
- Middleware de auth anadido a rutas `/api/bl/settings` (`5695c44`).
- Refresh de DID sincrono en el controller de settings (`d682242`).
- Correccion de `PATCH` a `POST` para approve/reject de credential-requests (`ce3bee7`).
- Operaciones KMS via STS exclusivamente + manejo de mensajes HCS fragmentados (`39fe3d5`).
- Lectura de DID Document de Hedera desde tenant DB; escritura desde backoffice con pool propio (`e556d1c3`).
- Correccion de paths de API para endpoints KMS y Hedera (`710b402`).

### services/backoffice

- Actualizacion del DID document service para usar shared library (`04fb61f`).
- Actualizacion del entity repository/service para soportar `default_did_method` (`20c806e`).

### services/propagation

- Resolver DID multi-metodo con soporte `did:hedera` (`3ea2bf8`).
- Exposicion de estado `not-propagated` en respuesta `/send` (`8a7b488`).

### Lambdas KMS

- **4 Lambdas individuales por tipo de clave** (fase inicial): `kms-key-ed25519`, `kms-key-p256`, `kms-key-secp256k1`, `kms-key-rsa` — cada una con operaciones create/list/delete/query (`cae05d6`, `558557f`, `432317c`, `13ee90b`).
- **Lambda unificada `kms-keys`** — refactor que consolida las 4 Lambdas en una sola con prefijo `alias/tenant/` y tags estandarizados (`06604b4`, `43d5925`, `b626b15`).
- **Permisos de firma** — `TenantRole-admin` obtiene acceso de firma en claves de identidad (`e25c0e8`).

### Hedera (servicio y proxy)

- **HederaDID service** — servicio POC con claves software para operaciones DID en Hedera Testnet (`7c1a2b1`).
- **hederaClient factory** y utilidades DID (`339cc1d`).
- **Hedera proxy container** (Fargate) para comunicacion con la red Hedera (`5c05b2e`, eliminado posteriormente `0f24810`).
- **Integracion Hedera Testnet** completa — DID, KMS Lambdas, despliegue Fargate (`6dc40be`).

### Deploy y operaciones

- Script `reset-dev.sh` para limpieza de datos en DEV con recreacion de documentos `did:web` (`d7a8a1e`, `f926634`).
- Smoke tests unificados para DEV y staging con nuevos endpoints (`6c49747`, `c493bc3`, `2cb3d0b`).
- Fix de flujo de deploy a staging (`694b519`).
- Workflow CI: adicion de tenants `alsa`, `dataie`, `solred` al deploy de staging (`e740cf2`).

### Documentacion tecnica

- SERVICE_SPEC unificado para Hedera DID (`f272c87`).
- ADRs: HED-004 a HED-011 cubriendo multi-method dispatch, HCS anchoring, JWT signing algorithm, default DID method storage, KMS fallback, KMS key policy, DID document factory, y payload builders (`b5f4994`, `865abde`).
- Documentacion de migracion v1.2.0 staging y eliminacion de Lambda `did-resolver` en DEV (`d3bba61`, `22c5efe`).
