# Backoffice Service — Architecture

## Propósito

Servicio HTTP/Lambda que expone la API de administración para la plataforma Sybol. Permite gestionar tenants, usuarios, contratos inteligentes, DIDs y KYB desde el panel de backoffice.

## Componentes

```
backoffice/
└── src/
    ├── app.js              ← Express app configuration
    ├── server.js           ← HTTP server (local dev)
    ├── lambda.js           ← Lambda handler adapter
    ├── controllers/
    │   ├── did-document.controller.js
    │   ├── email.controller.js
    │   ├── kyb.controller.js
    │   ├── referral.controller.js
    │   └── smart-contract.controller.js
    ├── routes/
    │   ├── did-document.routes.js
    │   ├── email.routes.js
    │   ├── kyb.routes.js
    │   ├── referral.routes.js
    │   └── smart-contract.routes.js
    ├── services/           ← Lógica de negocio
    ├── repositories/       ← Acceso a datos (PostgreSQL)
    ├── persistence/        ← ORM / DB models
    ├── middleware/         ← Auth, error handling
    ├── config/             ← Variables y configuración
    ├── lib/                ← Utilidades internas
    └── utils/              ← Helpers
```

## Flujo principal

```
API Gateway → Lambda Handler → Express Router → Controller → Service → Repository → PostgreSQL
                                                                      ↕
                                                              Cognito (auth)
                                                              BlockchainManager (DIDs, contratos)
```

## APIs expuestas

| Módulo | Prefijo ruta | Descripción |
|---|---|---|
| DID Document | `/did-document` | Alta y gestión de DIDs para tenants |
| Email | `/email` | Envío de notificaciones |
| KYB | `/kyb` | Know Your Business — verificación corporativa |
| Referral | `/referral` | Sistema de invitación de tenants |
| Smart Contract | `/smart-contract` | Registro y gestión de contratos inteligentes |

## Dependencias externas

- **AWS Cognito**: Autenticación y autorización multi-tenant.
- **PostgreSQL (RDS)**: Almacenamiento principal.
- **Blockchain Manager (bm)**: Firma y registro de DIDs y contratos.

## Documentación relacionada

- [API Reference](../api/backoffice-api.md)
- [Auth Config](../specs/auth-config.md)
- [ADRs globales](../../global/decisions/)
