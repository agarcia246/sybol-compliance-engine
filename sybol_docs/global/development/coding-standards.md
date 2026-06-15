# Coding Standards

## Purpose

This document defines code quality standards, conventions, and best practices for Sybol development.

All code must be:
- Readable
- Maintainable
- Testable
- Secure
- Consistent

---

## JavaScript / Node.js Style Guide

### General Principles

1. **Clarity over Cleverness**: Write code that is easy to understand
2. **Consistency**: Follow established patterns in the codebase
3. **Simplicity**: Prefer simple solutions over complex ones
4. **DRY**: Don't Repeat Yourself - extract common logic

### Code Formatting

#### Indentation

Use **2 spaces** for indentation (not tabs).

```javascript
// Correct
function calculateTotal(items) {
  return items.reduce((sum, item) => {
    return sum + item.price;
  }, 0);
}

// Incorrect
function calculateTotal(items) {
    return items.reduce((sum, item) => {
        return sum + item.price;
    }, 0);
}
```

#### Line Length

Maximum **100 characters** per line.

```javascript
// Correct
const credentialRequest = await businessLogicService
  .createCredentialRequest(userId, schemaId, data);

// Avoid
const credentialRequest = await businessLogicService.createCredentialRequest(userId, schemaId, data);
```

#### Semicolons

**Always use semicolons**.

```javascript
// Correct
const user = await getUser(id);
return user;

// Incorrect
const user = await getUser(id)
return user
```

#### Quotes

Use **single quotes** for strings.

```javascript
// Correct
const message = 'User created successfully';

// Incorrect
const message = "User created successfully";
```

**Exception**: Use backticks for template literals.

```javascript
const greeting = `Hello, ${user.name}!`;
```

---

## ESLint Configuration

All services use ESLint for code quality enforcement.

### Standard Configuration

`.eslintrc.json`:

```json
{
  "env": {
    "node": true,
    "es2021": true,
    "jest": true
  },
  "extends": ["eslint:recommended"],
  "parserOptions": {
    "ecmaVersion": 12
  },
  "rules": {
    "semi": ["error", "always"],
    "quotes": ["error", "single"],
    "no-unused-vars": "warn",
    "no-console": "off",
    "indent": ["error", 2],
    "linebreak-style": ["error", "unix"],
    "comma-dangle": ["error", "never"],
    "arrow-spacing": ["error", { "before": true, "after": true }],
    "no-var": "error",
    "prefer-const": "error"
  }
}
```

### Run Linting

```bash
# Lint all files
npm run lint

# Lint specific file
npx eslint src/controllers/userController.js

# Auto-fix issues
npx eslint --fix src/
```

### Pre-commit Hooks

Consider adding Husky for automatic linting:

```bash
npm install --save-dev husky lint-staged
```

`.husky/pre-commit`:
```bash
#!/bin/sh
npm run lint
```

---

## Naming Conventions

### Files

| Type | Convention | Example |
|------|------------|---------|
| Routes | camelCase + descriptive | `userRoutes.js` |
| Controllers | camelCase + Controller suffix | `userController.js` |
| Models | PascalCase | `User.js`, `Credential.js` |
| Utilities | camelCase + descriptive | `jwtUtils.js`, `validators.js` |
| Tests | Same as target + `.test.js` | `userController.test.js` |
| Configuration | lowercase | `database.js`, `auth.js` |

### Variables

**Use camelCase**:

```javascript
// Correct
const userId = req.params.id;
const credentialRequest = await getCredentialRequest(id);

// Incorrect
const user_id = req.params.id;
const CredentialRequest = await getCredentialRequest(id);
```

**Use descriptive names**:

```javascript
// Correct
const authenticatedUser = await authenticate(token);
const activeCredentials = credentials.filter(c => c.status === 'active');

// Avoid
const u = await authenticate(token);
const creds = credentials.filter(c => c.status === 'active');
```

**Constants in UPPER_SNAKE_CASE**:

```javascript
const MAX_RETRY_ATTEMPTS = 3;
const DEFAULT_PAGE_SIZE = 20;
const TOKEN_EXPIRATION_HOURS = 24;
```

### Functions

**Use camelCase and verb prefixes**:

