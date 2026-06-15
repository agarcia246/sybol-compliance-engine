# ADR-005: On-Chain Event Handling Strategy

**Date:** 2026-03-16  
**Status:** Accepted  
**Authors:** IGM  
**Deciders:** IGM

---

## Context and Problem Statement

Smart contracts emit events (EVM logs) that business logic services need to react to — for example, detecting when a credential hash has been anchored on-chain, or when a token transfer has been confirmed.

There are two distinct event use cases:

1. **Historical queries**: "Give me all events emitted by contract X between block A and block B."  
2. **Real-time notification**: "Notify me when contract X emits event Y."

Historical queries are straightforward (FR-40). The design challenge is **real-time event handling** (FR-41), which is complicated by the Lambda execution model (no persistent process, no long-running WebSocket connections).

This decision determines how the bm service — or a component alongside it — handles real-time event detection and notification.

---

## Decision Drivers

- Lambda execution model (no persistent process between invocations)
- Reliability: events must not be missed, including during service downtime
- Latency: time from event emission to notification delivery
- Operational complexity
- Cost (polling frequency, indexer infrastructure)
- Decoupling: callers should not be blocked waiting for events

---

## Considered Options

### Option A — Caller-driven polling (no server-side subscription)

The bm service only exposes the historical getLogs endpoint. Callers are responsible for polling at their own interval.

- Simplest implementation for bm
- Polling logic duplicated in each caller service
- Callers must manage their own last-seen block cursor
- Suitable if event latency requirements are relaxed (seconds to minutes)
- Risk of missed events if a caller's polling fails

### Option B — Server-side polling loop (Lambda scheduled EventBridge)

A periodic Lambda (triggered by EventBridge Scheduler) polls eth_getLogs for registered subscriptions and publishes events to an internal queue (SQS/SNS/EventBridge).

- No persistent process required (fits Lambda model)
- Polling interval = minimum event latency (minimum ~1 minute with EventBridge, sub-minute with SQS delay)
- Risk of duplicate event delivery (at-least-once semantics)
- Requires a subscription registry (what to watch, from which block)
- Misses events only if polling lapses over the block window (recoverable)

### Option C — WebSocket subscription with long-running compute (ECS/Fargate)

A persistent process (ECS Fargate task) maintains a WebSocket connection to the RPC provider and subscribes to `eth_subscribe`. Events are forwarded to internal queues.

- Near-real-time event delivery (< 1 block latency)
- Requires a separate ECS service to operate alongside Lambda
- WebSocket subscriptions are provider-dependent (not all providers support `eth_subscribe` reliably)
- Higher operational complexity; persistent process to monitor

### Option D — External blockchain indexer (The Graph, Subsquid, Goldsky)

Delegate event indexing to a dedicated indexer that monitors contracts and exposes a GraphQL or webhook API.

- Robust, battle-tested indexing with query capabilities
- No polling or subscription logic in bm
- Additional external service dependency and potential vendor lock-in
- Self-hosted indexer (Graph Node) requires significant infrastructure
- Managed indexer services (Goldsky, Subsquid Cloud) have cost and data-sharing implications

### Option E — Hybrid: polling for reliability + WebSocket for latency

Maintain a WebSocket subscription for low-latency events with EventBridge polling as a fallback/reconciliation mechanism. Events are deduplicated by log index + txHash.

- Best of both: low latency + resilience to WebSocket disconnections
- Most complex implementation
- Requires deduplication logic

---

## Decision

Adopt **Option B — Server-side polling loop via EventBridge Scheduler + Lambda**.

A dedicated `bm-event-poller` Lambda is invoked on a fixed schedule (EventBridge Scheduler, `rate(1 minute)`). On each invocation it reads all active subscriptions from a `bm_event_subscriptions` registry, calls `eth_getLogs` per subscription, publishes discovered events to a shared EventBridge custom bus, and advances the per-subscription block cursor.

This fits the existing Lambda-only deployment model (no ECS required), keeps all event state in the tenant's RDS PostgreSQL database (consistent with ADR-004), and guarantees no event is permanently missed because the block cursor is only advanced after successful publication.

---

## Decision Outcome

**Option B chosen** over the alternatives for the following reasons:

- **Option A rejected**: duplicates cursor management and polling logic in every caller service; no centralised visibility into which contracts are being watched.
- **Option C rejected**: ECS Fargate adds a persistent-compute tier that conflicts with the serverless-first architecture. WebSocket reliability across managed providers (Alchemy, Infura) is inconsistent, especially for private/self-hosted RPCs. The operational burden does not justify the latency improvement (1 block ≈ 2–15 s, already within acceptable SLAs).
- **Option D rejected**: managed indexers (Goldsky, Subsquid Cloud) introduce data-sharing concerns incompatible with Sybol's confidentiality model; self-hosted Graph Node requires significant infrastructure. Vendor lock-in risk is high.
- **Option E rejected**: hybrid architecture delivers marginal latency benefit over Option B given block times of 2–12 s, while doubling implementation and operational complexity.

Option B provides sufficient latency (~60 s worst case), guaranteed durability (cursor-based recovery), fits the Lambda model, and keeps the entire stack within AWS.

---

## Consequences

### Positive

