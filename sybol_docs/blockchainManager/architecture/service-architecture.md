# blockchainManager — Architecture

## Propósito

Servicio HTTP (Express) y Lambda que actúa como la capa de abstracción blockchain de la plataforma Sybol. Permite a todos los servicios del backend interactuar con redes EVM (Alastria RedT, RedB, Ethereum) sin conocer los detalles de los providers, la firma o el registro de contratos.

## Estructura

```
blockchainManager/
├── main.js               ← Entry point (Express + Lambda adapter)
└── src/
    ├── bootstrap/        ← Inicio de conexiones RPC y cache de contratos
    ├── config/           ← Configuración por chainId y entorno
    ├── exposition/       ← Rutas Express y controladores HTTP
    ├── helpers/          ← ABI encoding, gas estimation, utilidades RPC
    ├── persistence/      ← Cache en memoria de contratos y estado de cadena
    ├── repositories/     ← Consulta al registro de contratos (PostgreSQL)
    ├── services/         ← Lógica de negocio: sign, send, call, listen
    ├── standard/         ← Implementaciones W3C VC y Alastria Identity
    └── utils/            ← Logging, formateo, tracing
```

## API

Documentada en el fichero Swagger:
→ [api/swagger.yaml](../api/swagger.yaml)

## Patrones de código

El servicio sigue el **Developer Style DNA** definido en:
→ [development/developer-style-dna.md](../development/developer-style-dna.md)

Principios clave:
- Tracing por request con `traceId`.
- Todos los errores tienen el shape estándar `{ error, message, traceId }`.
- Separación estricta entre exposition, services y repositories.

## Dependencias externas

- **AWS Secrets Manager**: Claves privadas de firma (producción).
- **Nodos RPC**: Alastria RedT, Alastria RedB, Ethereum.
- **PostgreSQL**: Registro de smart contracts por tenant y chainId.
- **signEth Lambda**: (alternativa para firma vía KMS cuando se usa off-chain).

## Documentación relacionada

- [README](../README.md)
- [OpenAPI / Swagger](../api/swagger.yaml)
- [Developer Style DNA](../development/developer-style-dna.md)
- [ADRs del servicio bm](../../services/bm/decisions/)
