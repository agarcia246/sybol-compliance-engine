# signEth Lambda — Architecture

## Propósito

Lambda para **firma de transacciones Ethereum usando AWS KMS** y verificación de firmas con `ethers.js` (`ecrecover`). Permite firmar transacciones sin exponer claves privadas fuera de KMS.

## Componentes

```
signEth/
├── index.mjs              ← Lambda handler principal (firma con KMS)
├── verifySignature.mjs    ← Verificación de firmas (personal message + tx)
└── kmsEthereumUtils.mjs   ← Utilidades KMS-Ethereum (encoding, hashing)
```

## Flujo de firma

```
Request (txData + tenantId)
        ↓
  index.mjs
        ↓
  kmsEthereumUtils: encode tx → hash
        ↓
  AWS KMS: sign hash (ECDSA secp256k1)
        ↓
  Firma Ethereum lista para broadcast
```

## Flujo de verificación

```
Request (mensaje + firma)
        ↓
  verifySignature.mjs
        ↓
  ethers.utils.recoverAddress (ecrecover)
        ↓
  Dirección recuperada ↔ dirección esperada
```

## Permisología IAM

- `kms:Sign`
- `kms:GetPublicKey`

## Documentación relacionada

- [README](../README.md)
- [svault service](../../services/svault/) (servicio complementario para KMS)
- [ADR-0003 bm — Transaction Signing](../../services/bm/decisions/0003-transaction-signing-key-management.md)