```javascript
// Correct
function getUserById(id) { }
function createCredential(data) { }
function validateSchema(schema) { }
function isExpired(credential) { }
function hasPermission(user, action) { }

// Incorrect
function user(id) { }
function credential(data) { }
function schema(schema) { }
```

**Naming by Purpose**:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `get` | Retrieve data | `getUser()`, `getCredentials()` |
| `create` | Create new resource | `createCredential()` |
| `update` | Modify existing | `updateUser()` |
| `delete` | Remove resource | `deleteCredential()` |
| `validate` | Validation | `validateInput()` |
| `is` / `has` | Boolean checks | `isValid()`, `hasPermission()` |
| `handle` | Event handlers | `handleError()`, `handleRequest()` |

### Classes

**Use PascalCase**:

```javascript
class CredentialService { }
class UserRepository { }
class JWTValidator { }
```

---

## Code Organization

### Project Structure

```
service/
├── src/
│   ├── routes/         # Express route definitions
│   ├── controllers/    # Request handlers & business logic
│   ├── models/         # Data models
│   ├── services/       # Business logic services
│   ├── repositories/   # Data access layer
│   ├── middleware/     # Express middleware
│   ├── utils/          # Helper functions
│   ├── config/         # Configuration
│   └── validators/     # Input validation
```

### Layer Responsibilities

#### Routes

Define API endpoints and map to controllers:

```javascript
// routes/userRoutes.js
const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
const auth = require('../middleware/auth');

router.get('/', auth.authenticate, userController.getAllUsers);
router.post('/', auth.authenticate, userController.createUser);

module.exports = router;
```

#### Controllers

Handle HTTP requests and responses:

```javascript
// controllers/userController.js
const userService = require('../services/userService');

async function getAllUsers(req, res, next) {
  try {
    const users = await userService.getAllUsers();
    res.json({ success: true, data: users });
  } catch (error) {
    next(error);
  }
}

module.exports = { getAllUsers };
```

#### Services

Encapsulate business logic:

```javascript
// services/userService.js
const userRepository = require('../repositories/userRepository');

async function getAllUsers() {
  return await userRepository.findAll();
}

module.exports = { getAllUsers };
```

#### Repositories

Handle data persistence:

```javascript
// repositories/userRepository.js
const { pool } = require('../config/database');

async function findAll() {
  const result = await pool.query('SELECT * FROM users');
  return result.rows;
}

module.exports = { findAll };
```

---

## Error Handling

### Always Use Try-Catch

Wrap async operations in try-catch:

```javascript
async function getUser(id) {
  try {
    const user = await userRepository.findById(id);
    if (!user) {
      throw new Error('User not found');
    }
    return user;
  } catch (error) {
    logger.error('Error fetching user:', error);
    throw error;
  }
}
```

### Custom Error Classes

Create specific error types:

```javascript
// utils/errors.js
class NotFoundError extends Error {
  constructor(message) {
    super(message);
    this.name = 'NotFoundError';
    this.statusCode = 404;
  }
}

class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
    this.statusCode = 400;
  }
}

module.exports = { NotFoundError, ValidationError };
```

Usage:

```javascript
const { NotFoundError } = require('../utils/errors');

async function getUserById(id) {
  const user = await userRepository.findById(id);
  if (!user) {
    throw new NotFoundError(`User with id ${id} not found`);
  }
  return user;
}
```

### Centralized Error Handler

Express middleware:

```javascript
// middleware/errorHandler.js
function errorHandler(err, req, res, next) {
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  logger.error({
    error: err.name,
    message: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method
  });

  res.status(statusCode).json({
    success: false,
    error: {
      message,
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    }
  });
}

module.exports = errorHandler;
```

---

## Async/Await Best Practices

### Prefer Async/Await over Promises

```javascript
// Correct
async function processCredential(id) {
  const credential = await getCredential(id);
  const validated = await validateCredential(credential);
  return await saveCredential(validated);
}

// Avoid
function processCredential(id) {
  return getCredential(id)
    .then(credential => validateCredential(credential))
    .then(validated => saveCredential(validated));
}
```

### Always Await Promises

```javascript
// Correct
const user = await getUserById(id);

// Incorrect (floating promise)
getUserById(id); // Result is lost
```

### Parallel Operations

Use `Promise.all` for independent operations:

