# svault Service — Architecture Decision Records

No hay ADRs específicos del servicio svault registrados aún.

## ADRs globales relacionados

| ADR | Título |
|---|---|
| [0001 global](../../global/decisions/0001-aws-cognito-authentication.md) | AWS Cognito Authentication |
| [0002 global](../../global/decisions/0002-serverless-architecture.md) | Serverless Architecture |

## ADRs de servicios relacionados

| ADR | Título |
|---|---|
| [0003 bm](../../services/bm/decisions/0003-transaction-signing-key-management.md) | Transaction Signing Key Management |

## Decisiones pendientes de documentar

- Estrategia de rotación de CMKs (Customer Managed Keys) en KMS.
- Modelo de permisos IAM (una CMK por tenant vs. una CMK compartida con alias).
- Auditoría de operaciones criptográficas (CloudTrail + alertas).
