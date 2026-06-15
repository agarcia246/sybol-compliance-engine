# Global — Documentación Transversal

Contiene toda la documentación que aplica al proyecto Sybol en su conjunto, independientemente del servicio o componente específico.

## Secciones

| Sección | Descripción |
|---|---|
| [overview/](overview/) | Visión general del proyecto, conceptos clave, glosario |
| [architecture/](architecture/) | Arquitectura del sistema, componentes, datos, despliegue, seguridad |
| [decisions/](decisions/) | ADRs globales — decisiones arquitectónicas transversales |
| [api/](api/) | Contratos API transversales (autenticación, manejo de errores) |
| [development/](development/) | Guías para desarrolladores: setup, estándares, testing, contribución |
| [operations/](operations/) | Operaciones: despliegue, infraestructura, monitoring, multi-tenancy |
| [security/](security/) | Seguridad: auth, autorización, criptografía, compliance |
| [appendix/](appendix/) | Recursos AWS, variables de entorno, FAQ, referencias |

## ADRs globales

| ADR | Título | Estado |
|---|---|---|
| [0001](decisions/0001-aws-cognito-authentication.md) | AWS Cognito Authentication | Accepted |
| [0002](decisions/0002-serverless-architecture.md) | Serverless Architecture | Accepted |
| [0003](decisions/0003-multi-tenant-database-design.md) | Multi-Tenant Database Design | Accepted |
| [0004](decisions/0004-w3c-verifiable-credentials.md) | W3C Verifiable Credentials | Accepted |
| [0005](decisions/0005-lambda-vpc-blockchain-connectivity.md) | Lambda VPC Blockchain Connectivity | Accepted |
| [0006](decisions/0006-catalog-w3c-data-model-alignment.md) | Catalog W3C Data Model Alignment | Accepted |
