# bm — Blockchain Manager Service

Servicio Node.js que abstrae la interacción con redes blockchain EVM (Alastria RedT, RedB, Ethereum). Gestiona transacciones, firma, registro de contratos inteligentes y eventos on-chain para todos los tenants de la plataforma.

## Responsabilidades

- Firma y envío de transacciones a la red blockchain.
- Gestión de estrategia de proveedor RPC (failover, round-robin).
- Registro y lookup de contratos inteligentes por tenant.
- Escucha y enrutado de eventos on-chain.
- Abstracción multi-cadena (misma API para diferentes redes EVM).

## API

→ [api/openapi.yaml](api/openapi.yaml)

## Especificaciones

→ [specs/service-spec.md](specs/service-spec.md)

## Decisiones arquitectónicas (6 ADRs)

→ [decisions/](decisions/)

| ADR | Título |
|---|---|
| [0001](decisions/0001-evm-client-library.md) | EVM Client Library |
| [0002](decisions/0002-rpc-provider-strategy.md) | RPC Provider Strategy |
| [0003](decisions/0003-transaction-signing-key-management.md) | Transaction Signing Key Management |
| [0004](decisions/0004-multi-chain-abstraction.md) | Multi-Chain Abstraction |
| [0005](decisions/0005-event-handling-strategy.md) | Event Handling Strategy |
| [0006](decisions/0006-smart-contract-registry.md) | Smart Contract Registry |

## Arquitectura

→ [architecture/service-architecture.md](architecture/service-architecture.md)
