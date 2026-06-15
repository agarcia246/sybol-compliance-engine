# ADR-HED-004: Multi-Method DID Dispatch via Universal Resolver
**Status:** Accepted (implemented in POC; refactoring only — no re-decision needed)
**Date:** 2026-04-15 (accepted 2026-04-16)
**Issue:** #199
**Deciders:** Engineering team

## Context
The platform currently resolves DIDs exclusively through `didWebResolver`, which handles `did:web` identifiers. With the introduction of `did:hedera` support, multiple resolution paths must coexist. Every call site that currently invokes `didWebResolver` directly would need method-aware branching, creating duplication and making future method additions expensive.

A single entry point is needed so that callers remain agnostic to the underlying DID method and new methods can be added without touching consuming code.

## Decision
Create a universal DID resolver dispatcher (`didResolver.js`) that inspects the DID method prefix (`did:web:`, `did:hedera:`) and routes resolution to the appropriate handler (`didWebResolver` or `hederaDid.service`). All existing code that calls `didWebResolver` directly will be migrated to use the dispatcher.

The dispatcher exposes the same interface as the current resolver (`resolve(did) -> DID Document`) so the migration is transparent to callers.

## Options Evaluated

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A) Dispatcher pattern (selected)** | Central `didResolver.js` routes by method prefix | Single point of change; clean separation of concerns; trivial to add new methods | One additional layer of indirection |
| B) If/else in each calling site | Each consumer checks the DID method and calls the right resolver | No new abstraction | Duplicated logic across call sites; every new method requires N changes; error-prone |
| C) Plugin registry pattern | Dynamic registration of resolvers at startup via a registry map | Maximum extensibility | Over-engineered for two methods; adds startup complexity and debugging difficulty |

## Consequences
- All DID resolution goes through a single module, simplifying testing and logging.
- Adding a third DID method (e.g., `did:key`) requires only registering a new handler in the dispatcher.
- Existing unit tests for `didWebResolver` remain valid; integration tests are updated to call through the dispatcher.
- A brief migration pass is needed to replace direct `didWebResolver` imports across the codebase.
