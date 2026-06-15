# ADR-0003: Context API over Redux for State Management

**Status:** Accepted

**Date:** 2024-Q2

**Authors:** @frontend-lead, @react-team

**Deciders:** @architect, @tech-lead, @ux-lead

---

## Context and Problem Statement

WWC requires global state management for:
- Authentication state (user, tokens, session status)
- Application state (catalog data, notifications, metrics, tenant ID)
- UI state (sidebar open/closed, theme preference)
- Real-time updates (credential status changes, new notifications)

The application is a single-page React application with approximately:
- 15+ page components
- 40+ reusable components
- 5+ service modules
- Complex authentication flows
- WebSocket-based updates (future requirement)

**Question:** What state management solution should WWC use to balance simplicity, performance, and developer experience?

## Decision Drivers

- **Team Expertise:** Team has React 18 experience, limited Redux experience
- **Learning Curve:** Minimize onboarding time for new developers
- **Bundle Size:** Keep application lightweight and fast
- **Development Velocity:** Need rapid feature development
- **Boilerplate:** Minimize repetitive code
- **Type Safety:** Good TypeScript support (future consideration)
- **DevTools:** Debugging and inspection capabilities
- **Performance:** Avoid unnecessary re-renders
- **Testing:** Easy to test components and state logic
- **React 18 Features:** Leverage concurrent features, Suspense

## Considered Options

### Option 1: React Context API + useReducer

**Description:** Use React's built-in Context API with useReducer hook for complex state, enhanced with RxJS for asynchronous event streams.

**Pros:**
- ✅ Zero additional dependencies (built into React)
- ✅ No bundle size increase
- ✅ Simple mental model (just React concepts)
- ✅ Easy to learn for React developers
- ✅ Perfect for authentication and app-level state
- ✅ React 18 concurrent features work natively
- ✅ Minimal boilerplate
- ✅ Good performance with proper memoization
- ✅ Easy to test (standard React testing patterns)
- ✅ Can add RxJS for reactive patterns

**Cons:**
- ❌ No time-travel debugging (without extra tools)
- ❌ No Redux DevTools integration
- ❌ More manual optimization needed (React.memo, useMemo)
- ❌ No middleware ecosystem
- ❌ Complex state updates require careful design
- ❌ Can lead to context proliferation

**Bundle Size Impact:** 0 KB (native React)  
**Implementation Effort:** Low (1 week)

### Option 2: Redux Toolkit

**Description:** Modern Redux with Redux Toolkit (RTK) providing opinionated defaults, built-in Immer, and simplified API.

**Pros:**
- ✅ Industry standard with huge ecosystem
- ✅ Excellent Redux DevTools for debugging
- ✅ Time-travel debugging
- ✅ Middleware ecosystem (thunk, saga, observable)
- ✅ RTK Query for API caching
- ✅ Opinionated structure (less bikeshedding)
- ✅ Immer for immutable updates
- ✅ Great TypeScript support
- ✅ Centralized state management

**Cons:**
- ❌ +14KB bundle size (RTK + dependencies)
- ❌ Steeper learning curve (actions, reducers, selectors)
- ❌ More boilerplate than Context API
- ❌ Team lacks Redux experience
- ❌ Overkill for authentication-centric app
- ❌ Additional testing complexity
- ❌ Async actions require middleware setup

**Bundle Size Impact:** +14 KB gzipped  
**Implementation Effort:** Medium (3 weeks + learning curve)

### Option 3: Zustand

**Description:** Lightweight state management library with hooks-based API, no providers needed.

**Pros:**
- ✅ Tiny bundle size (1KB)
- ✅ Simple hooks-based API
- ✅ No provider wrapper needed
- ✅ Easy to learn
- ✅ Good performance
- ✅ Middleware support (persist, devtools)
- ✅ Redux DevTools integration available

**Cons:**
- ❌ Smaller ecosystem than Redux
- ❌ Less documentation and community resources
- ❌ Team unfamiliar with library
- ❌ Additional dependency to maintain
- ❌ Less opinionated (more design decisions)

**Bundle Size Impact:** +1 KB gzipped  
**Implementation Effort:** Low (1-2 weeks)

### Option 4: Recoil

**Description:** Facebook's state management library designed for React, with atomic state approach.

**Pros:**
- ✅ Designed specifically for React
- ✅ Atomic state approach (granular updates)
- ✅ Built-in async handling
- ✅ Time-travel debugging
- ✅ Excellent concurrency support

