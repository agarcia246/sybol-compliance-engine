# BusinessLogic Service — Architecture

## Propósito

Servicio HTTP/Lambda que implementa la lógica de negocio central de la plataforma Sybol: emisión de Verifiable Credentials (VCs), gestión del ciclo de vida de credenciales, presentaciones, contactos, actividades y procesamiento batch de credenciales desde Excel.

## Componentes

```
businessLogic/
└── src/
    ├── app.js              ← Express app
    ├── server.js           ← HTTP entry (local)
    ├── lambda.js           ← Lambda handler adapter
    ├── controllers/
    │   ├── activityController.js
    │   ├── batchController.js
    │   ├── contactController.js
    │   ├── credentialController.js
    │   ├── credentialRequestController.js
    │   ├── delegateController.js
    │   ├── presentationController.js
    │   └── presentationRequestController.js
    ├── routes/             ← Definición de rutas Express
    ├── handlers/           ← Handlers SQS para procesamiento asíncrono
    ├── services/           ← Lógica de negocio por dominio
    ├── models/             ← Modelos de datos y esquemas
    ├── repositories/       ← Acceso a datos (PostgreSQL)
    ├── persistence/        ← ORM / connection pool
    ├── middleware/         ← Auth, error handling, tenant isolation
    ├── validators/         ← Validación de requests
    ├── lib/                ← Integraciones externas (bm, catalog)
    ├── config/             ← Configuración por entorno
    └── utils/              ← Logging, helpers
```

## Dominios de negocio

| Dominio | Responsabilidad |
|---|---|
| **Credentials** | Emisión y gestión de VCs (W3C) — flujo DIDless |
| **Batch** | Procesamiento masivo desde Excel (SQS + S3) |
| **Presentations** | Generación y verificación de VPs |
| **Contacts** | Gestión de contactos entre tenants |
| **Activities** | Registro de actividades del holder |
| **Delegates** | Delegación de capacidades entre tenants |
| **Requests** | Solicitudes de credenciales y presentaciones |

## Flujo de emisión DIDless

```
HTTP Request → Controller → Service
                                ↓
                    Catalog (verificar esquema VC)
                                ↓
                    BlockchainManager (anclar hash)
                                ↓
                    PostgreSQL (persistir VC)
                                ↓
                    EventBridge → Propagate (notificar)
```

## Procesamiento batch

Según [ADR-0003](../decisions/0003-s3-tenant-data-bucket.md) y [ADR-0004](../decisions/0004-sqs-handlers-in-businesslogic.md):
- Fichero Excel sube a **S3** por bucket de tenant.
- Evento S3 dispara mensaje en **SQS**.
- Handler SQS procesa filas con idempotencia ([ADR-0008](../decisions/0008-batch-idempotency-strategy.md)).

## Dependencias externas

- **AWS Cognito**: Auth multi-tenant.
- **AWS SQS**: Cola de procesamiento batch.
- **AWS S3**: Almacenamiento de ficheros Excel por tenant.
- **BlockchainManager (bm)**: Anclaje on-chain de credenciales.
- **Catalog**: Validación de esquemas de credenciales.
- **PostgreSQL (RDS)**: Persistencia principal.
- **EventBridge → Propagate**: Notificación de nuevas credenciales.

## Documentación relacionada

- [Batch SPEC](../specs/batch-spec.md)
- [API Reference](../api/businesslogic-api.md)
- [ADRs (8)](../decisions/)