```javascript
// Sequential (slower)
const user = await getUser(userId);
const organization = await getOrganization(orgId);
const credentials = await getCredentials(userId);

// Parallel (faster)
const [user, organization, credentials] = await Promise.all([
  getUser(userId),
  getOrganization(orgId),
  getCredentials(userId)
]);
```

### Handle Promise Rejections

```javascript
// Correct
try {
  const result = await riskyOperation();
} catch (error) {
  logger.error('Operation failed:', error);
  throw error;
}

// Incorrect (unhandled rejection)
const result = await riskyOperation(); // No error handling
```

---

## Comments and Documentation

### When to Comment

**Comment WHY, not WHAT**:

```javascript
// Correct
// Use exponential backoff to avoid overwhelming the external API
const delay = Math.pow(2, attempt) * 1000;

// Incorrect
// Set delay variable
const delay = Math.pow(2, attempt) * 1000;
```

### JSDoc for Functions

Document public functions:

```javascript
/**
 * Creates a new verifiable credential
 * @param {string} userId - The ID of the credential holder
 * @param {string} schemaId - The credential schema ID
 * @param {Object} claimData - The credential claims/data
 * @returns {Promise<Object>} The created credential
 * @throws {ValidationError} If schema or data is invalid
 */
async function createCredential(userId, schemaId, claimData) {
  // Implementation
}
```

### TODO Comments

Use standardized format:

```javascript
// TODO: Implement credential revocation check
// FIXME: Race condition when multiple requests arrive simultaneously
// HACK: Temporary workaround until AWS SDK v4 is released
```

### README per Service

Each service should have a README.md explaining:
- Purpose
- API endpoints
- Environment variables
- Running instructions
- Testing

---

## Security Practices

### Never Hardcode Secrets

```javascript
// Incorrect
const apiKey = 'sk-1234567890abcdef';
const dbPassword = 'mypassword123';

// Correct
const apiKey = process.env.API_KEY;
const dbPassword = process.env.DB_PASSWORD;
```

### Input Validation

**Always validate user input**:

```javascript
const Joi = require('joi');

const createUserSchema = Joi.object({
  email: Joi.string().email().required(),
  name: Joi.string().min(2).max(100).required(),
  role: Joi.string().valid('admin', 'user', 'viewer').required()
});

function validateCreateUser(data) {
  const { error, value } = createUserSchema.validate(data);
  if (error) {
    throw new ValidationError(error.details[0].message);
  }
  return value;
}
```

### SQL Injection Prevention

**Use parameterized queries**:

```javascript
// Correct
const result = await pool.query(
  'SELECT * FROM users WHERE email = $1',
  [email]
);

// Incorrect (SQL injection risk)
const result = await pool.query(
  `SELECT * FROM users WHERE email = '${email}'`
);
```

### Authentication Checks

Always verify JWT tokens:

```javascript
// middleware/auth.js
const jwt = require('jsonwebtoken');

function authenticate(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

### Sensitive Data Logging

**Never log sensitive information**:

```javascript
// Incorrect
logger.info('User logged in:', { email, password });

// Correct
logger.info('User logged in:', { email });
```

---

## Code Review Checklist

Before submitting code for review:

- [ ] Code follows naming conventions
- [ ] ESLint passes without errors
- [ ] Tests written and passing
- [ ] Error handling implemented
- [ ] Input validation added
- [ ] No hardcoded secrets
- [ ] Logging added for important operations
- [ ] Comments explain complex logic
- [ ] README updated if needed
- [ ] No debugging code (console.log) left

---

## Anti-Patterns to Avoid

### Callback Hell

```javascript
// Avoid
getData(function(data) {
  processData(data, function(result) {
    saveData(result, function(saved) {
      // Deep nesting
    });
  });
});

// Use async/await
const data = await getData();
const result = await processData(data);
await saveData(result);
```

### God Objects

Avoid massive classes/modules doing too much. Split into smaller, focused modules.

### Magic Numbers

```javascript
// Avoid
if (user.loginAttempts > 5) { }

// Use named constants
const MAX_LOGIN_ATTEMPTS = 5;
if (user.loginAttempts > MAX_LOGIN_ATTEMPTS) { }
```

### Long Functions

Keep functions short and focused. If a function exceeds ~50 lines, consider splitting it.

---

## See Also

- [Testing Strategy](testing-strategy.md) - Test patterns
- [Contributing](contributing.md) - Code review process
- [Local Development](local-development.md) - Development setup