- No persistent compute — `bm` remains Lambda-only; consistent with ADR-002 and ADR-004 deployment model.
- Guaranteed event delivery: cursor only advances after successful EventBridge `PutEvents`; a failed invocation re-processes the same block range on the next schedule.
- Centralised subscription registry enables observability (auditable list of watched contracts per tenant).
- Block reorg resilience: cursor is set to `latest_confirmed_block - confirmation_blocks` (reuses ADR-004's `confirmation_blocks` value), so logs from reorged blocks are not emitted permanently.
- Easy to add new subscriptions at runtime (SQL `INSERT`) without Lambda redeployment.

### Negative

- Minimum event latency ≈ polling interval (1 minute). Not suitable for sub-second use cases.
- `eth_getLogs` range queries can be expensive for high-traffic contracts; block windows must be bounded.
- At-least-once delivery: a crash between publication and cursor update can reprocess the same block. Consumers must be idempotent (deduplicate on `txHash + logIndex`).
- EventBridge Scheduler adds a small additional cost per invocation per tenant.

---

## Implementation Notes

### Subscription Registry Schema (PostgreSQL — tenant DB)

```sql
-- Registered event subscriptions for this tenant.
CREATE TABLE bm_event_subscriptions (
  subscription_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chain_id            INTEGER NOT NULL REFERENCES bm_chains(chain_id),
  contract_address    TEXT NOT NULL,              -- checksummed EVM address
  topic0              TEXT NOT NULL,              -- keccak256 of event signature, e.g. Transfer(address,address,uint256)
  from_block          BIGINT NOT NULL,            -- block at which monitoring started
  last_processed_block BIGINT NOT NULL,           -- cursor; updated after each successful poll
  target_bus          TEXT NOT NULL DEFAULT 'bm-events', -- EventBridge bus name
  detail_type         TEXT NOT NULL,              -- EventBridge detail-type for routing
  enabled             BOOLEAN NOT NULL DEFAULT TRUE,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_bm_event_subs_chain_enabled
  ON bm_event_subscriptions(chain_id, enabled);
```

### Poller Lambda (`bm-event-poller`)

```
bm-event-poller (separate Lambda, same ECR image, different handler entrypoint)
  Trigger: EventBridge Scheduler — rate(1 minute)
  Timeout: 5 minutes
  Concurrency: 1 (prevent overlapping invocations)
```

**Execution loop per invocation:**

1. Query all `bm_event_subscriptions WHERE enabled = TRUE`.
2. For each subscription:
   a. Resolve `JsonRpcProvider` for `chain_id` (reuse ADR-004 chain cache).
   b. Fetch `latestBlock`; set `toBlock = latestBlock - confirmation_blocks` (prevents reorg exposure).
   c. If `toBlock <= last_processed_block` — skip (no new confirmed blocks).
   d. Bound the window: `toBlock = MIN(toBlock, last_processed_block + MAX_BLOCK_WINDOW)` (default `MAX_BLOCK_WINDOW = 2000`).
   e. Call `provider.getLogs({ address, topics: [topic0], fromBlock: last_processed_block + 1, toBlock })`.
   f. For each log, call `EventBridge.putEvents` with `detail-type = subscription.detail_type`, `detail = { log, deduplicationId: txHash-logIndex }`.
   g. Update `last_processed_block = toBlock` in DB.
3. Emit CloudWatch metric `bm.poller.lag_blocks` per subscription (for alerting).

### Event Deduplication

- **Publisher-side**: EventBridge event entries include a stable `deduplicationId` (`${txHash}-${logIndex}`) in the `detail` payload.
- **Consumer-side**: downstream services (e.g., `businessLogic`) must treat event processing as idempotent using the `deduplicationId` as an idempotency key.
- No SQS FIFO required at the bm layer; deduplication is the consumer's responsibility.

### EventBridge Event Envelope

```json
{
  "source": "bm.poller",
  "detail-type": "<subscription.detail_type>",
  "detail": {
    "subscriptionId": "<uuid>",
    "chainId": 137,
    "contractAddress": "0x...",
    "topic0": "0x...",
    "deduplicationId": "<txHash>-<logIndex>",
    "blockNumber": 12345678,
    "txHash": "0x...",
    "logIndex": 3,
    "data": "0x...",
    "topics": ["0x...", "0x..."]
  }
}
```

### Operational Notes

- Set Lambda reserved concurrency = 1 on `bm-event-poller` to prevent parallel invocations racing on the same cursors.
- Alert on `bm.poller.lag_blocks > 100` (CloudWatch alarm) to detect stalled polling.
- `MAX_BLOCK_WINDOW` prevents `eth_getLogs` timeouts after a poller outage; on recovery, the poller self-heals across multiple invocations.
- Adding a new subscription to a running tenant requires only a SQL `INSERT`; it will be picked up on the next scheduled invocation.

---

## References

- [Ethereum JSON-RPC eth_getLogs](https://ethereum.org/en/developers/docs/apis/json-rpc/#eth_getlogs)
- [Ethereum eth_subscribe (WebSocket)](https://geth.ethereum.org/docs/interacting-with-geth/rpc/pubsub)
- [The Graph Protocol](https://thegraph.com/docs/)
- [Goldsky](https://docs.goldsky.com/)
- [AWS EventBridge Scheduler](https://docs.aws.amazon.com/scheduler/latest/UserGuide/what-is-scheduler.html)
- Service Spec §4.5 (Event Log Querying — FR-40, FR-41, FR-42)
