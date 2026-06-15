# propagate — Propagate Service

Servicio HTTP/Lambda que propaga objetos verificables (Verifiable Credentials, Presentations) entre tenants y sistemas externos mediante AWS EventBridge.

## Responsabilidades

- Recibir solicitudes de propagación de VCs y VPs.
- Publicar eventos en EventBridge para consumo por otros servicios.
- Validar la autenticidad y formato de los objetos recibidos.
- Gestionar la autenticación multi-tenant (Cognito).

## API

→ [api/propagate-api.md](api/propagate-api.md)

## Decisiones arquitectónicas

→ [decisions/README.md](decisions/README.md)

## Especificaciones

→ [specs/README.md](specs/README.md)

## Arquitectura

→ [architecture/service-architecture.md](architecture/service-architecture.md)