**Cons:**
- ❌ Still experimental (0.x version)
- ❌ Smaller community than Redux
- ❌ Different mental model (atoms, selectors)
- ❌ +10KB bundle size
- ❌ Potential breaking changes (not v1.0)
- ❌ Team unfamiliar with library

**Bundle Size Impact:** +10 KB gzipped  
**Implementation Effort:** Medium (2-3 weeks)

### Option 5: MobX

**Description:** Reactive state management using observables and decorators.

**Pros:**
- ✅ Reactive programming model
- ✅ Minimal boilerplate
- ✅ Automatic dependency tracking
- ✅ Good performance

**Cons:**
- ❌ Magic behavior (implicit dependencies)
- ❌ Team unfamiliar with reactive programming
- ❌ Decorators require build configuration
- ❌ Less predictable than Redux
- ❌ Smaller ecosystem

**Bundle Size Impact:** +16 KB gzipped  
**Implementation Effort:** High (4 weeks + learning curve)

## Decision Outcome

**Chosen option:** "React Context API + useReducer + RxJS" because:
1. **Zero Dependencies:** Leverages React built-ins, no extra libraries
2. **Team Alignment:** Team knows React; no new concepts to learn
3. **Application Fit:** WWC has two primary state domains (Auth + App) which map perfectly to two Context providers
4. **Bundle Size:** No impact on application size
5. **Fast Development:** Can start immediately without Redux learning curve
6. **Future-Proof:** Can migrate to Redux later if complexity grows (Context is compatible migration path)
7. **RxJS Bonus:** Already using RxJS for async event streams; natural fit

### Expected Positive Consequences

- **Fast Onboarding:** New developers productive immediately (just React knowledge)
- **Clean Architecture:** Two clear domains (AuthContext, AppContext)
- **Zero Overhead:** No library maintenance or breaking changes
- **Performance:** Direct React optimization patterns (memo, useMemo, useCallback)
- **Testing:** Standard React testing patterns, no special mocking
- **React 18 Ready:** Native support for Suspense, transitions, concurrent rendering

### Expected Negative Consequences

- **Context Proliferation Risk:** May create too many contexts if not disciplined
- **Manual Optimization:** Must manually optimize re-renders (Redux Toolkit does this automatically)
- **No Time-Travel:** Cannot replay state changes (less critical for WWC use case)
- **Debugging:** React DevTools less powerful than Redux DevTools for state inspection

### Mitigation Strategies

- **Context Proliferation:**
  - Strict rule: Maximum 3 contexts (Auth, App, Theme)
  - Document when to add state to context vs local component state
  - Code review guideline: justify any new context
  
- **Performance Optimization:**
  - Create performance guide: when to use memo/useMemo/useCallback
  - ESLint rule for exhaustive deps in useEffect
  - Component profiling in Chrome DevTools
  - Establish baseline performance metrics
  
- **Debugging:**
  - Custom React DevTools integration for contexts
  - Logging middleware for state changes (development mode)
  - State snapshots in error reports (production)
  
- **Future Migration Path:**
  - If application grows to 50+ components needing global state → re-evaluate
  - Document Redux migration path if complexity increases
  - Keep state logic in reducers (easy to move to Redux slices)

## Implementation Details

### Architecture

**Two Primary Contexts:**

**1. AuthContext** (`src/context/AuthContext.js`)
```javascript
AuthProvider
├── State:
│   ├── user (userInfo from Cognito)
│   ├── tokens (idToken, accessToken, refreshToken)
│   ├── loading (authentication check in progress)
│   └── isAuthenticated (boolean)
├── Actions:
│   ├── signIn(email, password)
│   ├── signOut()
│   ├── refreshSession()
│   └── checkAuth()
└── Effects:
    ├── Auto token refresh (before expiration)
    ├── Route protection (redirect to login)
    └── Session persistence (localStorage)
```

**2. AppContext** (`src/context/AppContext.js`)
```javascript
AppStateProvider
├── State (via useReducer):
│   ├── session (tenantId, role, permissions)
│   ├── notifications (array of user notifications)
│   ├── catalog (available credential types)
│   ├── metrics (dashboard statistics)
│   └── connectivity (online/offline status)
├── Reducer Actions:
│   ├── SET_SESSION
│   ├── ADD_NOTIFICATION
│   ├── CLEAR_NOTIFICATIONS
│   ├── UPDATE_CATALOG
│   └── UPDATE_METRICS
└── Custom Hooks:
    ├── useAppState() - Read state
    ├── useSession() - Session shortcuts
    └── useNotifications() - Notification helpers
```

