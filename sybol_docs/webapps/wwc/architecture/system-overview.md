# wwc — Web Wallet Client Architecture

## Propósito

Aplicación React (Create React App) que implementa la interfaz de usuario para el **Wallet Web del ciudadano / holder** en la plataforma Sybol. Permite a los usuarios gestionar sus Verifiable Credentials, contactos, presentaciones, voting y firma digital.

## Estructura de la aplicación

```
wwc/src/
├── app/                ← Configuración de routing y app shell
├── pages/              ← Vistas por módulo funcional
│   ├── Balloting/      ← Votaciones
│   ├── Catalog/        ← Catálogo de documentos
│   ├── CatalogManagement/
│   ├── Contacts/       ← Gestión de contactos entre tenants
│   ├── Dashboard/      ← Panel principal del holder
│   ├── DigitalSignature/ ← Firma digital de documentos
│   ├── Holder/         ← Gestión de credenciales (VCs)
│   ├── Issuer/         ← Panel del emisor de credenciales
│   ├── Search/         ← Búsqueda de contactos/credenciales
│   ├── Settings/       ← Configuración del usuario
│   └── Voting/         ← Módulo de votación (dos tracks)
├── components/         ← Componentes UI reutilizables
├── context/
│   ├── AppContext.js   ← Estado global de la aplicación
│   └── AuthContext.js  ← Estado de autenticación Cognito
├── services/           ← Capa de abstracción de APIs
│   ├── sybol.js        ← API calls a BusinessLogic
│   ├── cognito.js      ← Autenticación AWS Cognito
│   ├── veia.js         ← Integración protocolo VEIA
│   ├── w3c.js          ← Utilidades W3C VC
│   └── voting.js       ← API calls al módulo de voting
├── layouts/            ← Layouts de página
├── helpers/            ← Utilidades y formatadores
├── config/             ← Variables de entorno y configuración
└── utils/              ← Helpers genéricos
```

## Arquitectura de estado

Según [ADR-0003](../decisions/0003-context-api-over-redux.md):
- **Context API** (no Redux) para estado global.
- `AppContext`: datos de aplicación (credenciales, contactos, tenant).
- `AuthContext`: sesión Cognito (tokens, usuario, permisos).

## Módulo de Voting

Arquitectura de dos tracks según [ADR-0004](../decisions/0004-voting-module-two-track-architecture.md):
- **Track digital**: Voto firmado con clave privada del holder ([ADR-0005](../decisions/0005-digital-vote-signing-strategy.md)).
- **Track físico**: Votación presencial verificada con VC de identidad.

Ver spec detallada: [voting-module-spec.md](voting-module-spec.md)

## Autenticación

Según [ADR-0001](../decisions/0001-aws-cognito-authentication.md):
- **AWS Cognito User Pools** para autenticación de holders.
- Tokens JWT para llamadas a API de backend.
- Refresh automático de tokens via `cognito.js`.

## Estándares soportados

Según [ADR-0002](../decisions/0002-w3c-veia-dual-standards.md):
- **W3C Verifiable Credentials** (formato principal).
- **Protocolo VEIA** (estándar español de credenciales verificables).

## Dependencias externas

- **AWS Cognito**: Autenticación del holder.
- **BusinessLogic API**: Credenciales, presentaciones, contactos, actividades.
- **Catalog API**: Catálogo de tipos de credenciales.
- **svault**: Firma digital de documentos y votos.

## Documentación relacionada

- [ADRs (5)](../decisions/)
- [Voting Module Spec](voting-module-spec.md)
- [Auth Implementation](../development/auth-implementation.md)
- [Security](../development/security.md)
