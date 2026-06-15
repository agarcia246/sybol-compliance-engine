# bm — Blockchain Manager Service Architecture

## Propósito

Capa de abstracción que desacopla a todos los demás servicios de la complejidad de interactuar directamente con redes blockchain EVM. Provee una API unificada para firma de transacciones, llamadas a contratos inteligentes y escucha de eventos on-chain.

## Componentes

```
blockchainManager/
├── main.js               ← Entry point HTTP + Lambda adapter
└── src/
    ├── bootstrap/        ← Inicialización de conexiones y providers
    ├── config/           ← Configuración de cadenas blockchain
    ├── exposition/       ← Rutas y controladores HTTP (Express)
    ├── helpers/          ← Utilidades blockchain (ABI encoder, gas, etc.)
    ├── persistence/      ← Cache de contratos y estado
    ├── repositories/     ← Acceso al registro de contratos
    ├── services/         ← Lógica de negocio: sign, send, call
    ├── standard/         ← Implementaciones estándar (W3C, Alastria)
    └── utils/            ← Parsing, formateo, logging
```

## Flujo de transacción

```
Servicio cliente → HTTP/Lambda → Exposition Layer
                                        ↓
                                   Service Layer
                                        ↓
                              ┌─────────────────┐
                              │   RPC Provider  │  (Infura / Alchemy / nodo propio)
                              │   con failover  │
                              └────────┬────────┘
                                       ↓
                                 EVM Blockchain
                              (Alastria RedT/RedB/Ethereum)
```

## Estrategia de firma

Según [ADR-0003](../decisions/0003-transaction-signing-key-management.md):
- Claves en **AWS Secrets Manager** (producción).
- Firma local en memoria para testing/staging.
- Sin claves en disco ni variables de entorno en producción.

## Estrategia multi-cadena

Según [ADR-0004](../decisions/0004-multi-chain-abstraction.md):
- Configuración por `chainId`.
- Un conjunto de providers por cadena.
- Abstracción de contrato por nombre lógico → dirección física.

## Dependencias externas

- **AWS Secrets Manager**: Almacenamiento seguro de claves privadas.
- **Nodos RPC**: Alastria RedT/RedB, o Ethereum mainnet/testnet.
- **PostgreSQL**: Registro permanente de contratos por tenant.

## Documentación relacionada

- [OpenAPI](../api/openapi.yaml)
- [SERVICE_SPEC](../specs/service-spec.md)
- [ADRs](../decisions/)
- [Developer Style DNA](../../../blockchainManager/development/developer-style-dna.md)
