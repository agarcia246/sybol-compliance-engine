# setupAlastriaIdentity Lambda — Architecture

## Propósito

Lambda autocontenida (Node 18, `eu-west-1`) que registra la identidad on-chain de Alastria para el servicio BlockchainManager. No tiene dependencias del monorepo — empaqueta toda la lógica internamente.

## Trigger

Manual o **EventBridge** (ejecución única por entorno al hacer bootstrap de un nuevo nodo).

## Flujo

```
Trigger (manual / EventBridge)
        ↓
1. Load / create wallets    ──► AWS Secrets Manager
2. Fetch signing keys       ──► AWS Secrets Manager
3. Extract public key       ──► openssl (bundled)
4. Register identity        ──► Ethereum / Alastria RPC
5. Store DID                ──► AWS Secrets Manager
```

## Permisología IAM requerida

- `secretsmanager:GetSecretValue`
- `secretsmanager:CreateSecret` / `PutSecretValue`
- Acceso de red al nodo RPC de Alastria (VPC o endpoint público)

Ver [ADR-0005 global — Lambda VPC Blockchain Connectivity](../../global/decisions/0005-lambda-vpc-blockchain-connectivity.md).

## Documentación relacionada

- [README](../README.md)
- [ADR-0005 — Lambda VPC Blockchain](../../global/decisions/0005-lambda-vpc-blockchain-connectivity.md)
