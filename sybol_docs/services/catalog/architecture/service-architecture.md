# Catalog Service — Architecture

## Propósito

Servicio HTTP/Lambda que actúa como repositorio centralizado de esquemas de datos (Claims, Documents, Forms) y gestión de compliance regional. Define los tipos de credenciales que la plataforma puede emitir.

## Componentes

```
catalog/
└── src/
    ├── app.js              ← Express app
    ├── server.js           ← HTTP entry (local)
    ├── lambda.js           ← Lambda handler adapter
    ├── controllers/
    │   ├── claimController.js
    │   ├── complianceRegionController.js
    │   ├── documentController.js
    │   └── formController.js
    ├── routes/             ← Rutas Express
    ├── repositories/       ← Acceso a datos (PostgreSQL)
    ├── persistence/        ← ORM / connection pool
    ├── middleware/         ← Auth, error handling
    ├── lib/                ← Integraciones externas
    └── config/             ← Configuración por entorno
```

## Dominios

| Dominio | Descripción |
|---|---|
| **Claims** | Esquemas de atributos individuales de una credencial |
| **Documents** | Tipos de documentos verificables completos |
| **Forms** | Formularios de captura asociados a documentos |
| **ComplianceRegion** | Restricciones de compliance por región geográfica |

## Modelo de datos

Los esquemas siguen el estándar **W3C Data Model** ([ADR-0006 global](../../global/decisions/0006-catalog-w3c-data-model-alignment.md)):

```
Document
  └── Claims[]
        └── Form fields[]
```

Ver esquemas JSON en [specs/schemas/](../specs/schemas/).

## Flujo de consulta

```
BusinessLogic / BackOffice → HTTP GET /catalog/documents/:type
                                     ↓
                              CatalogController
                                     ↓
                              CatalogRepository (PostgreSQL)
                                     ↓
                              Devuelve esquema + claims + form
```

## Dependencias externas

- **AWS Cognito**: Autenticación multi-tenant.
- **PostgreSQL (RDS)**: Almacenamiento de esquemas.

## Documentación relacionada

- [Data Model SPEC](../specs/data-model-spec.md)
- [API Reference](../api/catalog-api.md)
- [Schemas JSON](../specs/schemas/)
- [ADR-0006 global — W3C alignment](../../global/decisions/0006-catalog-w3c-data-model-alignment.md)
