# Developer Style DNA

---

## 1. Analysis Scope

- **Analyzed path:** `/Users/rox/Projects/sybolRelases/blockchainManager/src/`
- **Number of files inspected:** 18 source files
- **File types:** `.js` (ES Modules)
- **Directories covered:** `services/`, `controllers/`, `routes/`, `helpers/`, `repositories/`, `persistence/`, `standard/`, `config/`, `bootstrap/`, `utils/`

---

## 2. Folder Architecture Style

The project follows a **strict layered architecture** organized by technical role, not by feature.

```
src/
  bootstrap/        ← application startup and wiring
  config/           ← constants and static configuration
  exposition/
    api/
      controllers/  ← HTTP request handlers
      routes/       ← Express route definitions
  helpers/          ← pure utility functions (no business logic)
  persistence/
    database/
      postgres/     ← raw database queries and connection
  repositories/     ← data access abstraction over persistence
  services/         ← core business logic
  standard/         ← shared base classes (AppError, AppResponse, LOG)
  utils/            ← low-level address/key utilities
```

- Logic is grouped **by layer**, not by domain.
- `standard/` acts as a shared kernel: logging, error handling, and response shaping.
- `exposition/` encapsulates all HTTP surface (controllers + routes).
- `bootstrap/` owns application initialization and dependency wiring.
- `helpers/` are stateless utilities injected or imported directly.

---

## 3. File Structure Style

Every file follows a **rigid, consistent section structure** using a fixed separator style.

**Section separator format:**
```js
// ---------------------------------------------------------------------------
// SECTION NAME
// ---------------------------------------------------------------------------
```
- Separator: 75 dashes (`-`)
- Section names: UPPERCASE
- One blank line before each separator, zero blank lines after

**Observed section ordering (strong convention):**
1. `//SYBOLID` ← file header attribution comment
2. `const MODULE_NAME = 'filename.js';` ← immediate after header
3. `// IMPORTS`
4. `// CONSTANTS` or `// GLOBAL VARIABLES`
5. `// PRIVATE FUNCTIONS`
6. `// PUBLIC FUNCTIONS`
7. `// EXPORTS`

**Example pattern (from `blockchain.controller.js`, `wallet.service.js`, `evm.service.js`):**
```js
//SYBOLID
const MODULE_NAME = 'evm.service.js';

// ---------------------------------------------------------------------------
// IMPORTS
// ---------------------------------------------------------------------------
// ------NODE MODULES---------------------------------------------------------
import { ethers } from 'ethers';
// ------PRIVATE MODULES------------------------------------------------------
import LOG from '#logs';
// ------FILE MODULES---------------------------------------------------------
import walletService from './wallet.service.js';
// ---------------------------------------------------------------------------
// CONSTANTS
// ---------------------------------------------------------------------------
let config;
let defaultProvider;
// ---------------------------------------------------------------------------
// PUBLIC FUNCTIONS
// ---------------------------------------------------------------------------
const init = async (_config) => { ... }

export default { init, getSigner }
```

---

## 4. Import Conventions

Imports are **always split into three explicitly labeled sub-groups** using a distinct inline separator style:

```js
// ------NODE MODULES---------------------------------------------------------
import { ethers } from 'ethers';

// ------PRIVATE MODULES------------------------------------------------------
import LOG from '#logs';
import MESSAGES from '#messages';

// ------FILE MODULES---------------------------------------------------------
import walletService from './wallet.service.js';
import blockchainService from './blockchain.service.js';
```

**Sub-group separator format:** `// ------{GROUP NAME}---...---` (6 leading dashes, trailing dashes to ~75 chars, no blank line before group label)

**Three import groups (ordered):**
1. `NODE MODULES` — npm packages (`ethers`, `express`, `axios`, `fetch`, `fs`)
2. `PRIVATE MODULES` — `#`-aliased internal modules (`#logs`, `#messages`, `#constants`, `#helpers/...`)
3. `FILE MODULES` — relative path imports (`./wallet.service.js`, `../helpers/vault.helpers.js`)

**Alias usage:** Internal shared modules (`LOG`, `MESSAGES`, `CONSTANTS`) are accessed via `#` path aliases defined in `package.json` imports map:
```js
import LOG from '#logs';
import MESSAGES from '#messages';
import * as CONSTANTS from '#constants';
```

---

## 5. Commenting Style

**Section comments:** Fixed 75-char separator as described above. Used universally.

