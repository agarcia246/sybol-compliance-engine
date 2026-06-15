# OnBoardingWeb — Architecture

## Propósito

Aplicación React que guía a nuevas organizaciones (tenants) a través del proceso de **onboarding** en la plataforma Sybol. Incluye registro, KYB (Know Your Business), verificación de identidad con Sumsub, MFA y aceptación de términos legales.

## Estructura

```
OnBoardingWeb/src/
├── app/                ← Routing y app shell
├── pages/
│   ├── Login/          ← Autenticación
│   ├── Register/       ← Registro de nuevo tenant
│   ├── Kyb/            ← KYB — documentación corporativa
│   ├── Mfa/            ← Configuración MFA
│   ├── Review/         ← Revisión de solicitud y estado
│   ├── CookiesPolicy/
│   ├── LegalNotification/
│   ├── PrivacyPolicy/
│   └── TermsOfService/
├── services/
│   ├── Sybol.js        ← API calls a Backoffice / BusinessLogic
│   ├── cognito.js      ← Autenticación AWS Cognito
│   ├── email.js        ← Notificaciones email
│   ├── Sumsub.js       ← Integración SDK Sumsub (KYC/KYB)
│   └── ProcessStatusRepository.js ← Estado del proceso de onboarding
├── components/         ← Componentes UI reutilizables
├── context/            ← Estado global (Context API)
├── hooks/              ← Custom React hooks
├── layouts/            ← Layouts de página
├── templates/          ← Templates de email / documentos
├── helpers/            ← Formatadores y utilidades
├── config/             ← Variables de entorno
└── examples/           ← Datos de ejemplo
```

## Flujo de onboarding

```
Registro → Login Cognito
               ↓
          KYB Form (documentación corporativa)
               ↓
          Sumsub Widget (verificación de identidad)
               ↓
          MFA Setup (Cognito MFA)
               ↓
          Review (estado de la solicitud)
               ↓
          Aprobado → acceso a la plataforma
```

## Integración Sumsub

Sumsub gestiona la verificación KYC/KYB del tenant. Ver documentación:
- [Sumsub Status Check](../specs/sumsub-status-check.md)
- [Sumsub Webhooks](../specs/sumsub-webhooks.md)

## Dependencias externas

- **AWS Cognito**: Autenticación y gestión de usuarios.
- **Sumsub SDK**: Verificación de identidad corporativa (KYB).
- **Backoffice API**: Registro y gestión de tenants.
- **BusinessLogic API**: Creación de credenciales iniciales del tenant.

## Documentación relacionada

- [ADRs](../decisions/)
- [Sumsub Status Check](../specs/sumsub-status-check.md)
- [Sumsub Webhooks](../specs/sumsub-webhooks.md)
