# Services

Documentación de todos los servicios backend de la plataforma Sybol.

## Catálogo de servicios

| Servicio | Descripción | API | ADRs | SPECs |
|---|---|---|---|---|
| [backoffice](backoffice/) | API de administración — tenants, usuarios, DIDs, KYB | [API](backoffice/api/backoffice-api.md) | [ADRs](backoffice/decisions/) | [specs](backoffice/specs/) |
| [bm](bm/) | Capa de abstracción blockchain (EVM) — firma, contratos, eventos | [OpenAPI](bm/api/openapi.yaml) | [6 ADRs](bm/decisions/) | [SERVICE_SPEC](bm/specs/service-spec.md) |
| [businessLogic](businessLogic/) | Lógica central — emisión VCs, batch, presentaciones, contactos | [API](businessLogic/api/businesslogic-api.md) | [8 ADRs](businessLogic/decisions/) | [Batch SPEC](businessLogic/specs/batch-spec.md) |
| [catalog](catalog/) | Repositorio de esquemas — Claims, Documents, Forms | [API](catalog/api/catalog-api.md) | [ADRs](catalog/decisions/) | [Data Model](catalog/specs/data-model-spec.md) |
| [database](database/) | Herramientas de auditoría de permisos PostgreSQL | — | [ADRs](database/decisions/) | [Business Rules](database/specs/business-rules.md) |
| [iom](iom/) | Identity Object Manager _(en desarrollo)_ | — | [ADRs](iom/decisions/) | — |
| [propagate](propagate/) | Propagación de VCs/VPs entre tenants (EventBridge) | [API](propagate/api/propagate-api.md) | [ADRs](propagate/decisions/) | — |
| [svault](svault/) | Vault criptográfico vía AWS KMS — firma, cifrado | — | [ADRs](svault/decisions/) | — |

## Arquitectura global

→ [docs/global/architecture/](../global/architecture/)

## Ver también

- [API transversal — error-handling](../global/api/error-handling.md)
- [API transversal — authentication](../global/api/authentication.md)
- [ADRs globales](../global/decisions/)
