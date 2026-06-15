# propagate Service — Architecture Decision Records

No hay ADRs específicos del servicio propagate registrados aún.

## ADRs globales relacionados

| ADR | Título |
|---|---|
| [0001 global](../../global/decisions/0001-aws-cognito-authentication.md) | AWS Cognito Authentication |
| [0002 global](../../global/decisions/0002-serverless-architecture.md) | Serverless Architecture |
| [0004 global](../../global/decisions/0004-w3c-verifiable-credentials.md) | W3C Verifiable Credentials |

## ADRs de servicios relacionados

| ADR | Título |
|---|---|
| [0005 businessLogic](../../services/businessLogic/decisions/0005-async-auth-propagation.md) | Async Auth Propagation |

## Decisiones pendientes de documentar

- Estrategia de reintentos de propagación en caso de fallo.
- Fan-out pattern: propagación a múltiples tenants simultáneamente.
- Esquema de eventos en EventBridge (event bus naming, rules).
