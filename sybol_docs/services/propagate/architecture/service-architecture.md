# Propagate Service — Architecture

## Propósito

Servicio HTTP/Lambda que propaga objetos verificables (Verifiable Credentials, Presentations) entre tenants y hacia sistemas externos. Actúa como bus de distribución de eventos de credenciales, publicando en **AWS EventBridge**.

## Componentes

```
propagate/
└── src/
    ├── app.js          ← Express app
    ├── server.js       ← HTTP entry (local)
    ├── lambda.js       ← Lambda handler adapter
    ├── controllers/    ← Controladores de propagación
    ├── routes/         ← Rutas Express
    ├── middleware/     ← Auth, validación, error handling
    ├── models/         ← Modelos de datos
    ├── validators/     ← Validación de requests
    ├── lib/            ← Integraciones externas
    └── utils/          ← Logging, helpers
```

## Flujo de propagación

```
Llamada desde BusinessLogic / BackOffice
              ↓
    PropagateController
              ↓
    Validación del objeto VC/VP
              ↓
    AWS EventBridge (publicar evento)
              ↓
    Consumidores registrados (otros servicios / sistemas externos)
```

## Autenticación

Según [ADR-0005 businessLogic — Async Auth Propagation](../../services/businessLogic/decisions/0005-async-auth-propagation.md):
- El tenant se propaga de forma asíncrona vía claims del token Cognito.
- El servicio valida el token antes de procesar cualquier solicitud.

## Dependencias externas

- **AWS Cognito**: Autenticación multi-tenant.
- **AWS EventBridge**: Bus de eventos para distribución asíncrona.
- **AWS Secrets Manager**: Credenciales de sistemas externos (si aplica).
- **AWS STS**: Assume role cross-account (si aplica).

## Documentación relacionada

- [API Reference](../api/propagate-api.md)
- [ADRs del servicio](../decisions/)