**Import group separators:** Shorter inline style:
```js
// ------NODE MODULES---------------------------------------------------------
```

**Inline comments:** Sparse and minimal. Used only to clarify non-obvious logic or leave TODOs:
```js
// await operations.addWalletNonce(wallet.address);  ← commented-out code
// TODO
// BOOTSTRAP
```

**LOG-as-tracing:** Rather than prose comments, function entry is traced via `LOG.traceHeader`:
```js
const getWallet = async (address, password) => {
  LOG.traceHeader('getWallet', MODULE_NAME, [address]);
```

**JSDoc:** Present on some public functions, absent on others. Quality is inconsistent (see section 7).

---

## 6. Comment Language

**Primary comment language: English**

All section headers, inline comments, JSDoc, and log messages are written in English. No Spanish comments were detected in the analyzed source files.

---

## 7. Function Documentation Style

JSDoc usage is **occasional and inconsistent**. Some functions have JSDoc blocks; many do not.

**When present, JSDoc follows this minimal style:**
```js
/**
 * Set config params in vault helper
 * @param {JSON} config 
 */
const init = (config) => { ... }
```

```js
/**
 * Store contract data to generate instances
 * @param {*} abi 
 * @param {*} bytecode 
 * @param {*} contractName 
 * @returns 
 */
const addContract = async (abi, bytecode, deployed_bytecode, contractName) => { ... }
```

**Observations:**
- `@param {*}` is used frequently (type not specified), indicating documentation is added for presence rather than precision.
- `@returns` is often left empty.
- Many public functions in services and controllers have **no JSDoc at all**.
- `log.standard.js` has the most detailed JSDoc in the codebase.

**Classification:** Occasional — not systematic. Present in ~40% of public functions.

---

## 8. Naming Conventions

### Variables
- **camelCase** — universally applied for local variables and parameters:
  ```js
  let mainWallet;
  let encriptedWallet;
  const defaultProvider;
  ```

### Module-level mutable state
- **UPPER_CASE** — for module-level `let` variables acting as singletons:
  ```js
  let VAULT_CLIENT;
  let KEYS_URL;
  let CONFIRMATIONS;
  let GAS_PRICE;
  ```

### Constants (config, fixed values)
- **UPPER_CASE** — for true constants and grouped config:
  ```js
  const DEFAULT_LOGGER_NAME = 'Default';
  const MODULE_NAME = 'wallet.service.js';
  export const AVAILABLE_ALGS = ['HS256', ...];
  export const CREDENTIAL_STATUS = ['Valid', ...];
  ```

### Functions
- **camelCase** — all functions use camelCase, including async arrow functions:
  ```js
  const createRandomWallet = async (...) => { ... }
  const getBlockchainDetail = async (...) => { ... }
  const subscribeEventListener = async (...) => { ... }
  ```

### Classes
- **PascalCase**:
  ```js
  class AppError extends Error { ... }
  class AppResponse { ... }
  ```

### Files
- **dot-separated lowercase with role suffix**: `blockchain.service.js`, `vault.helpers.js`, `operation.route.js`, `operations.blockchain.js`
- Pattern: `{domain}.{role}.js`
- Role tokens: `service`, `controller`, `helpers`, `repository`, `route`, `standard`, `bootstrap`
- No kebab-case or PascalCase observed in filenames

### Injected dependencies
- Prefixed with underscore in `init()` parameters to distinguish from module-level variable:
  ```js
  const init = (_operations) => {
    operations = _operations;
  }
  ```

---

## 9. Error Handling Style

### Guard clauses with custom AppError
The primary error signal is `new MESSAGES.AppError(MESSAGES.STANDARD_MESSAGES.{code})`:
```js
if (Object.keys(networkData).length == 0)
  throw new MESSAGES.AppError(MESSAGES.STANDARD_MESSAGES.contractInvalidData);
```

### Try/catch in service layer
Services wrap async operations in try/catch, log, then re-throw:
```js
try {
  const response = await operations.getBlockchains(offset, limit);
  return camelcase.keysToCamel(response);
} catch (error) {
  LOG.error(error.message)
  throw error
}
```

### Try/catch in controllers
Controllers catch errors and delegate to `presenterController.error(err)`:
```js
try {
  const data = await walletService.createRandomWallet(...);
  const response = new MESSAGES.AppResponse(data, MESSAGES.STANDARD_MESSAGES.okResponse);
  return presenterController.response(response);
} catch (err) {
  LOG.error(`Unexpected error Err: ${err.message}`);
  return presenterController.error(err);
}
```

