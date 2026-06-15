# ADR-001: EVM Client Library

**Date:** 2026-03-16  
**Status:** Accepted  
**Authors:** IGM  
**Deciders:** IGM

---

## Context and Problem Statement

The bm service must interact with EVM-compatible blockchains: encoding/decoding ABI-typed data, constructing and signing transactions, querying state via `eth_call`, and subscribing to or querying event logs.

The JavaScript/TypeScript ecosystem offers several mature libraries that abstract the JSON-RPC layer. The choice affects:

- **Bundle size and cold-start latency** (Lambda cold start is sensitive to dependency weight)
- **Type safety** — important for correctness when handling addresses, BigInt values, and ABI types
- **API ergonomics** — how transactions, providers, and signers are modelled
- **Maintenance and community** — long-term support and security patch cadence
- **Tree-shaking / modular imports** — a library that is modular reduces Lambda package size

This is a foundational choice: all internal modules (TransactionService, ContractService, EventService, SignerBackend) will depend on it.

---

## Decision Drivers

- Lambda cold start performance (smaller is better)
- TypeScript-first development experience
- ABI encoding/decoding correctness and type safety
- Active maintenance and security patch cadence
- Compatibility with AWS KMS signing (custom signer interface)
- Support for EIP-1559 fee model
- Support for both HTTP and WebSocket providers
- Ease of testing (mockability of provider layer)

---

## Considered Options

### Option A — ethers.js v6

A widely-adopted, full-featured Ethereum library. v6 is a TypeScript rewrite with modular packages (`@ethersproject/*`), a first-class `Signer` abstraction suitable for custom KMS backends, and native BigInt support.

- High community adoption; extensive documentation
- `AbstractSigner` pattern makes KMS integration straightforward
- Modular: only required packages need to be bundled
- v5 → v6 migration is a breaking change; most community examples target v5

### Option B — web3.js v4

The original Ethereum JavaScript library, now at v4 with TypeScript support and plugin architecture. Maintained by the ChainSafe team.

- Long history; large ecosystem
- v4 adds TypeScript and plugin system
- Generally heavier bundle than ethers.js v6 or viem
- Smaller usage share than ethers.js in recent projects

### Option C — viem

A modern TypeScript-first library built around tree-shakeable modules, immutable data structures, and full type inference from ABI definitions. Designed with bundle size and type safety as first-class concerns.

- Smallest bundle size of the three options
- Strictest type inference (ABI → TypeScript types at compile time)
- Immutable, functional API (no class instantiation)
- Youngest library; smaller ecosystem than ethers.js
- Custom signer integration uses a `LocalAccount` / custom `Account` pattern (different mental model from ethers `Signer`)

### Option D — Minimal custom JSON-RPC client (no library)

Build only the JSON-RPC calls needed (eth_call, eth_sendRawTransaction, eth_getLogs) using a lightweight HTTP client. ABI encoding delegated to a standalone library (e.g. `abitype`, `@ethersproject/abi`).

- Maximum control and minimal footprint
- Significant implementation effort for ABI codec, transaction serialization (RLP), EIP-1559/EIP-155 signing
- Maintenance burden for low-level encoding edge cases

---

## Decision

Adopt **ethers.js v6** (Option A) as the EVM client library for the bm service.

All internal modules — TransactionService, ContractService, EventService, and SignerBackend — will use ethers.js v6 APIs. The `AbstractSigner` class will be extended to implement the AWS KMS signing backend.

---

## Decision Outcome

ethers.js v6 is selected for the following reasons:

- Its `AbstractSigner` pattern provides a clean, well-documented extension point for integrating a custom AWS KMS signer without patching internals.
- The v6 TypeScript rewrite offers strong type safety for addresses, BigInt amounts, and ABI-typed values, reducing encoding bugs.
- It is the most widely adopted library in the ecosystem, ensuring a large body of community examples, security disclosures, and long-term maintenance.
- The modular package structure (`ethers/providers`, `ethers/contract`, etc.) allows bundling only the required sub-packages, keeping Lambda package size manageable.
- viem (Option C) was considered seriously for its bundle size advantage, but its functional/immutable `Account` model requires more adapter code to integrate with a KMS backend and its ecosystem maturity is lower at this time.

---

## Consequences

### Positive

- First-class `AbstractSigner` extension point simplifies KMS signer integration.
- Strong TypeScript types reduce ABI encoding mistakes.
- Broad community adoption means abundant documentation and fast security patch response.
- Native EIP-1559 and EIP-155 support out of the box.
- Supports both `JsonRpcProvider` (HTTP) and `WebSocketProvider` without additional libraries.

### Negative

- Slightly larger bundle than viem; cold-start impact must be measured and mitigated via selective imports.
- Most publicly available code examples still target v5; v6 API differences require developer awareness.
- Library lock-in: switching to viem in the future would require reworking all provider, signer, and contract interfaces.

---

## Implementation Notes

- Import selectively from `ethers` sub-paths (e.g. `import { Contract } from 'ethers'`) and enable tree-shaking in the Lambda build pipeline to minimise bundle size.
- Implement `KmsSigner extends AbstractSigner` adapting the AWS KMS `Sign` API response (DER-encoded secp256k1 signature) to the compact 65-byte Ethereum format (`r || s || v`).
- Use `JsonRpcProvider` for HTTP connections (standard operations) and `WebSocketProvider` only where real-time subscriptions are required (see ADR-005).
- Pin the ethers.js version in `package.json` (`"ethers": "^6.x.x"`) and add it to the renovate/dependabot config for automated patch updates.
- Unit-test the `KmsSigner` adapter with a mocked KMS client to avoid coupling tests to AWS infrastructure.

---

## References

- [ethers.js v6 documentation](https://docs.ethers.org/v6/)
- [web3.js v4 documentation](https://docs.web3js.org/)
- [viem documentation](https://viem.sh/)
- [abitype](https://abitype.dev/)
- Service Spec §6 (Architecture Overview), §4.4 (Smart Contract Interaction)
