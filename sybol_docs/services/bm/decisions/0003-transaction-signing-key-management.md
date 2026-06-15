# ADR-003: Transaction Signing & Key Management

**Date:** 2026-03-16  
**Status:** Accepted  
**Authors:** IGM  
**Deciders:** IGM  
**Security Review Required:** Yes

---

## Context and Problem Statement

The bm service must sign EVM transactions on behalf of tenants before broadcasting them to the network. Transaction signing requires access to private key material corresponding to the signer's Ethereum address (EOA).

This is the **highest-security decision** in the bm service. Any compromise of signing keys would allow unauthorized transactions to be submitted on behalf of tenants, potentially resulting in asset loss or fraudulent on-chain actions.

Key constraints:

- The service runs as AWS Lambda (serverless, stateless, ephemeral runtime).
- Private key material MUST NOT be stored in plaintext in code, environment variables, or logs.
- The signing approach must be auditable (who signed what, when).
- Multiple tenants may require distinct signing identities (wallet addresses).
- The chosen approach must support the EVM signing spec (secp256k1 ECDSA, keccak256, EIP-155, EIP-1559).

The existing Sybol platform already uses AWS KMS for key management (`infraestructure/ClientInfra/KMS-MANAGEMENT.md`). This context should inform the decision.

---

## Decision Drivers

- Security: private key material must never be exposed or recoverable in plaintext
- Auditability: all signing operations must be logged and attributable
- Scalability: signing must work with concurrent Lambda invocations
- Operational simplicity: key lifecycle management (rotation, revocation) must be operationally sound
- Compliance: potential regulatory requirements (eIDAS 2.0, GDPR) on key custody
- Cost: HSM/KMS usage is per-request; high transaction volume increases cost
- Tenant isolation: each tenant's keys must be cryptographically isolated

---

## Considered Options

### Option A — AWS KMS (asymmetric key, ECC_SECG_P256K1)

AWS KMS natively supports `ECC_SECG_P256K1` keys (secp256k1), the curve used by Ethereum. Signing occurs inside KMS; the private key never leaves the HSM hardware boundary.

- Private key never accessible; HSM-backed by default
- Audit trail via AWS CloudTrail
- IAM policies for fine-grained access control
- Per-request cost (~$0.03–0.04 per signing operation)
- Requires deriving the Ethereum address from the public key (supported)
- KMS does not return the signature in Ethereum format natively — DER-to-compact conversion required
- Each tenant needs a separate KMS key (cost scales with tenant count)

### Option B — AWS Secrets Manager (encrypted raw private key)

Store raw private key material (hex) encrypted in AWS Secrets Manager. Lambda retrieves and loads the key into memory at runtime to sign locally.

- Simpler implementation (standard ethers.js / viem wallet pattern)
- Private key is decrypted into Lambda memory during invocation — higher risk surface than KMS
- Rotation requires updating the secret and syncing dependent records
- Secrets Manager has lower per-request cost than KMS signing
- Audit trail limited to secret retrieval (not per-signing-operation)

### Option C — AWS CloudHSM

Hardware Security Module service providing dedicated HSM hardware. Supports PKCS#11 and JCE APIs.

- Strongest isolation; dedicated hardware per customer
- Significant operational and cost overhead (dedicated cluster)
- No Lambda-native SDK; requires custom PKCS#11 bridge
- Suitable for very high compliance/regulatory environments

### Option D — External signing service (MPC / Fireblocks / Web3Auth)

Delegate signing to a specialized external service such as Fireblocks (MPC custody), Web3Auth, or a custom MPC implementation.

- Multi-party computation eliminates single-key compromise risk
- Institutional-grade key custody and policy engine
- High per-transaction or licensing cost
- Additional external service dependency and latency
- Complex integration; vendor lock-in risk

### Option E — Hierarchical Deterministic (HD) wallets from a master seed