**3. RxJS Integration** (for reactive patterns)
```javascript
// Observable streams for real-time updates
notificationStream$ = new Subject()
credentialStatusStream$ = new Subject()

// Subscribe in AppContext
// Emit from service layer (WebSocket, polling)
```

### File Structure

```
src/
├── context/
│   ├── AuthContext.js       # Authentication state
│   └── AppContext.js         # Application state
├── app/
│   └── App.js                # Wrap with providers
└── pages/
    └── */                    # Consume with useContext
```

### Usage Patterns

**Consuming Auth State:**
```javascript
import { useAuth } from '../context/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, signOut } = useAuth();
  
  if (!isAuthenticated) return <Redirect to="/login" />;
  
  return <div>Hello {user.name}</div>;
}
```

**Consuming App State:**
```javascript
import { useAppState } from '../context/AppContext';

function Dashboard() {
  const { appState, dispatch } = useAppState();
  
  useEffect(() => {
    dispatch({ type: 'UPDATE_METRICS', payload: metrics });
  }, [metrics]);
  
  return <div>{appState.metrics.credentialCount}</div>;
}
```

### Dependencies

- React 18.3.1 (already required)
- RxJS ^7.8.1 (already using for async patterns)

### Performance Guidelines

**Optimization Rules:**
1. **Memoize Context Values**
   ```javascript
   const value = useMemo(() => ({ user, tokens }), [user, tokens]);
   ```

2. **Split Contexts by Update Frequency**
   - Slow-changing: AuthContext (updates on login/logout)
   - Fast-changing: AppContext (notifications, metrics)

3. **Memoize Child Components**
   ```javascript
   const MemoizedComponent = React.memo(ExpensiveComponent);
   ```

4. **Use Selector Pattern**
   ```javascript
   // Good: Only re-renders when role changes
   const role = useAppState(state => state.session.role);
   
   // Bad: Re-renders on any appState change
   const { appState } = useAppState();
   const role = appState.session.role;
   ```

## Validation

**Success Criteria:**
- ✅ Two contexts implemented (Auth, App)
- ✅ No prop drilling beyond 2 levels
- ✅ Page load time < 2 seconds
- ✅ Re-render count < 5 on state update
- ✅ Developer velocity: 2-3 features/week
- ✅ Zero performance complaints in first 3 months
- ✅ Implementation completed in 1 week

**Monitoring:**
- React DevTools Profiler for render counts
- Lighthouse performance scores (monthly)
- Developer satisfaction survey (quarterly)
- State-related bugs per sprint

**Validation Results (2025-Q1):**
- ✅ Page load: 1.2s average
- ✅ Re-render count: 3.1 average
- ✅ Developer velocity: 2.5 features/week
- ✅ Zero context-related bugs
- ✅ Team satisfaction: 4.5/5

## Related Decisions

- Depends on [ADR-0001: AWS Cognito Authentication](0001-aws-cognito-authentication.md) - Auth state structure
- Influences component architecture (functional components, hooks)
- Related to testing strategy (React Testing Library)

## References

- [React Context Documentation](https://react.dev/reference/react/useContext)
- [useReducer Hook](https://react.dev/reference/react/useReducer)
- [RxJS Documentation](https://rxjs.dev/)
- [React Performance Optimization](https://react.dev/learn/render-and-commit)
- [When to use Context vs Redux](https://blog.isquaredsoftware.com/2021/01/context-redux-differences/)

## Notes

### Decision Process

We ran a 1-week spike comparing Context API vs Redux Toolkit:
- Built authentication flow in both approaches
- Measured bundle size, development time, code complexity
- Team voted: 4/5 preferred Context API for simplicity

### Redux Re-evaluation Triggers

We will reconsider Redux if:
1. **Complexity:** State logic exceeds 500 lines across contexts
2. **Performance:** Context updates cause >10 unnecessary re-renders
3. **Debugging:** Multiple state-related bugs per sprint
4. **Team Growth:** New team members struggle with Context patterns
5. **Features:** Need middleware like time-travel debugging, persistence, etc.

### Alternative Considered

**Context API + Redux DevTools Extension:**
- We can use Redux DevTools with Context using `useReducer` and custom middleware
- Not implemented initially (YAGNI principle)
- Available as future enhancement if debugging becomes pain point

---

**Review Date:** 2025-Q2 (Re-evaluate if performance issues arise)  
**Last Updated:** March 5, 2026  
**Status:** In Production, performing excellently with no plans to change