### Centralized error catalog
All error definitions live in `appCodes.standard.js` as exported named constants. No inline error strings:
```js
export const contractInvalidData = {
  appResponse: { code: 40010, message: 'Invalid contract data' },
  httpResponse: httpCodes.HTTP_400
};
```

### Repository layer errors
Repositories silently swallow the original error and wrap it:
```js
} catch {
  throw new MESSAGES.AppError(MESSAGES.STANDARD_MESSAGES.persistenceDatabaseConnectionError)
}
```

---

## 10. Function Structure Patterns

### Decomposed, single-responsibility functions
Functions are small and focused. Each function does one thing:
```js
const generateContractInstance = (address, abi) => { ... }
const addContractInstance = async (...) => { ... }
const getContractInstance = async (alias) => { ... }
```

### Init / dependency injection pattern
Every service and helper exposes an `init(config, dependencies)` function that assigns module-level variables. This acts as a lightweight IoC container:
```js
const init = (config, _operations) => {
  DEFAULT_WALLET = config.DEFAULT_WALLET;
  operations = _operations;
}
```

### Trace-first function body
Every non-trivial public function begins with `LOG.traceHeader`:
```js
const subscribeEventListener = async (type_name, alias, network, events, wallet) => {
  LOG.traceHeader('subscribeEventListener', MODULE_NAME, [type_name, alias, network, events]);
  ...
}
```

### Controller entry trace
Controllers add a debug log immediately after traceHeader:
```js
const createBlockchain = async (req, presenterController) => {
  LOG.traceHeader('createBlockchain', MODULE_NAME, []);
  LOG.debug(`Entering controller with: ${JSON.stringify(req.body)}`);
  ...
}
```

### Mixed function declaration styles (routes only)
Routes use `function` declarations instead of arrow functions, which is the **only exception** to the arrow function pattern:
```js
async function getBlockchains(req, res, next) {
  return passToHandler(req, res, next, blockchainController.getBlockchains);
}
```

---

## 11. Export Conventions

### Default object export with named references (dominant)
All services, controllers, helpers, and repositories use:
```js
export default {
  init,
  createRandomWallet,
  getWallet,
  synchronizeNonce
}
```

### Named exports for constants
Config/constants files use named exports:
```js
export const AVAILABLE_ALGS = ['HS256', ...];
export const CREDENTIAL_STATUS = ['Valid', ...];
```

No `module.exports` CommonJS-style exports detected in `src/`. Pure ES Modules throughout.

---

## 12. Implicit Design Patterns

| Pattern | Evidence |
|---|---|
| **Service layer** | All business logic lives in `services/` files with `init()` + domain methods |
| **Controller-service separation** | Controllers only delegate to services and format responses via `presenterController` |
| **Repository pattern** | `repositories/` abstracts `persistence/` operations; services call repositories, not persistence directly |
| **Presenter / adapter pattern** | `presenter.controller.js` formats all HTTP responses from `AppResponse`/`AppError` to `{ httpStatus, headers, response }` |
| **Dependency injection via init()** | Services and helpers do not import each other freely — dependencies are injected through `init()` calls at boot time in `main.js` |
| **Centralized error catalog** | `appCodes.standard.js` defines all error and success codes. No inline error message strings in business logic |
| **Module singleton pattern** | Module-level `let` variables act as singletons, initialized once via `init()` |
| **Bootstrap orchestration** | `main.js` wires all services in the correct order; `bootstrap/` files encapsulate initialization steps |

---

## 13. Strong Conventions

- **File header:** Every file starts with `//SYBOLID` then `const MODULE_NAME = 'filename.js';`
- **Section separators:** 75-dash `// ---...--- // SECTION NAME // ---...---` format is applied in every file
- **Three import groups:** `NODE MODULES` → `PRIVATE MODULES` → `FILE MODULES` with inline separator labels
- **Default object export:** All modules export `export default { fn1, fn2, ... }`
- **MESSAGES.AppError pattern:** All errors thrown using `new MESSAGES.AppError(MESSAGES.STANDARD_MESSAGES.{key})`
- **Module-level singletons:** Injected dependencies stored as module-level `let` variables, set via `init()`
- **LOG.traceHeader at function entry:** Every non-trivial public function opens with `LOG.traceHeader('fnName', MODULE_NAME, [params])`
- **camelCase for functions and variables**
- **UPPER_CASE for module-level state and constants**
- **dot-separated lowercase filenames** with role suffix (`.service.js`, `.helpers.js`, `.controller.js`)