Derive per-tenant signing keys from a BIP-32/BIP-44 HD wallet master seed. The master seed is stored encrypted (KMS or Secrets Manager). Tenant keys are derived in-memory at runtime.

- Single secret to manage (the master seed)
- Enables deterministic re-derivation of addresses
- Master seed compromise affects all tenants
- Not natively supported by standard KMS flows (requires in-Lambda derivation)
- Key rotation requires a new master seed and migration of all on-chain state

### Option F — HD Derivation for Provisioning + KMS for Runtime Signing (Hybrid A+E)

Combine the **deterministic address derivation** of HD wallets with the **HSM-backed signing security** of KMS. The key lifecycle is split into two distinct phases:

**Phase 1 — Provisioning (one-time, off-Lambda):**
1. A BIP-32/BIP-44 HD wallet master seed is used **offline** (in a dedicated, air-gapped or hardened provisioning tool) to derive a per-tenant private key at a deterministic path (e.g. `m/44'/60'/tenantIndex'/0/0`).
2. The derived private key is imported into AWS KMS as external key material (`KeySpec: ECC_SECG_P256K1`, `Origin: EXTERNAL`) using the [ImportKeyMaterial](https://docs.aws.amazon.com/kms/latest/APIReference/API_ImportKeyMaterial.html) API.
3. After successful import and verification (by calling `GetPublicKey` and confirming the Ethereum address), **the raw private key material is securely wiped** from the provisioning environment.
4. The master seed is stored separately with maximum security (e.g. hardware wallet, paper backup in a vault) and is only ever used for provisioning — never at runtime.

**Phase 2 — Runtime (Lambda, production):**
- All signing operations go through AWS KMS (identical to Option A).
- Private key material never enters Lambda memory.
- Full CloudTrail audit trail per signing operation.
- No master seed or derived key material anywhere in the runtime environment.

Key properties:
- Deterministic: tenant wallet addresses can be pre-computed before provisioning, enabling pre-registration of addresses in smart contracts.
- KMS-backed: post-provisioning, the security posture is identical to Option A.
- Master seed used only during provisioning, not at runtime — eliminates the runtime exposure risk of Option E.
- Requires a secure, auditable provisioning pipeline (not a Lambda concern).

Constraints and considerations:
- KMS `ImportKeyMaterial` for `ECC_SECG_P256K1` requires wrapping the raw private key with the KMS-provided RSA public key before importing.
- Master seed must be generated with a CSPRNG and stored with strict access controls (separate from the KMS keys it seeds).
- Master seed compromise would only allow derivation of new keys at new paths — existing imported KMS keys remain secure because the private key material was wiped post-import.
- Key rotation for a specific tenant requires: derive a new key at a different path, import to KMS as a new key, update the tenant's `signerRef` in the registry, retire the old KMS key.

**Extension — Native KMS keys (non-derived):**

Option F can coexist with keys generated natively inside KMS (`Origin: AWS_KMS`) for cases where address pre-determinism is not required and operational agility takes priority. These "agile" keys:

- Are created on demand via `CreateKey` (`KeySpec: ECC_SECG_P256K1`, `KeyUsage: SIGN_VERIFY`) without any provisioning pipeline.
- Have no derivation path — KMS generates the key material internally and it never leaves the HSM.
- Ethereum address is obtained post-creation by calling `GetPublicKey` and deriving the address from the uncompressed public key.
- Are ideal for: platform-managed operational wallets (e.g. gas relayers, service accounts), temporary or test tenant onboarding, scenarios where address pre-registration is not needed.

The two key origins are distinguished in the registry (ADR-004) by a `keyOrigin` field (`HD_IMPORTED` or `KMS_NATIVE`) on the signer record. Runtime signing is identical for both: all calls go through the KMS `Sign` API.

| Property | HD-derived + imported | KMS-native |
|---|---|---|
| Address determinism | ✅ Pre-computable from seed | ❌ Known only after creation |
| Pre-registration in contracts | ✅ Yes | ❌ Not without creating the key first |
| Private key ever outside HSM | ⚠️ During provisioning only (then wiped) | ❌ Never |
| Provisioning complexity | Medium (offline pipeline) | Low (API call) |
| Master seed dependency | Yes | No |
| Runtime signing flow | KMS Sign API | KMS Sign API |

---

## Decision

Adopt **Option F — HD Derivation for Provisioning + KMS for Runtime Signing**, extended to support both key origins (`HD_IMPORTED` and `KMS_NATIVE`) within the same runtime model.

All transaction signing at runtime goes through AWS KMS (`Sign` API, `ECC_SECG_P256K1`). Private key material never enters Lambda memory under any circumstances after provisioning.

Two key provisioning paths are supported, selected per use case at tenant onboarding time:

1. **`HD_IMPORTED`** — A BIP-32/BIP-44 master seed is used in an offline provisioning tool to derive a deterministic per-tenant key. The derived key is imported into KMS via `ImportKeyMaterial` and the raw material is wiped immediately after. Used when the Ethereum address must be known before key creation (e.g. pre-registration in smart contracts).

2. **`KMS_NATIVE`** — A key is created directly inside KMS (`CreateKey`, `Origin: AWS_KMS`). The address is derived post-creation from `GetPublicKey`. Used for operational wallets, gas relayers, and fast-onboarding scenarios where address pre-determinism is not required.

The `keyOrigin` field in the signer registry (ADR-004) records which path was used. The signing interface is identical for both.

---

## Decision Outcome

Option F is selected for the following reasons:

- **Options B and E** were rejected because both require the private key to exist in plaintext in a runtime environment (Lambda memory or Lambda-reachable secret store), which is an unacceptable risk surface for transaction signing keys.
- **Option C (CloudHSM)** provides stronger isolation than KMS but requires a dedicated cluster and has no Lambda-native SDK support, making operational cost disproportionate at this stage.
- **Option D (MPC/Fireblocks)** provides MPC key custody but introduces vendor lock-in, high per-transaction cost, and an additional external dependency on the critical signing path.
- **Option A (KMS-only)** is a subset of Option F. Option F adopts A's runtime posture entirely and adds deterministic provisioning via HD derivation as an opt-in path, without weakening any of A's security guarantees.
- The `KMS_NATIVE` extension ensures operational agility: new operational wallets can be provisioned in seconds via a single API call, without requiring the offline provisioning pipeline.
- The HD derivation path (`HD_IMPORTED`) preserves address pre-determinism, which is required when Ethereum addresses must be registered in smart contract state before the tenant is fully onboarded.
- Post-provisioning, both key origins are indistinguishable at runtime — the signing adapter calls `KMS Sign` in both cases, giving a uniform, auditable, HSM-backed signing path.

---

## Consequences

### Positive

- Private key material never present in Lambda memory or any runtime environment at any point after provisioning.
- Full CloudTrail audit trail per signing operation (attributable to tenant + signer reference).
- IAM policies provide fine-grained, per-key access control enforced at the AWS control plane.
- `HD_IMPORTED` path allows pre-computing tenant Ethereum addresses before onboarding, enabling address pre-registration in smart contract state.
- `KMS_NATIVE` path allows near-instant key provisioning without an offline pipeline — suitable for operational wallets and rapid onboarding.
- Uniform runtime signing interface: both key origins use the same `KMS Sign` call, keeping the service layer simple.
- Aligns with the existing KMS usage pattern in the Sybol platform (`infraestructure/ClientInfra/KMS-MANAGEMENT.md`).
- Each tenant has cryptographically isolated keys; no shared key material across tenants.

### Negative

- **`HD_IMPORTED` path**: requires a secure offline provisioning pipeline. The provisioning tool must handle raw private key material during the import window — this window must be minimised and audited.
- **`HD_IMPORTED` path**: the master seed is a high-value secret. Its compromise does not affect existing KMS keys (material was wiped post-import) but would allow derivation of new keys at unused paths — master seed custody requires strict controls.
- KMS `Sign` has a per-request cost (~$0.03–0.04). High transaction throughput will increase costs proportionally; must be accounted for in capacity planning.
- KMS signature output is DER-encoded ECDSA — requires a DER-to-compact conversion step (`r || s || v`) in the `KmsSigner` adapter before submitting EVM transactions (already noted in ADR-001).
- Importing external key material into KMS (`ImportKeyMaterial`) requires wrapping the private key with a KMS-provided RSA public key and managing the import token lifetime (valid for 24 hours).
- `KMS_NATIVE` keys cannot be exported or migrated — if the KMS key is accidentally deleted (without a pending deletion window), the Ethereum address is permanently lost. Deletion protection policies must be enforced.

---

## Implementation Notes

### Signer Adapter (runtime)
- Implement `KmsSigner extends AbstractSigner` (ethers.js v6 — see ADR-001) that calls `kms.sign({ KeyId, Message, SigningAlgorithm: 'ECDSA_SHA_256', MessageType: 'DIGEST' })`.
- Convert the DER-encoded response signature to Ethereum compact format (`r || s || v`) using the `secp256k1` library or equivalent. The recovery bit `v` must be determined by trying both candidates (0 and 1) against the expected address.
- The `KmsSigner` constructor receives a `keyId` (KMS Key ARN or alias); it never receives any key material.

### Signer Registry (ADR-004)
- Add a `signerRef` → `{ kmsKeyId, address, chainIds, keyOrigin, hdPath? }` record per tenant.
- `keyOrigin`: `HD_IMPORTED` | `KMS_NATIVE`.
- `hdPath`: present only for `HD_IMPORTED` keys — records the BIP-44 derivation path for auditability (e.g. `m/44'/60'/0'/0/0`).

### HD Provisioning Pipeline (offline tool, not part of Lambda)
- Implemented as a standalone CLI tool (not deployed as Lambda).
- Steps: generate/load master seed → derive private key at BIP-44 path → call `GetParametersForImport` (RSA wrapping key + import token) → wrap private key with RSA public key → call `ImportKeyMaterial` → verify address via `GetPublicKey` → write signer registry record → **securely zero private key buffer in memory** → exit.
- The CLI must run in a hardened, access-controlled environment. Key provisioning events must be logged to CloudTrail and a separate audit log.
- Master seed storage: hardware wallet or encrypted offline backup in a physically secured location, separate from AWS credentials.

### KMS_NATIVE Provisioning (operational)
- `CreateKey({ KeySpec: 'ECC_SECG_P256K1', KeyUsage: 'SIGN_VERIFY', Origin: 'AWS_KMS' })`
- Derive Ethereum address: `GetPublicKey` → parse DER X.509 SubjectPublicKeyInfo → extract 64-byte uncompressed public key → `keccak256(pubKey)[12:]` → checksum (EIP-55).
- Write signer registry record with `keyOrigin: KMS_NATIVE`.

### Key Deletion Protection
- All KMS keys used for signing MUST have a minimum pending deletion window of 30 days.
- IAM policies MUST deny `kms:ScheduleKeyDeletion` except for a dedicated key-lifecycle role requiring MFA.
- Automatic key deletion MUST be disabled (keys do not expire unless `ImportKeyMaterial` is called with `ExpirationModel: KEY_MATERIAL_EXPIRES`).

---

## References

- [AWS KMS ECC_SECG_P256K1 support](https://docs.aws.amazon.com/kms/latest/developerguide/asymmetric-key-specs.html)
- [Ethereum secp256k1 signing spec (Yellow Paper, Appendix F)](https://ethereum.github.io/yellowpaper/paper.pdf)
- [EIP-155: Simple Replay Attack Protection](https://eips.ethereum.org/EIPS/eip-155)
- `infraestructure/ClientInfra/KMS-MANAGEMENT.md`
- `docs/security/cryptography.md`
- Service Spec §4.6, §9.2, NFR-20 through NFR-23
