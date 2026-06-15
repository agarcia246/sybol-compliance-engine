# ADR-0004: Two-Track Architecture for Voting Module

**Status:** Proposed

**Date:** 2026-03-12

**Authors:** frontend-architect-agent

**Deciders:** @architect, @product-owner, @tech-lead

> ⚠️ `TEMPORARY-NONSTANDARD` — This ADR was authored manually because the `create_adr_file` tool was not available in the current environment. It follows the existing ADR format for this project. Replace with tool-generated artifact when available.

---

## Context and Problem Statement

The application has an existing `/balloting` page that serves as a mock/prototype for voting functionality. It mixes administrator and voter concerns in a single monolithic component (`BallotingContent.component.js`), uses hardcoded mock data (`getMockBallotData()`), simulates voting with `setTimeout` alerts, and contains no real identity verification, signing, or API integration.

The business requirement is to replace this mock with a production-ready digital identity–based voting module that:
- Enforces separate administrative and voter workflows
- Verifies voter identity using digital credentials before allowing participation
- Validates voter eligibility against a configurable credential rule
- Enforces one-person-one-vote with backend confirmation
- Requires digital signing of votes before submission
- Supports a full election lifecycle (draft → scheduled → open → closed → archived)

**Question:** How should the frontend architecture of the new voting module be structured to cleanly separate administrative and voter flows while remaining consistent with the existing `wwc` application patterns?

---

## Decision Drivers

- **Separation of concerns**: Administrative actions (create, manage, lifecycle) must be completely isolated from voter actions (verify, select, sign, submit)
- **Security**: Role-based access control must prevent non-administrators from reaching management screens
- **State complexity**: The voter flow involves 14 sequential states that require a state machine approach
- **Service layer compliance**: Direct HTTP calls from components are prohibited; all API access must go through `src/services/`
- **Repository consistency**: Solution must use existing patterns (AppContext, React Router v6, MUI v6, service-layer convention)
- **Migration safety**: The existing `/balloting` URL must be preserved via redirect to avoid breaking bookmarks or shared links
- **Testability**: Each flow must be independently testable without requiring the other

---

## Considered Options

### Option A: Extend the Existing Monolithic Component

Extend `BallotingContent.component.js` to support real API calls, identity verification, and signing within the same file/component tree.

**Pros:**
- ✅ Minimal structural change
- ✅ No directory renaming needed

**Cons:**
- ❌ Already ~600 lines; will become unmanageable
- ❌ Both admin and voter state live in the same component
- ❌ Cannot independently test admin vs. voter flows
- ❌ Cannot apply different route guards per flow
- ❌ State machine for voter flow would be embedded in component state (not reducers)
- ❌ Violates single-responsibility principle

### Option B: Single Unified Page with Role-Based Rendering

One page component at `/votes` that renders admin or voter content depending on `userRole`.

**Pros:**
- ✅ Single route to maintain

**Cons:**
- ❌ Admin and voter data, state, and permissions mixed at the component level
- ❌ Voter flow state machine interleaved with admin form state
- ❌ Route-level access control is impossible (same URL for both actors)
- ❌ Harder to deep-link directly to voter flow
- ❌ Confusing for future developers

### Option C (Chosen): Two-Track Route-Separated Architecture

Implement two separate routes trees:
- **Admin track**: `/votes`, `/votes/new`, `/votes/:electionId` — protected by `userRole === 'admin'`
- **Voter track**: `/vote/:electionId` — accessible to any authenticated user

Each track has its own page components, custom hooks, and sub-components. The voter track uses a `useReducer`-based state machine (`useVotingBooth`). Both tracks call a new `src/services/voting.js` service.

**Pros:**
- ✅ Clean separation of admin and voter concerns
- ✅ Route-level role enforcement is straightforward
- ✅ Independent testability per track
- ✅ State machine cleanly expressed in `useVotingBooth` hook
- ✅ Each phase of the voter flow is a separate component (each independently testable)
- ✅ Scales naturally (future tracks: results, auditing, delegate voting)

**Cons:**
- ❌ More files to create (mitigated by phased implementation plan)
- ❌ `RouteGuard.js` needs a small extension for role-based protection (acceptable — single shared guard is the right pattern)

---

## Decision

**Chosen: Option C — Two-Track Route-Separated Architecture**

The voter flow's inherent complexity (14 sequential states, identity verification, cryptographic signing) cannot be cleanly handled in a single component. The administrative flow's CRUD + lifecycle management requires independent, testable components with their own form state. These two flows have different actors, different access requirements, and different state lifecycles.

Route separation is the natural, idiomatic React Router v6 approach and aligns with the existing application convention of one-route-per-feature-area.

---

## Implementation Consequences

- `src/pages/Balloting/` renamed to `src/pages/Voting/`
- `src/services/voting.js` created
- `src/config/routes.js` extended with `Votes`, `VotesNew`, `VotesDetail`, `VoteBooth`
- `src/app/DataRouter.js` updated to wire new routes and add `/balloting` redirect
- `RouteGuard.js` extended with optional `requiredRole` prop (non-breaking)
- Existing `BallotingContent.component.js` deleted after Phase 1 components are verified
- Existing `getMockBallotData()` removed after real API integration

---

## Assumptions Pending Confirmation

- `A-002`: The Cognito `custom:role` value for administrators is `'admin'`
- `A-003`: Backend API follows `/api/voting/` namespace (confirmed before Phase 1 integration)

---

## Related Decisions

- ADR-0001: AWS Cognito Authentication — role-based access via `custom:role` attribute
- ADR-0003: Context API over Redux — `AppContext` extended to expose `userRole`; no new global state library needed
- ADR-0005: Digital Vote Signing Strategy — companion ADR