---

## 14. Probable Conventions

- **JSDoc on public functions** — Present in most `helpers/` and `standard/` files, sporadic in `services/` and absent in some controllers
- **Underscore prefix for `init()` parameters** — `_operations`, `_config`, `_blockchainService` — observed in most but not all `init()` functions
- **Guard clause before main logic** — checking empty objects or null/undefined before proceeding, using `Object.keys(x).length == 0`
- **`LOG.debug(`Entering controller with: ...`)` in controllers** — present in most controllers  
- **`#` alias imports for shared modules** — used for `LOG`, `MESSAGES`, and `CONSTANTS` but not always for file-local helpers

---

## 15. Occasional Patterns

- **Full JSDoc with typed params** — Only in `log.standard.js` and a few helpers; not the default
- **`async function` declarations** — Only in `operation.route.js` route handlers; everywhere else uses arrow functions
- **`try { ... } catch (err) { throw new MESSAGES.AppError(...) }` in repositories** — silently swallows the original error without logging
- **`LOG.step(...)` for bootstrap phase logging** — appears only in `main.js` and bootstrap helpers
- **Commented-out code** — occasional `//` commented code blocks left in files (e.g., middleware lines in `api.js`)

---

## 16. Style Adherence Prompt

Use the following prompt when generating new code for this repository:

---

```
You are generating JavaScript (ES Module) code for the blockchainManager service.
Follow every rule below exactly.

## File Header
Every file must begin with:
  //SYBOLID
  const MODULE_NAME = 'your-file-name.js';

## File Section Structure
Organize every file using this exact section structure and separator style:

  // ---------------------------------------------------------------------------
  // IMPORTS
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // CONSTANTS
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // PRIVATE FUNCTIONS
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // PUBLIC FUNCTIONS
  // ---------------------------------------------------------------------------

  // ---------------------------------------------------------------------------
  // EXPORTS
  // ---------------------------------------------------------------------------

Separators are exactly 75 dashes. Section names are UPPERCASE.

## Import Organization
Split all imports into exactly three labeled sub-groups, in this order:

  // ------NODE MODULES---------------------------------------------------------
  import express from 'express';

  // ------PRIVATE MODULES------------------------------------------------------
  import LOG from '#logs';
  import MESSAGES from '#messages';

  // ------FILE MODULES---------------------------------------------------------
  import walletService from './wallet.service.js';

## Naming
- Variables and function parameters: camelCase
- Module-level mutable state (let): UPPER_CASE
- Constants and exported config values: UPPER_CASE
- Functions: camelCase arrow functions (const fn = async () => {})
- Classes: PascalCase
- Files: dot-separated lowercase with role suffix (e.g., payment.service.js, jwt.helpers.js)

## Init / Dependency Injection Pattern
Every service or helper must expose an `init()` function that receives config and
dependencies and assigns them to module-level let variables:

  let operations;
  const init = (_operations) => {
    operations = _operations;
  }

Parameters injected via init() use an underscore prefix to distinguish from the module variable.

## Tracing Pattern
Every non-trivial public function must start with:
  LOG.traceHeader('functionName', MODULE_NAME, [relevantParams]);

Controllers must also add immediately after:
  LOG.debug(`Entering controller with: ${JSON.stringify(req.body)}`);

## Error Handling
- Throw errors using: throw new MESSAGES.AppError(MESSAGES.STANDARD_MESSAGES.{key})
- Never use inline error strings. All error/success codes are centralized in appCodes.standard.js.
- In services: wrap async operations in try/catch, log with LOG.error(error.message), then re-throw.
- In controllers: catch errors and return presenterController.error(err).
- Guard clauses: check for invalid state immediately at the top of the function before main logic.

## Exports
Always use a default object export listing named function references:
  export default {
    init,
    functionA,
    functionB
  }

Use named exports only for constants files:
  export const MY_CONSTANT = [...];

## Response Shaping
Use MESSAGES.AppResponse to wrap successful data:
  const response = new MESSAGES.AppResponse(data, MESSAGES.STANDARD_MESSAGES.okResponse);
  return presenterController.response(response);

## Comments
- Write all comments in English.
- Inline comments should be minimal and only explain non-obvious logic.
- JSDoc is optional but if present, use @param and @returns with types where known.
- Do not add unnecessary comments; the trace logger covers function entry documentation.
```
