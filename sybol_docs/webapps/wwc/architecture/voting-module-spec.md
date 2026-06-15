# Frontend Technical Specification
# Digital Identity–Based Voting Module (Balloting Replacement)

**Application:** `webApps/wwc`  
**Feature Area:** Voting / Balloting  
**Replaces:** `src/pages/Balloting/` (mock implementation)  
**Specification Status:** Draft  
**Date:** 2026-03-12  
**Architect:** frontend-architect-agent

---

## Table of Contents

1. [Business Interpretation](#1-business-interpretation)
2. [Scope](#2-scope)
3. [Solution Overview](#3-solution-overview)
4. [Navigation and Routes](#4-navigation-and-routes)
5. [Component Architecture](#5-component-architecture)
6. [State and Interaction Architecture](#6-state-and-interaction-architecture)
7. [API and Data Contracts Needed](#7-api-and-data-contracts-needed)
8. [Access Control and Security Considerations](#8-access-control-and-security-considerations)
9. [UX Behavior and Edge Cases](#9-ux-behavior-and-edge-cases)
10. [Implementation Plan](#10-implementation-plan)
11. [Testing Strategy](#11-testing-strategy)
12. [Documentation Plan](#12-documentation-plan)
13. [Agent Execution Plan](#13-agent-execution-plan)
14. [Suggested Skills](#14-suggested-skills)
15. [Open Questions and Assumptions](#15-open-questions-and-assumptions)

---

## 1. Business Interpretation

### Primary Business Need

The organization requires a digital identity–based voting system that guarantees:

- **Integrity**: only one vote per eligible participant, impossible to double-vote
- **Authenticity**: identity of voter is cryptographically verified via a digital credential before they can cast a vote
- **Non-repudiation**: each vote is digitally signed before submission, making it attributable and tamper-evident
- **Administrative control**: authorized operators can define, publish, and manage the lifecycle of voting processes from creation to archiving

### Primary User Goals

| Actor | Goal |
|---|---|
| Administrator | Create and manage voting processes (elections) across their organization |
| Administrator | View election status, participation metrics, and results |
| Eligible Voter | Participate in an election using their verified digital identity |
| Eligible Voter | Receive confirmation that their vote was recorded |

### Actors / Roles

| Actor | System Role | Access Pattern |
|---|---|---|
| Administrator | `userRole === 'admin'` (Cognito `custom:role`) | Can manage elections (CRUD + lifecycle) |
| Eligible Voter | Any authenticated user with required credential | Can cast votes in open elections |
| Non-eligible User | Authenticated user without required credential | Can see ineligibility message, cannot vote |

### Success Conditions

- An administrator can create, publish, and close an election end-to-end without backend workarounds
- An eligible voter can authenticate, verify their identity, select an option, sign digitally, and submit exactly one vote
- A voter who already voted receives a "already voted" screen — not an error
- A non-eligible voter receives a clear, distinct "not eligible" screen
- Votes submitted without signing are rejected by both the frontend workflow and the backend
- The election detail page shows live participation metrics for administrators

### Core Business Rules (frontend perspective)

1. Only authorized administrators can access the election management interface
2. A voting process must have at least 2 options
3. `endDate` must be strictly after `startDate`
4. Only eligible voters can access the voting flow beyond eligibility check
5. A voter can cast exactly one vote per election (enforced by both frontend and backend)
6. Votes are cryptographically signed (using `blockchain.helper.sign()`) before submission
7. A submitted vote cannot be modified or retracted
8. Voting is only possible when election status is `open`

---

## 2. Scope

### In-Scope

- **Admin management screens** at `/votes`, `/votes/new`, `/votes/:electionId`
- **Voter flow** at `/vote/:electionId` with full 10-step identity-verified voting workflow
- **Service layer**: new `src/services/voting.js` abstracting all election API calls
- **Route migration**: replacement of current `/balloting` route with the new voting routes
- **State machine** for the voter flow using `useReducer` within a `useVotingBooth` hook
- **Identity verification integration** using existing `veia.js` / `w3c.js` resolvers and `blockchain.helper.js` signing
- **Role-based access control** at the route and component level using the existing `userRole` from `AppContext`
- **Internationalization**: all new i18n keys under `voting.*` namespace in `public/locales/en/translation.json` and `es/translation.json`
- **Eligibility rule type**: credential-based eligibility (a specific credential type from the organization catalog)

### Out-of-Scope

- Backend voting API implementation (backend contract assumed, specified as needed)
- Multi-choice voting (single-choice only in this version)
- Rich-text or media voting options (plain text only)
- Vote delegation
- Anonymous voting or zero-knowledge proof integration
- Email/notification delivery to voters (existing notification infra may be leveraged later)
- Results visualization (charts, graphs) — admin sees raw counts for now
- External voter identity providers (only internal credential-based eligibility in v1)
- Storybook component documentation

### Dependencies

| Dependency | Type | Blocking |
|---|---|---|
| Backend voting API (`/api/voting/...`) | Backend service | Yes — voter and admin flows require real endpoints |
| Election eligibility credential type in catalog | Business configuration | Yes — eligibility requires a named credential type |
| `blockchain.helper.sign()` working in production context | Existing code | Partial — sign() uses `sessionStorage.privateKey` |
| `userRole` values defined for admin role in Cognito | Auth / configuration | Yes — role guard requires a known admin role string |
| `AppContext.appState.sessionInfo.userRole` populated on login | Existing auth | Yes — role-based guard uses this value |

---

## 3. Solution Overview

### Summary

The current `/balloting` page is a prototype: it uses hardcoded mock data, simulates voting with `setTimeout` alerts, has no identity verification, no digital signing, and mixes both admin and voter concerns in a single monolithic component. 

The replacement introduces a proper two-track architecture:

1. **Administrative track** (`/votes/*`): A multi-page management interface where administrators create and manage the lifecycle of voting processes.
2. **Voter track** (`/vote/:electionId`): A single, deeply-controlled voting page that drives the user through a strict state machine — from identity verification to signed vote submission.

Both tracks consume a new `src/services/voting.js` service layer. No component makes direct HTTP calls.

### Affected Areas

| Area | Change Type |
|---|---|
| `src/pages/Balloting/` | Refactored in-place → renamed and restructured to `Voting/` |
| `src/services/voting.js` | Net-new |
| `src/config/routes.js` | Extended with new route constants |
| `src/app/DataRouter.js` | Updated to wire new routes |
| `public/locales/*/translation.json` | Extended with `voting.*` keys |
| `src/pages/Balloting/engine.js` | Partially preserved, partially replaced |
| `src/pages/Balloting/Balloting.js` | Replaced by `VotingManagement.js` shell |
| `src/pages/Balloting/Components/BallotingContent.component.js` | Deleted, replaced by focused components |

### User Journeys Impacted

1. Admin creates a new election → sets options, eligibility, dates → validates → saves draft → publishes
2. Admin views election list → inspects status, votes cast, eligible voters
3. Admin opens election detail → views participation data → transitions status (close, archive)
4. Voter navigates to an election → identity verified → eligibility confirmed → one-time vote check → selects option → signs → submits → receives receipt

---

## 4. Navigation and Routes

### New Route Constants (to add to `src/config/routes.js`)

```js
const Votes           = `${Root}/votes`;
const VotesNew        = `${Root}/votes/new`;
const VotesDetail     = `${Root}/votes/:electionId`;
const VoteBooth       = `${Root}/vote/:electionId`;
```

### Route Map

| Path | Page Component | Access | Description |
|---|---|---|---|
| `/balloting` | (redirect → `/votes`) | Admin | Preserve backward compat — redirect to new admin list |
| `/votes` | `VotingManagement` | Admin only | Election management list |
| `/votes/new` | `VotingCreation` | Admin only | Create new election form |
| `/votes/:electionId` | `VotingDetail` | Admin only | Election detail + lifecycle management |
| `/vote/:electionId` | `VotingBooth` | Authenticated user | Full voting flow |

### Navigation Changes

- **Sidebar**: The existing `balloting` sidebar entry (id: `'balloting'`, path: `/balloting`) should be updated to `path: /votes` for admin users. The sidebar item is not shown to non-admin users (eligibility check handled in sidebar visibility logic).
- **Route guard**: The `/votes/*` subtree requires `userRole === 'admin'` (or the confirmed admin role string). Non-admin users hitting these routes are redirected to `/dashboard`.
- **Breadcrumb**: Breadcrumbs should follow the admin hierarchy: `Voting → Election Detail` and `Voting → New Election`.
- **Deep-linking**: All routes support direct navigation and browser refresh. The `VotingBooth` page loads election data on mount from the `:electionId` param.
- **Redirect `/balloting`**: Add a `<Navigate to="/votes" replace />` entry in `DataRouter.js` for the `/balloting` path so any deep-linked or bookmarked URL continues to work.

### `routesNavigation` Entries (for `src/config/routes.js`)

```js
[Votes]: { id: 'votes', parentId: null },
[VotesNew]: { id: 'votes-new', parentId: 'votes' },
// VotesDetail and VoteBooth are dynamic routes — no static nav entry needed
```

Only `Votes` needs a `FLOW_ORDER` entry. Replace `Balloting` in `FLOW_ORDER` with `Votes`.

### URL / Query Param Strategy

| Route | Params | Usage |
|---|---|---|
| `/votes` | `?status=draft\|scheduled\|open\|closed\|archived` (optional) | Filter election list by status |
| `/votes` | `?q=` (optional) | Search elections by title |
| `/votes/new` | none | — |
| `/votes/:electionId` | `:electionId` (path) | Identifies the election |
| `/vote/:electionId` | `:electionId` (path) | Identifies the election for voter |

---

## 5. Component Architecture

### Directory Structure

```
src/pages/Voting/                               ← rename from Balloting/
│
├── index.js                                    ← re-exports VotingManagement (admin entry)
│
├── VotingManagement/                           ← Admin list (/votes)
│   ├── VotingManagement.js                     ← page shell (layout wrapper)
│   ├── VotingManagement.css
│   ├── engine.js                               ← data loading, helpers (refactored from Balloting/engine.js)
│   └── components/
│       ├── ElectionList.component.js           ← table/list of elections
│       ├── ElectionListItem.component.js       ← single row with status + actions
│       └── ElectionFilterBar.component.js      ← status filter + search input
│
├── VotingCreation/                             ← Admin create (/votes/new)
│   ├── VotingCreation.js                       ← page shell
│   ├── VotingCreation.css
│   └── components/
│       ├── ElectionForm.component.js           ← full form container (controlled)
│       ├── OptionsEditor.component.js          ← dynamic add/remove text options
│       ├── EligibilitySelector.component.js    ← catalog credential type picker
│       └── DateRangePicker.component.js        ← start/end date pickers with validation
│
├── VotingDetail/                               ← Admin detail (/votes/:electionId)
│   ├── VotingDetail.js                         ← page shell
│   ├── VotingDetail.css
│   └── components/
│       ├── ElectionDetailCard.component.js     ← displays election metadata
│       ├── ElectionStatusManager.component.js  ← lifecycle action buttons
│       └── ElectionResultsTally.component.js   ← vote count per option (admin only)
│
├── VotingBooth/                                ← Voter flow (/vote/:electionId)
│   ├── VotingBooth.js                          ← page shell + orchestrates useVotingBooth hook
│   ├── VotingBooth.css
│   └── components/
│       ├── VotingStepWrapper.component.js      ← step container w/ stepper/progress UI
│       ├── IdentityVerification.component.js   ← loads & displays credential, triggers verify
│       ├── EligibilityCheck.component.js       ← shows eligibility status, loading state
│       ├── OptionSelector.component.js         ← radio buttons, single choice, confirm trigger
│       ├── VoteConfirmation.component.js       ← "you are about to vote for X" review panel
│       ├── VoteSigning.component.js            ← triggers blockchain.helper.sign(), shows progress
│       ├── VoteSuccess.component.js            ← receipt: confirmation, vote ref, timestamp
│       ├── VoteAlreadyVoted.component.js       ← informational screen (not an error)
│       ├── VoteNotEligible.component.js        ← ineligibility explanation screen
│       ├── ElectionNotOpen.component.js        ← shows reason: not started / closed
│       └── VoteError.component.js             ← generic error with retry option
│
└── hooks/
    ├── useVotingBooth.js                       ← useReducer state machine for voter flow
    ├── useElectionList.js                      ← data fetching + filter state for admin list
    └── useElectionForm.js                      ← form state + validation for creation form
```

### Components to Reuse

| Existing Component | Where Used |
|---|---|
| `Layout` (`header+sidebar+main+footer`) | All `Voting*` admin page shells |
| `Layout` (`header+main+footer`) | `VotingBooth` shell (no sidebar needed in voting flow) |
| `Header`, `Footer`, `Sidebar` | Via Layout wrappers |
| `SybolButton` | All action buttons |
| `SybolTable` / `InfiniteScrollTable` | `ElectionList` (admin) |
| `InfoDrawer` | `ElectionDetailCard` (drawer-based detail) |
| `AlertBanner` via `addAlert` | All result/error notifications |
| `TabNavigation` | `VotingDetail` (tabs: Overview, Results, Settings) |

### New Components (net-new)

All components under `VotingBooth/components/` are net-new.
`OptionsEditor`, `EligibilitySelector`, `DateRangePicker` under `VotingCreation/components/` are net-new.
`ElectionStatusManager` is net-new.

### Component Responsibility Rules

- **Page shells** (`VotingManagement.js`, `VotingCreation.js`, `VotingDetail.js`, `VotingBooth.js`): layout composition + hook wiring only. No business logic, no direct API calls.
- **Content components**: receive data and callbacks as props. Do not call services directly.
- **Hooks** (`useVotingBooth`, `useElectionList`, `useElectionForm`): all service calls, state transitions, and derived state live here.
- **`engine.js`**: shared pure utilities (status color maps, date validation helpers, form validators). No React state, no service calls.

---

## 6. State and Interaction Architecture

### Admin — Election List (`useElectionList`)

```
state:
  elections: []
  loading: boolean
  error: string | null
  filters: { status: string | null, q: string }
  pagination: { page, pageSize, total }

actions:
  loadElections(filters)
  setFilter(key, value)
  clearFilters()
  refresh()

derived:
  filteredElections (client-side filter on top of fetched results when paginating locally)
  isEmpty (elections.length === 0 && !loading)
```

### Admin — Election Form (`useElectionForm`)

```
state:
  form: {
    title: string
    description: string
    startDate: ISO8601 string | null
    endDate: ISO8601 string | null
    options: string[]
    eligibilityCredentialType: string | null
    status: 'draft' | 'scheduled'
  }
  phase: 'idle' | 'validating' | 'saving' | 'saved' | 'error'
  errors: { [field]: string }

actions:
  updateField(field, value)
  addOption()
  removeOption(index)
  updateOption(index, value)
  submit(saveAsDraft: boolean)
  publish()           // submit + transition to scheduled/open depending on dates

validation triggers:
  - On blur per field (inline error)
  - On submit (full validation before save)

business validation rules:
  - title: required, non-empty
  - description: required
  - startDate: required, must be a future datetime
  - endDate: required, must be > startDate
  - options: minimum 2 non-empty values, no duplicates
  - eligibilityCredentialType: required
```

### Admin — Election Detail (`VotingDetail`)

```
state (local component state, no hook needed):
  election: Election | null
  loading: boolean
  error: string | null
  results: { optionId, optionText, count }[] | null
  statusAction: 'publishing' | 'closing' | 'archiving' | null

lifecycle transitions (valid state machine):
  draft          → scheduled (if startDate is in future) / open (if startDate is now/past and endDate future)
  draft          → open      (manual "publish now")
  scheduled      → open      (auto on startDate, or manual)
  open           → closed    (manual close or auto on endDate)
  closed         → archived
```

### Voter — Voting Booth State Machine (`useVotingBooth`)

```
Phase enum (voting flow states):

  LOADING_ELECTION
  ELECTION_NOT_STARTED
  ELECTION_CLOSED
  IDENTITY_VERIFICATION
  ELIGIBILITY_CHECK
  ALREADY_VOTED
  NOT_ELIGIBLE
  SELECTING_OPTION
  CONFIRMING_VOTE
  SIGNING_VOTE
  SUBMITTING_VOTE
  VOTE_SUCCESS
  VOTE_ERROR

State shape:
  phase: Phase (above)
  election: Election | null
  identityCredential: VerifiedCredential | null
  eligibilityResult: { eligible: boolean, reason?: string } | null
  alreadyVoted: boolean
  selectedOption: string | null          // optionId
  signedVote: string | null              // signed JWT payload
  receipt: { voteId, timestamp } | null
  error: { code, message, retryable } | null

Transitions:
  LOADING_ELECTION
    → (election status === 'open')        → IDENTITY_VERIFICATION
    → (election status === 'not_started') → ELECTION_NOT_STARTED
    → (election status === 'closed')      → ELECTION_CLOSED
    → (load error)                        → VOTE_ERROR

  IDENTITY_VERIFICATION
    → (credential verified)              → ELIGIBILITY_CHECK
    → (credential invalid / missing)     → stays (shows inline error)

  ELIGIBILITY_CHECK
    → (already voted = true)             → ALREADY_VOTED
    → (eligible = true, not voted)       → SELECTING_OPTION
    → (eligible = false)                 → NOT_ELIGIBLE
    → (error)                            → VOTE_ERROR

  SELECTING_OPTION
    → (user selects + clicks confirm)    → CONFIRMING_VOTE

  CONFIRMING_VOTE
    → (user confirms)                    → SIGNING_VOTE
    → (user cancels)                     → SELECTING_OPTION

  SIGNING_VOTE
    → (sign() succeeds)                  → SUBMITTING_VOTE
    → (sign() fails)                     → VOTE_ERROR

  SUBMITTING_VOTE
    → (API success)                      → VOTE_SUCCESS
    → (API error)                        → VOTE_ERROR

  VOTE_ERROR
    → (retry if retryable)               → (back to previous retryable phase)
    → (non-retryable)                    → terminal

Actions exposed by hook:
  loadElection(electionId)
  verifyIdentity()
  selectOption(optionId)
  confirmVote()
  cancelConfirmation()
  retryFromError()
```

### Global State Integration

- `useAppState().addAlert()` — used for transient success/error alerts in admin flows
- `useAppState().appState.sessionInfo` — provides `userRole`, `didDocument` for eligibility context
- No new AppContext keys added in Phase 1 (extend only if voter session history needs caching)

---

## 7. API and Data Contracts Needed

### New Service: `src/services/voting.js`

All election-related API calls MUST go through this service. No component or hook imports from `axios` directly.

```js
// Election Management (admin)
getElections(filters)                     // GET /api/voting/elections?status=&q=&page=&pageSize=
getElectionById(electionId)               // GET /api/voting/elections/:id
createElection(data)                      // POST /api/voting/elections
updateElection(electionId, data)          // PUT /api/voting/elections/:id
publishElection(electionId)              // POST /api/voting/elections/:id/publish
closeElection(electionId)                 // POST /api/voting/elections/:id/close
archiveElection(electionId)               // POST /api/voting/elections/:id/archive
getElectionResults(electionId)            // GET /api/voting/elections/:id/results

// Voter operations
checkEligibility(electionId, did)         // GET /api/voting/elections/:id/eligibility?did=
checkAlreadyVoted(electionId, did)        // GET /api/voting/elections/:id/vote-status?did=
submitVote(electionId, signedVotePayload) // POST /api/voting/elections/:id/votes
```

All functions should use the existing `axios.helper.js` instance (which handles auth headers, tenant context, and error normalization) — the same pattern used throughout `sybol.js`.

### Request / Response Models

#### `Election` object (backend response)

```json
{
  "id": "string (UUID)",
  "title": "string",
  "description": "string",
  "startDate": "ISO8601",
  "endDate": "ISO8601",
  "status": "draft | scheduled | open | closed | archived",
  "options": [
    { "id": "string", "text": "string", "order": 0 }
  ],
  "eligibilityCredentialType": "string (catalog credential type ID)",
  "totalVotes": 0,
  "eligibleVoters": 0,
  "createdAt": "ISO8601",
  "createdBy": "string (DID)"
}
```

#### `CreateElection` request body

```json
{
  "title": "string",
  "description": "string",
  "startDate": "ISO8601",
  "endDate": "ISO8601",
  "options": ["string"],
  "eligibilityCredentialType": "string"
}
```

#### `EligibilityResult` response

```json
{
  "eligible": true,
  "reason": "string | null",
  "credentialId": "string | null"
}
```

#### `VoteStatusResult` response

```json
{
  "hasVoted": true,
  "votedAt": "ISO8601 | null"
}
```

#### `VoteSubmission` request body

```json
{
  "electionId": "string",
  "optionId": "string",
  "signedVoteJwt": "string",  // signed by blockchain.helper.sign()
  "voterDid": "string"
}
```

#### `VoteReceipt` response

```json
{
  "voteId": "string",
  "electionId": "string",
  "optionId": "string",
  "timestamp": "ISO8601",
  "confirmed": true
}
```

#### `ElectionResults` response

```json
{
  "electionId": "string",
  "totalVotes": 0,
  "results": [
    { "optionId": "string", "optionText": "string", "count": 0, "percentage": 0.0 }
  ]
}
```

### Identity Verification Integration

Identity verification reuses existing resolvers from `veia.js` / `w3c.js`:

- `extractClaimsFromCredential(credentialData)` — extracts `{ subjectId, issuerId, claimsList }` from voter's stored credential  
- The voter's DID is read from `appState.sessionInfo.didDocument`
- `checkEligibility(electionId, did)` is called with the voter's DID after credential resolution

### Digital Signing Integration

Vote signing uses `blockchain.helper.sign(credentials, verification)` which:
- Reads `sessionStorage.privateKey` or `jwk`
- Signs a VP JWT (ES256)
- Returns a signed JWT string

The `signedVoteJwt` sent to `submitVote` is this signed JWT.

**ASSUMPTION `A-001`**: `blockchain.helper.sign()` is operational in the production deployment context and `sessionStorage.privateKey/jwk` is available after the voter completes identity verification. If not, a key availability check must be added before entering `SIGNING_VOTE` phase.

### Error Contract Expectations

Frontend expects all API errors to be normalized by `axios.helper.js` into:

```json
{
  "code": "string",
  "message": "string",
  "retryable": true
}
```

Specific error codes the voting flow must handle:

| Code | Meaning | Frontend behavior |
|---|---|---|
| `ELECTION_NOT_FOUND` | Invalid election ID | VOTE_ERROR (non-retryable) |
| `ELECTION_NOT_OPEN` | Status not 'open' | Show appropriate closed/not-started screen |
| `ALREADY_VOTED` | Voter already submitted | ALREADY_VOTED phase |
| `NOT_ELIGIBLE` | Voter not eligible | NOT_ELIGIBLE phase |
| `INVALID_SIGNATURE` | Signed vote rejected | VOTE_ERROR with re-sign option |
| `DUPLICATE_VOTE` | Race condition — vote already exists | ALREADY_VOTED phase |

---

## 8. Access Control and Security Considerations

### Role-Based Visibility

| Route | Required Role | Fallback |
|---|---|---|
| `/votes` | `userRole === 'admin'` | Redirect to `/dashboard` |
| `/votes/new` | `userRole === 'admin'` | Redirect to `/dashboard` |
| `/votes/:electionId` | `userRole === 'admin'` | Redirect to `/dashboard` |
| `/vote/:electionId` | Any authenticated user | Redirect to `Login` if unauthenticated |

**ASSUMPTION `A-002`**: The admin role string is `'admin'` (Cognito `custom:role`). This must be confirmed and aligned with the deployed Cognito User Pool attribute. If the role string differs (e.g., `'backoffice'`, `'operator'`), the guard conditions must be updated.

### Route Guard Implementation

The existing `RouteGuard.js` component does not currently implement role-based checks — only auth-based checks. Two options exist for enforcing admin access:

**Option A (Recommended)**: Extend `RouteGuard` to accept an optional `requiredRole` prop and redirect if `appState.sessionInfo.userRole !== requiredRole`. Wire this at the route level in `DataRouter.js`.

**Option B**: Add role check logic inside each admin page component (less clean, but no changes to shared RouteGuard needed).

Option A is recommended for consistency with future role-restricted routes.

### Sensitive Data Handling

- The `signedVoteJwt` payload must NEVER be logged, printed to console, or stored in `localStorage`/`sessionStorage` beyond the immediate submission request
- Voter's DID should not be exposed in the ballot receipt UI beyond a truncated display
- Election results are admin-only; the `getElectionResults` call should only be initiated from pages protected by admin route guard
- Voter's selected option must not be persisted in `sessionStorage` or `localStorage` after submission

### Frontend Security Notes

- The frontend's digital signing (`blockchain.helper.sign()`) provides non-repudiation at the presentation layer. The backend MUST also verify the signature independently — the frontend signing step does not replace backend verification.
- No vote payload should be constructed or sent without completing the signing step first. If `sign()` throws, the `SUBMITTING_VOTE` phase must never be entered.
- The election ID from the URL param (`:electionId`) must be validated server-side; the frontend should not trust the param as an access control mechanism.
- All API calls must include the existing auth token headers managed by `axios.helper.js`.

### Auditability

- Frontend must pass `voterDid` in the `VoteSubmission` payload for backend audit trail
- The `VoteReceipt` response should be displayed in full and optionally downloadable as a text file (using existing `blockchainHelper.downloadTxt()`)

---

## 9. UX Behavior and Edge Cases

### Admin: Election List (`/votes`)

| State | Behavior |
|---|---|
| Loading | Skeleton rows or spinner inside the table area |
| Empty list | Empty state illustration with "Create your first election" CTA |
| Filtered empty | "No elections match your filter" with a "Clear filters" link |
| Error loading | Alert banner with retry button |
| Mix of statuses | Status chip differentiates by color; open elections should visually stand out |
| Election requires action (draft) | Optional "Publish" quick action in row |

### Admin: Create Election (`/votes/new`)

| State | Behavior |
|---|---|
| Initial | Clean form, no validation errors shown |
| Inline validation (blur) | Per-field error shown below input |
| Submit with errors | All errors shown simultaneously; page scrolls to first error |
| `endDate <= startDate` | Inline error on endDate immediately on change |
| Fewer than 2 options | Error on the options section; submit blocked |
| Saving | Submit button shows spinner; inputs disabled |
| Saved (draft) | Redirect to `/votes/:electionId` with success alert |
| Publish immediately | Transition to `open` or `scheduled` based on `startDate` |
| Publish error | Error alert; form remains editable |
| Discard / cancel | Confirmation dialog before navigating away if form is dirty |

### Admin: Election Detail (`/votes/:electionId`)

| State | Behavior |
|---|---|
| Loading | Skeleton layout |
| Draft status | Show "Publish" action, "Edit" option, "Delete" with confirmation |
| Scheduled status | Show "Cancel" (revert to draft) and "Open Now" |
| Open status | Show "Close Early" with confirmation; results live-update (polling optional) |
| Closed status | Show "Archive" action; results displayed |
| Archived | Read-only view |
| Invalid electionId | Error page: "Election not found" with back link |

### Voter: Voting Booth (`/vote/:electionId`)

**Step-by-step UX behavior:**

1. **LOADING_ELECTION**: Full-page spinner. No interaction possible.

2. **ELECTION_NOT_STARTED**: Informational card showing election title, start date/time. No voting action available. "Come back when the election opens" message.

3. **ELECTION_CLOSED**: Informational card. Shows election title, end date. "This election has ended" message.

4. **IDENTITY_VERIFICATION**: Shows a prompt asking the user to present their digital credential. The user's stored credential is loaded from `appState.sessionInfo.didDocument` or fetched. Shows issuer, credential type, and status. A "Verify My Identity" CTA triggers the verification call. If the credential is expired or revoked, shows inline error with explanation.

5. **ELIGIBILITY_CHECK**: Loading indicator while eligibility is being checked. No interaction.

6. **ALREADY_VOTED**: Informational, positive-toned screen. Shows "You have already voted in this election." Optionally shows the timestamp of the previous vote (from `votedAt`). No voting actions.

7. **NOT_ELIGIBLE**: Clear, non-judgmental explanation that the user does not hold the required credential. Shows which credential type is required. Has a link to the holder credentials section if they believe they should be eligible.

8. **SELECTING_OPTION**: Shows election title, description, and a radio-button list of options. "Confirm My Choice" button is disabled until an option is selected. Deselecting is allowed.

9. **CONFIRMING_VOTE**: Review panel showing the selected option text and election title. "This action cannot be undone" advisory. Two actions: "Confirm Vote" and "Go Back" (returns to SELECTING_OPTION).

10. **SIGNING_VOTE**: Full-page loading state. Message: "Signing your vote digitally, please wait." No user interaction. If signing takes > 5 seconds, show a "this is taking longer than expected" advisory without aborting.

11. **SUBMITTING_VOTE**: Full-page loading state. Message: "Submitting your vote securely." No user interaction.

12. **VOTE_SUCCESS**: Confirmation card with:
    - Vote confirmation checkmark
    - Election title
    - Selected option (displayed)
    - Receipt ID (`voteId`)
    - Timestamp
    - Optional "Download receipt" button (using `blockchainHelper.downloadTxt()`)
    - Link back to dashboard

13. **VOTE_ERROR**: Error card with:
    - Friendly error message (no technical details in default view)
    - "Retry" button (visible only if `error.retryable === true`)
    - "Return to Dashboard" fallback
    - Expandable technical detail (accordion, hidden by default)

### Edge Cases

| Scenario | Handling |
|---|---|
| User navigates away mid-flow | No unsaved state to lose; re-entering resets the flow |
| Network timeout during signing | Retry is safe as long as `submitVote` is not in progress |
| Network timeout during submission | Show error; retry is allowed only if backend confirms no vote was recorded |
| Clock skew: `startDate` in future but less than 1 minute away | Show "election opens very soon" rather than generic not-started message |
| Election deleted while user is in flow | Handle 404 from `getElectionById` as VOTE_ERROR with "election not found" |
| Two browser tabs voting simultaneously | Backend enforces one-vote; second tab receives `DUPLICATE_VOTE` → ALREADY_VOTED |
| Credential revoked between eligibility check and submission | Backend rejects signature; frontend shows VOTE_ERROR with "identity verification issue" |
| Admin role user navigating to `/vote/:electionId` | Allowed — admin can also be a voter if they hold the required credential |

### Internationalization

All voter flow phases and admin form messages must have translations. New keys live under:
- `voting.list.*` — admin list
- `voting.create.*` — create form
- `voting.detail.*` — detail page
- `voting.booth.*` — voter flow (all phases)
- `voting.errors.*` — error messages

No changes to existing `balloting.*` keys until migration is confirmed stable, then they can be removed.

### Accessibility

- All vote options must be selectable via keyboard (radio buttons → native focus/tab)
- Status chips must include accessible `aria-label` describing the status
- VotingBooth step transitions must use `aria-live="polite"` for screen reader announcements
- Confirmation dialog must trap focus correctly
- All loading states must expose `aria-busy="true"` on the loading container

---

## 10. Implementation Plan

### Phase 0: Preparation (foundation, no visible changes to users)

**Goal**: Lay the service, route, and test infrastructure before touching the UI.

| Task | Files Affected | Notes |
|---|---|---|
| P0-1: Create `src/services/voting.js` with stub implementations | New file | Return mock data initially; real endpoints filled in as backend is ready |
| P0-2: Add route constants to `src/config/routes.js` | `routes.js` | Add `Votes`, `VotesNew`, `VotesDetail`, `VoteBooth`; keep `Balloting` |
| P0-3: Add redirect for `/balloting` → `/votes` in `DataRouter.js` | `DataRouter.js` | Add `<Navigate to="/votes" replace />` |
| P0-4: Wire new routes in `DataRouter.js` (pointing to placeholder pages) | `DataRouter.js` | Placeholder pages can be empty shell components initially |
| P0-5: Rename `src/pages/Balloting/` to `src/pages/Voting/` | Directory rename | Update all imports in `DataRouter.js` and `index.js` |
| P0-6: Extend `RouteGuard` with `requiredRole` prop to support admin-only routes | `RouteGuard.js` | Non-breaking — existing routes don't pass `requiredRole` |

### Phase 1: Admin Management Track

**Goal**: Functional admin election list, create, and detail screens.

| Task | Files Created/Modified | Notes |
|---|---|---|
| P1-1: `useElectionList` hook | `hooks/useElectionList.js` | |
| P1-2: `VotingManagement` page + `ElectionList` component | New files under `VotingManagement/` | Replaces `BallotingContent.component.js` list view |
| P1-3: `ElectionFilterBar` | New | Status filter + search |
| P1-4: `useElectionForm` hook with full validation | `hooks/useElectionForm.js` | |
| P1-5: `VotingCreation` page + `ElectionForm` + subcomponents | New files under `VotingCreation/` | Replaces create ballot modal |
| P1-6: `VotingDetail` page + `ElectionDetailCard` + `ElectionStatusManager` | New files under `VotingDetail/` | |
| P1-7: `ElectionResultsTally` | New | Admin-only vote counts |
| P1-8: Extend `engine.js` with date helpers, status color map | `Voting/engine.js` | Refactored from `Balloting/engine.js`; remove `getMockBallotData` |
| P1-9: Admin i18n keys | `public/locales/*/translation.json` | Add `voting.list.*`, `voting.create.*`, `voting.detail.*` |
| P1-10: Update sidebar navigation for admin to point to `/votes` | `Sidebar` component or config | |

### Phase 2: Voter Flow Track

**Goal**: Full end-to-end voter flow from identity verification to vote receipt.

| Task | Files Created/Modified | Notes |
|---|---|---|
| P2-1: `useVotingBooth` hook with full state machine | `hooks/useVotingBooth.js` | |
| P2-2: `VotingBooth` page shell | `VotingBooth/VotingBooth.js` | |
| P2-3: `VotingStepWrapper` | New | Wraps each phase UI |
| P2-4: `IdentityVerification` component | New | Uses credential resolver + DID from context |
| P2-5: `EligibilityCheck` component | New | Loading state + calls `checkEligibility` |
| P2-6: `OptionSelector` component | New | Radio buttons, single choice |
| P2-7: `VoteConfirmation` component | New | Review + confirm/cancel |
| P2-8: `VoteSigning` component | New | Calls `blockchain.helper.sign()` |
| P2-9: `VoteSuccess` component | New | Receipt display + download |
| P2-10: `VoteAlreadyVoted`, `VoteNotEligible`, `ElectionNotOpen`, `VoteError` | New | Informational / dead-end states |
| P2-11: Voter i18n keys | `public/locales/*/translation.json` | Add `voting.booth.*`, `voting.errors.*` |
| P2-12: Wire `/vote/:electionId` in `DataRouter.js` | `DataRouter.js` | Replace placeholder |
| P2-13: Update `FLOW_ORDER` and `routesNavigation` | `routes.js` | |

### Phase 3: Integration and Polish

| Task | Notes |
|---|---|
| P3-1: Connect `voting.js` to real backend endpoints | Requires backend to be available |
| P3-2: Remove `getMockBallotData()` from engine.js | After real API is confirmed working |
| P3-3: Remove old `BallotingContent.component.js` | After Phase 1 components are verified |
| P3-4: Remove `Balloting.js` and `Balloting.css` | After route replacement confirmed |
| P3-5: Remove `balloting.*` i18n keys (or keep as legacy) | After migration is stable |
| P3-6: Add vote receipt download functionality | `VoteSuccess` + `blockchainHelper.downloadTxt()` |
| P3-7: Accessibility pass | `aria-live`, focus trapping in dialogs, keyboard test |
| P3-8: Performance pass | Loading state latency analysis, lazy-load `VotingBooth` route |

### Risk Areas

| Risk | Mitigation |
|---|---|
| Backend API not ready for Phase 1/2 | Use stub responses in `voting.js` mock mode |
| `blockchain.helper.sign()` not working in production key context | Add key availability check before SIGNING_VOTE; coordinate with infra |
| Admin role string value unknown | Confirm with backend team before committing guard condition |
| Credential resolution timing (async, slow) | Add timeout handling in `useVotingBooth`; show "taking longer than expected" advisory |
| Double-vote race condition | Backend must enforce idempotency; frontend maps `DUPLICATE_VOTE` to ALREADY_VOTED |

---

## 11. Testing Strategy

### Unit Tests

| Target | What to Test |
|---|---|
| `useVotingBooth` (reducer) | All phase transitions with simulated actions; all edge cases in the state machine |
| `useElectionForm` | Field validation rules; all error conditions; form submission lifecycle |
| `useElectionList` | Filter state mutations; loading / error states |
| `engine.js` helpers | Date validation, status color mapping, form validators |
| `voting.js` | API call signatures, error normalization (mock axios) |

### Component Tests (React Testing Library)

| Component | What to Test |
|---|---|
| `ElectionForm` | Renders all fields; shows errors on submit; disables submit when saving |
| `OptionsEditor` | Add/remove options; enforces minimum 2; updates values correctly |
| `OptionSelector` | Radio selection; confirm button disabled until option selected |
| `VoteConfirmation` | Shows selected option; confirm + cancel paths |
| `VoteSigning` | Loading state displayed; does not show UI action buttons |
| `VoteSuccess` | Receipt data rendered; download button present |
| `VoteNotEligible` | "Not eligible" messaging; link to credential holder present |
| `VoteAlreadyVoted` | Informational content; no voting actions present |
| `ElectionStatusManager` | Shows correct actions per status; disables others |
| `ElectionList` | Renders election rows; empty state; loading skeleton |

### Integration Tests

| Scenario | Scope |
|---|---|
| Full admin create flow | `useElectionForm` → `voting.js` mock → success redirect |
| Full voter flow: eligible, new voter | `useVotingBooth` drives from LOADING → identity → eligibility → sign → submit → success |
| Full voter flow: already voted | `useVotingBooth` reaches ALREADY_VOTED after eligibility check |
| Full voter flow: not eligible | `useVotingBooth` reaches NOT_ELIGIBLE after eligibility check |
| Election not open (closed status) | `useVotingBooth` enters ELECTION_CLOSED on load |
| Signing failure → error state | `sign()` throws → VOTE_ERROR with retryable flag |
| Submission failure (network) → retry | API rejects → retryable error → user retries → success |

### End-to-End Scenarios (webapp-testing skill / Playwright)

| Scenario | User Journey |
|---|---|
| Admin creates election | Login → `/votes` → "New Election" → fill form → save draft → verify list |
| Admin publishes election | `/votes/:id` → "Publish" → confirm status change to scheduled/open |
| Eligible voter votes | Login → `/vote/:id` → verify identity → select → confirm → sign → submit → receipt |
| Non-eligible user visits booth | Login → `/vote/:id` → identity verified → NOT_ELIGIBLE screen |
| Voter tries to vote twice | Vote → receipt → visit same URL again → ALREADY_VOTED screen |

### Regression Risk Areas

- `DataRouter.js` changes: any route addition/modification should be tested for catch-all behavior
- Existing `sybol.js` / `veia.js` / `w3c.js`: no changes should be made to these services for this feature
- `AppContext.buildBaseSession()`: no changes; only reads `userRole` from existing session
- `blockchain.helper.sign()`: no changes; only called by `VoteSigning`
- Sidebar navigation: verify that non-admin users do not see the Voting entry after migration

### Accessibility Validation Targets

- Keyboard navigation through all voting options (radio buttons)
- Screen reader announces phase transitions (aria-live regions)
- Modal / dialog focus trapping in `VoteConfirmation`
- Color is not the sole indicator of status in `ElectionStatusChip`

---

## 12. Documentation Plan

### Files to Document

| File | Documentation Need |
|---|---|
| `src/services/voting.js` | JSDoc for each exported function: params, return type, error codes |
| `hooks/useVotingBooth.js` | JSDoc: state shape, all actions, phase transition table |
| `hooks/useElectionForm.js` | JSDoc: form shape, all actions, validation rules |
| `docs/architecture/voting-module-spec.md` | This specification |
| `src/pages/Voting/README.md` | Module overview: purpose, sub-folder map, migration note |

### i18n Documentation

- Document all new `voting.*` translation keys in `docs/architecture/voting-module-spec.md` under an appendix
- Spanish translations should be completed alongside English (no placeholder keys shipped to production)

### README Changes

- `src/pages/Voting/README.md` must include:
  - Module purpose and role
  - Admin vs. voter track separation
  - Migration note: "replaces `src/pages/Balloting/` mock"
  - Service layer dependency (`voting.js`)
  - State machine summary (link to this spec)
  - Known assumptions (`A-001`, `A-002`, `A-003`)

### ADR Plan

#### ADR-0004: Voting Module Architecture

**Status:** Proposed (`TEMPORARY-NONSTANDARD` — `create_adr_file` tool not available)

**Decision Statement:** Implement the voting module as a two-track, route-separated architecture: an admin management track (`/votes/*`) and a voter flow track (`/vote/:electionId`), replacing the existing monolithic `/balloting` mock page.

**Alternatives Considered:**
- Alternative A: Extend the existing monolithic `BallotingContent.component.js` → rejected due to tight coupling of admin and voter concerns, lack of state machine, and inability to enforce per-phase security
- Alternative B: Single unified page with role-based rendering → rejected because mixing admin and voter state in one component creates fragility and complicates testing
- Alternative C (chosen): Two-track route-separated architecture with dedicated service layer and useReducer state machine for voter flow

**Assumptions Pending Confirmation:**
- `A-002`: Admin role string in Cognito is `'admin'`
- `A-003`: Backend API routes follow the `/api/voting/...` namespace (see Section 7)

**Impacted Modules:** `routes.js`, `DataRouter.js`, `src/pages/Voting/`, `src/services/voting.js`

---

#### ADR-0005: Digital Vote Signing Strategy

**Status:** Proposed (`TEMPORARY-NONSTANDARD` — `create_adr_file` tool not available)

**Decision Statement:** Use the existing `blockchain.helper.sign()` function to sign votes as VP JWTs using ES256 before submission, without introducing a new signing library or mechanism.

**Alternatives Considered:**
- Alternative A: Create new signing utility specifically for votes → rejected because `blockchain.helper.sign()` already handles ES256 + P-256 key pair + sessionStorage.jwk
- Alternative B: Submit unsigned votes and rely entirely on backend verification → rejected because non-repudiation at the frontend layer is a stated business requirement
- Alternative C (chosen): Reuse `blockchain.helper.sign()` as-is; gate `SUBMITTING_VOTE` on successful signing

**Assumptions Pending Confirmation:**
- `A-001`: `sessionStorage.privateKey/jwk` is populated at the point the voter enters the voting flow

**Impacted Modules:** `VotingBooth/hooks/useVotingBooth.js`, `VotingSigning.component.js`, `blockchain.helper.js`

---

## 13. Agent Execution Plan

The following downstream agents should execute the implementation. Each agent receives the corresponding section of this specification as input.

### Execution Order

```
1. product-analyst-agent     → Validate/expand business rules and requirements (Section 1-2)
2. ux-specification-agent    → Produce wireframes and interaction spec (Section 9)
3. api-contract-alingment    → Validate/finalize voting.js API contract (Section 7)
4. react-component-planner   → Produce component implementation plan (Section 5-6)
5. test-strategy             → Produce test plan and scenarios (Section 11)
6. documentation-writer-agent→ Produce README, i18n key list, JSDoc specs (Section 12)
7. react-component-impl*     → Execute implementation per component plan
```

*`react-component-implementation` skill executes after `react-component-planner` output is approved.

### Agent Inputs and Expected Outputs

| Agent | Input | Expected Output |
|---|---|---|
| `product-analyst-agent` | Sections 1-2 of this spec + business requirements from user | Validated functional spec with acceptance criteria per flow |
| `ux-specification-agent` | Sections 3, 4, 9 + validated functional spec | UX wireframes / behavior spec per screen and state |
| `api-contract-alingment` | Section 7 + existing `sybol.js` patterns | Confirmed `voting.js` function signatures and error contract |
| `react-component-planner` | Sections 5, 6 + UX spec + API contract | Component implementation plan (props, state API, hooks) |
| `test-strategy` | Sections 11 + component plan | Detailed test scenarios with acceptance criteria |
| `documentation-writer-agent` | Full spec | `src/pages/Voting/README.md`, i18n key list, JSDoc templates |
| `react-component-implementation` skill | Component plan output | Production-ready React code for each component and hook |

### Architecture Synthesis Checkpoints

Before each agent hands off to the next, the `frontend-architect-agent` must verify:
1. Output is internally consistent with this specification
2. No direct HTTP calls are introduced in components
3. No TypeScript or Redux migrations have been introduced
4. No existing shared service files (`sybol.js`, `veia.js`, `w3c.js`, `blockchain.helper.js`) have been modified

---

## 14. Suggested Skills

| Skill | When to Invoke | Expected Deliverable |
|---|---|---|
| `react-component-implementation` | After `react-component-planner` output is approved | All component files under `src/pages/Voting/` |
| `webapp-testing` | After Phase 2 is implemented | Playwright E2E scenarios for voter flow |
| `frontend-design` | If UX spec requires custom visual design beyond MUI defaults | Styled components, custom CSS for VotingBooth phases |
| `doc-coauthoring` | When writing the final module README and architecture narrative | `src/pages/Voting/README.md` |

---

## 15. Open Questions and Assumptions

### Assumptions

| ID | Assumption | Risk if Wrong | Resolution |
|---|---|---|---|
| `A-001` | `sessionStorage.privateKey` or `sessionStorage.jwk` is available when the voter enters the voting booth flow | Signing step will fail; voter cannot complete voting | Confirm with identity/auth engineers how and when keys are written to sessionStorage |
| `A-002` | The Cognito `custom:role` attribute value for administrators is exactly the string `'admin'` | Route guard will be misconfigured; admins may be blocked or non-admins may gain access | Confirm with backend team the exact role string(s) for admin users |
| `A-003` | The backend voting API namespace is `/api/voting/` and follows the REST patterns described in Section 7 | `voting.js` service will need rework | Confirm API contract with backend team before Phase 1 integration |
| `A-004` | A single `eligibilityCredentialType` (credential type identifier string) is sufficient to check voter eligibility | More complex eligibility rules will require backend support | Product confirmation: can the first version assume a simple one-credential-type eligibility rule? |
| `A-005` | The share-ballot-to-contacts feature in the current mock is not being carried forward (it was a mock-only invitation flow) | A real invitation/sharing flow may be expected | Product confirmation needed: is the ballot sharing feature intended to exist in production? If yes, it is out-of-scope for this spec and should be treated as a separate feature |

### Open Questions

1. **What exact role string(s) identify administrators in Cognito?** Required to implement route guards correctly.
2. **Is the signing key always available in sessionStorage at the point of voting?** What is the lifecycle of `sessionStorage.privateKey/jwk` — when is it set, when does it expire?
3. **Does the backend vote submission endpoint need to be idempotent?** Can a voter safely retry a failed submission without risk of recording a duplicate vote?
4. **Is there a requirement to display election results to voters after the election closes?** If so, the voter-accessible results view needs to be designed.
5. **Can an administrator also be a voter in the same election?** If yes, the admin role guard on `/votes` must not prevent the same user from accessing `/vote/:electionId`.
6. **Should the voter flow be accessible via a direct URL shared externally (e.g., email link)?** If so, deep-link behavior must ensure the auth redirect preserves the target URL.
7. **Is the "share ballot" feature from the current mock in scope for production?** Currently `loadSybolContacts()` uses `getDidDocument()` to load contacts — if sharing is in scope, a separate specification is needed.
8. **What is the expected response time for eligibility checking?** If it is slow (>2s), a loading experience with progress advisory is needed.

### Compatibility Notes

| Concern | Status |
|---|---|
| React 18 + JavaScript (no TypeScript) | ✅ Spec fully compliant — no TypeScript introduced |
| CRA + react-app-rewired | ✅ No build changes needed |
| MUI v6 + Emotion | ✅ All new components use MUI primitives |
| i18next with `public/locales` | ✅ New keys added under `voting.*` namespace |
| `AppContext` (`useAppState`) for alerts and session | ✅ Only reads `sessionInfo.userRole` and calls `addAlert()` |
| Centralized route config via `routes.js` | ✅ New constants added; `Balloting` kept for redirect |
| Service layer (`src/services/`) | ✅ New `voting.js` follows same pattern as `sybol.js` |
| Existing `blockchain.helper.sign()` for signing | ✅ Reused without modification |
| `RouteGuard` extension | ⚠️ DEVIATION: adding `requiredRole` prop requires a small change to `RouteGuard.js` — this is the only change to an existing shared component. Justification: role-based route protection is a cross-cutting concern that belongs in the centralized guard, not in individual pages. |
| Sidebar navigation entry rename (`balloting` → `votes`) | ⚠️ The existing sidebar `id: 'balloting'` must be updated to `id: 'votes'` with path `/votes`. This affects only the sidebar config/data and is backwards-compatible with no user-facing breakage after redirect is in place. |
| `/balloting` backward compatibility | ✅ Preserved via `<Navigate to="/votes" replace />` in `DataRouter.js` |
