# Lambdas

Documentación de todas las funciones Lambda del proyecto Sybol.

## Catálogo

| Lambda | Descripción | ADRs |
|---|---|---|
| [PAdES](PAdES/) | Procesamiento y firma de PDFs (PAdES) | [ADRs](PAdES/decisions/) |
| [PAdES_2](PAdES_2/) | Variante extendida de PAdES | [ADRs](PAdES_2/decisions/) |
| [setupAlastriaIdentity](setupAlastriaIdentity/) | Registro de identidad on-chain Alastria (bootstrap único) | [ADRs](setupAlastriaIdentity/decisions/) |
| [signEth](signEth/) | Firma de transacciones Ethereum vía AWS KMS | [ADRs](signEth/decisions/) |

## ADRs globales relacionados

- [0002 — Serverless Architecture](../global/decisions/0002-serverless-architecture.md)
- [0005 — Lambda VPC Blockchain Connectivity](../global/decisions/0005-lambda-vpc-blockchain-connectivity.md)
