# svault — Secure Vault Service Architecture

## Propósito

Lambda con despliegue Docker que provee operaciones criptográficas mediante **AWS KMS**. Actúa como vault seguro para firma, cifrado y descifrado de datos sensibles (claves privadas, hashes de credenciales, etc.) para los tenants de la plataforma.

## Componentes

```
svault/
├── src/
│   ├── index.js        ← Lambda handler principal
│   ├── modules/        ← Módulos KMS: sign, encrypt, decrypt, verify
│   └── utils/          ← Helpers y logging
├── Dockerfile          ← Imagen Docker para deploy Lambda
├── docker-compose.yml  ← Entorno local
├── test-local.sh       ← Script de test local
└── examples.json       ← Ejemplos de payloads
```

## Operaciones soportadas

- **Sign**: Firma de datos usando clave KMS del tenant.
- **Verify**: Verificación de firmas.
- **Encrypt**: Cifrado simétrico con KMS.
- **Decrypt**: Descifrado de datos.

## Contextos de ejecución

El servicio soporta dos contextos:
1. **AWS Lambda + KMS real** (producción/staging).
2. **Local con mocks KMS** (desarrollo, via Docker Compose).

## Flujo

```
Llamada desde servicio cliente
              ↓
    Lambda Handler (svault)
              ↓
    Módulo KMS (sign / encrypt / decrypt)
              ↓
    AWS KMS (clave del tenant)
              ↓
    Respuesta firmada / cifrada
```

## Aislamiento de tenants

Cada tenant tiene su propia CMK (Customer Managed Key) en KMS. El servicio resuelve la clave correcta a partir del claim del token Cognito.

## Dependencias externas

- **AWS KMS**: Operaciones criptográficas.
- **AWS Cognito**: Identificación del tenant para selección de clave.

## Documentación relacionada

- [README del servicio](../README.md)
- [ADRs](../decisions/)
