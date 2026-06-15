# ADR-002: RPC / Node Provider Strategy

**Date:** 2026-03-16  
**Status:** Accepted  
**Authors:** IGM  
**Deciders:** IGM

---

## Context and Problem Statement

The bm service communicates with EVM blockchains exclusively through JSON-RPC endpoints. The reliability, latency, cost, and data-sovereignty characteristics of the service depend directly on how these RPC connections are sourced.

Options range from fully managed third-party providers (Infura, Alchemy, QuickNode) to self-operated nodes, with hybrid multi-provider strategies in between.

This decision must account for:

- **Uptime requirements**: a single RPC provider becoming unavailable would make transaction submission impossible.
- **Multi-chain support**: each chain (Ethereum, Polygon, Base, etc.) may require a separate RPC node or provider plan.
- **Data sovereignty and privacy**: sending transaction data to a third-party provider means exposing wallet addresses, smart contract calls, and tenant activity.
- **Cost model**: managed providers charge per request; self-hosted nodes require infrastructure investment.
- **Lambda networking**: RPC calls are outbound HTTPS/WSS from Lambda; latency and connection pooling limits apply.

---

## Decision Drivers

- High availability and failover capability
- Latency (especially for synchronous transaction submission paths)
- Data privacy / confidentiality of on-chain activity
- Operational overhead (self-hosted vs managed)
- Cost at expected transaction throughput
- Multi-chain support scope
- Consistency of archive data access (getLogs across historical blocks)

---

## Considered Options

### Option A — Single managed third-party provider (e.g. Infura or Alchemy)

One managed provider account with endpoints per chain. No infrastructure to operate.

- Low operational overhead
- Single point of failure (provider outage → service unavailable)
- Third party sees all transaction data (addresses, calldata, timing)
- Simple configuration: one RPC URL per chain
- Subject to provider rate limits and pricing tiers

### Option B — Multi-provider with automatic fallback

Two or more managed providers per chain (e.g. primary Alchemy + fallback Infura). Automatic failover on error or timeout.

- Eliminates single-provider outage risk
- Doubles or triples RPC cost
- Minor implementation complexity for fallback routing
- Data is shared across multiple third-party providers

### Option C — Self-hosted nodes (AWS EC2 / ECS)

Run full nodes (or archive nodes) per chain on AWS infrastructure within the same VPC as Lambda.

- Complete data sovereignty; no third-party exposure
- Very low latency (same VPC)
- High operational complexity: node sync, disk, upgrades, monitoring
- Infrastructure cost scales per chain (node per chain)
- Archive node storage requirement for historical getLogs

### Option D — Hybrid: self-hosted for critical chains + managed fallback

Operate self-hosted nodes for the main chains used in production; use managed providers as fallback and for less-critical chains.

- Balances sovereignty and operational cost
- Greater complexity in routing and configuration
- Requires a clear policy for which chains are "critical"

### Option E — RPC aggregator service (e.g. Llamanodes, Chainlist public RPCs)

Use free/public aggregated RPC endpoints.

- Zero cost
- Typically rate-limited, unreliable, and unsuitable for production transaction submission
- No SLA guarantees

---

## Decision

Adopt **Option D — Hybrid: self-hosted nodes for critical chains + managed provider fallback**.

For chains designated as critical (those carrying production tenant transactions), operate self-hosted full/archive nodes within the AWS VPC. Managed third-party providers (e.g. Alchemy or Infura) are configured as automatic fallback per chain and serve as the primary source for non-critical or testnet chains. The RPCClient layer in bm handles routing and failover transparently, with chain criticality defined in the chain registry (ADR-004).

---

## Decision Outcome

Option D is selected as the best balance across the key drivers:

- **Option A** was rejected due to the single point of failure risk — a provider outage would make transaction submission entirely unavailable.
- **Option B** improves availability but still exposes all transaction data to third parties and provides no latency advantage over a co-located node.
- **Option C** provides full sovereignty and lowest latency but the operational cost (node sync, storage, upgrades) is prohibitive across all supported chains at this stage.
- **Option E** was rejected outright as unsuitable for production workloads (no SLA, rate limits).

Option D gives data sovereignty and predictable low latency for the chains that matter most (critical production chains), while keeping operational complexity bounded by delegating less-critical and testnet chains to managed providers. Fallback to managed providers for critical chains ensures availability if a self-hosted node falls behind or becomes unavailable.

---

## Consequences

### Positive

- Transaction data for critical chains never leaves the AWS VPC under normal operation — strongest data privacy posture.
- Lower and more predictable RPC latency for critical chains (same-VPC vs external HTTPS).
- Automatic fallback to managed providers maintains availability during node downtime or sync lag.
- Cost predictable for high-throughput chains (no per-request pricing on self-hosted node).
- Non-critical and testnet chains onboarded cheaply via managed providers without infrastructure investment.

### Negative

- Self-hosted node operation adds infrastructure responsibility: disk provisioning, sync monitoring, client upgrades, and on-call for node issues.
- Archive node storage (for deep historical `getLogs`) is significant — must be sized and monitored per chain.
- Routing policy (critical vs non-critical chain designation) must be kept in sync with the chain registry (ADR-004) and reviewed as chain usage evolves.
- Fallback to managed provider means third-party exposure occurs on node failure — this must be accepted and communicated to stakeholders.

---

## Implementation Notes

- **Node client**: use an EVM-compatible client (e.g. Geth or Nethermind) on AWS EC2 with dedicated EBS volumes for chain data. Define storage sizing per chain based on archived block history requirements.
- **Chain registry integration**: each chain entry in the registry (ADR-004) carries a `rpcPrimary` (self-hosted, internal URL) and optional `rpcFallback` (managed provider URL from Secrets Manager). The `critical` flag controls whether a self-hosted primary exists.
- **Fallback logic**: the RPCClient wraps each outbound call with a try/catch; on timeout or connection error it retries once on the fallback provider and emits a `bm.rpc.fallback` CloudWatch metric.
- **RPC API keys**: managed provider API keys stored in AWS Secrets Manager, never in environment variables. Loaded at Lambda cold start and cached in-memory.
- **Self-hosted node health check**: a Lambda-scheduled EventBridge rule pings the self-hosted node's `eth_blockNumber` every 60 seconds and publishes a `bm.node.blockLag` metric; alerting fires if lag exceeds a configurable threshold, triggering automatic traffic shift to the fallback.

---

## References

- [Alchemy documentation](https://docs.alchemy.com/)
- [Infura documentation](https://docs.infura.io/)
- [QuickNode documentation](https://www.quicknode.com/docs)
- Service Spec §5.2 (Reliability — NFR-10, NFR-11, NFR-12), §11 (Configuration)
