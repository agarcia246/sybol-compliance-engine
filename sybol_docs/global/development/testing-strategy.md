# Testing Strategy

## Purpose

This document defines the testing approach, tools, patterns, and practices for Sybol development.

## Testing Philosophy

Good tests are:
- **Fast** - Run quickly to enable rapid feedback
- **Isolated** - Independent of other tests
- **Repeatable** - Produce consistent results
- **Self-validating** - Pass or fail clearly
- **Timely** - Written alongside code

---

## Testing Pyramid

Sybol follows the testing pyramid approach:

```
         /\
        /  \
       / E2E \           Few (5%)
      /______\
     /        \
    /Integration\        Medium (25%)
   /____________\
  /              \
 /  Unit Tests    \      Many (70%)
/__________________\
```

### Unit Tests (70%)

**Focus**: Individual functions and modules in isolation.

**Characteristics**:
- Fast execution (milliseconds)
- No external dependencies (database, APIs)
- Mock/stub external calls
- High coverage

**Example**:
```javascript
// tests/unit/utils/validators.test.js
const { validateEmail } = require('../../../src/utils/validators');

describe('validateEmail', () => {
  test('should return true for valid email', () => {
    expect(validateEmail('user@example.com')).toBe(true);
  });

  test('should return false for invalid email', () => {
    expect(validateEmail('invalid-email')).toBe(false);
  });
});
```

### Integration Tests (25%)

**Focus**: Interaction between components, database, and AWS services.

**Characteristics**:
- Slower than unit tests (seconds)
- Uses test database
- Mocks external APIs (AWS, third-party)
- Validates component integration

**Example**:
```javascript
// tests/integration/controllers/userController.test.js
const request = require('supertest');
const app = require('../../../src/app');
const { pool } = require('../../../src/config/database');

describe('User Controller', () => {
  beforeAll(async () => {
    // Setup test database
    await pool.query('BEGIN');
  });

  afterAll(async () => {
    // Cleanup
    await pool.query('ROLLBACK');
    await pool.end();
  });

  test('POST /users should create user', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', name: 'Test User' })
      .expect(201);

    expect(response.body.data).toHaveProperty('id');
    expect(response.body.data.email).toBe('test@example.com');
  });
});
```

### End-to-End Tests (5%)

**Focus**: Complete user workflows across services.

**Characteristics**:
- Slowest (minutes)
- Tests real system behavior
- Runs against staging environment
- Critical paths only

**Example**:
```javascript
// tests/e2e/credentialIssuance.test.js
describe('Credential Issuance Flow', () => {
  test('should issue credential from request', async () => {
    // 1. User creates credential request
    const request = await createCredentialRequest(userId, schemaId);
    
    // 2. Admin reviews and approves
    await approveCredentialRequest(request.id);
    
    // 3. Credential is issued
    const credential = await getIssuedCredential(request.id);
    
    // 4. User receives credential
    const userCredentials = await getUserCredentials(userId);
    expect(userCredentials).toContainEqual(
      expect.objectContaining({ id: credential.id })
    );
  });
});
```

---

## Testing Tools

### Jest

**Purpose**: Test framework and test runner.

**Installation**:
```bash
npm install --save-dev jest
```

**Configuration**: `jest.config.js`

```javascript
module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/server.js',
    '!src/lambda.js'
  ],
  testMatch: [
    '**/tests/**/*.test.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js']
};
```

### Supertest

**Purpose**: HTTP assertion library for testing Express APIs.

**Installation**:
```bash
npm install --save-dev supertest
```

**Usage**:
```javascript
const request = require('supertest');
const app = require('../src/app');

test('GET /health returns 200', async () => {
  const response = await request(app)
    .get('/health')
    .expect(200);
  
  expect(response.body).toEqual({ status: 'ok' });
});
```

### Jest Mocks

**Purpose**: Mock external dependencies.

**AWS SDK Mocking**:
```javascript
// tests/mocks/aws.js
jest.mock('@aws-sdk/client-cognito-identity-provider', () => ({
  CognitoIdentityProviderClient: jest.fn(() => ({
    send: jest.fn()
  })),
  AdminGetUserCommand: jest.fn()
}));
```

---

## Test Structure and Organization

### Directory Layout

```
service/
├── src/
│   └── ... (source code)
├── tests/
│   ├── unit/               # Unit tests
│   │   ├── controllers/
│   │   ├── services/
│   │   └── utils/
│   ├── integration/        # Integration tests
│   │   ├── controllers/
│   │   └── repositories/
│   ├── e2e/                # End-to-end tests
│   ├── mocks/              # Shared mocks
│   ├── fixtures/           # Test data
│   └── setup.js            # Test setup/teardown
└── jest.config.js
```

### Test File Naming

Pattern: `<sourceFile>.test.js`

Examples:
- `src/controllers/userController.js` → `tests/unit/controllers/userController.test.js`
- `src/utils/validators.js` → `tests/unit/utils/validators.test.js`

### Test Structure (AAA Pattern)

**Arrange - Act - Assert**:

```javascript
describe('UserService', () => {
  describe('createUser', () => {
    test('should create user with valid data', async () => {
      // Arrange
      const userData = {
        email: 'test@example.com',
        name: 'Test User'
      };
      const mockRepository = {
        create: jest.fn().mockResolvedValue({ id: '123', ...userData })
      };

      // Act
      const result = await userService.createUser(userData, mockRepository);

      // Assert
      expect(result).toHaveProperty('id');
      expect(result.email).toBe(userData.email);
      expect(mockRepository.create).toHaveBeenCalledWith(userData);
    });
  });
});
```

---

## Mocking AWS Services

### Strategy

Mock AWS SDK calls to avoid:
- AWS costs during testing
- Dependency on AWS availability
- Slow test execution

### Example: Mocking KMS

```javascript
// tests/mocks/kms.js
const { KMSClient, SignCommand } = require('@aws-sdk/client-kms');

jest.mock('@aws-sdk/client-kms');

const mockKMSClient = {
  send: jest.fn()
};

KMSClient.mockImplementation(() => mockKMSClient);

beforeEach(() => {
  mockKMSClient.send.mockClear();
});

module.exports = { mockKMSClient };
```

**Usage in Tests**:
```javascript
const { mockKMSClient } = require('../../mocks/kms');

test('should sign data with KMS', async () => {
  mockKMSClient.send.mockResolvedValue({
    Signature: Buffer.from('mock-signature')
  });

  const signature = await signWithKMS(data);
  
  expect(signature).toBeTruthy();
  expect(mockKMSClient.send).toHaveBeenCalledWith(
    expect.any(SignCommand)
  );
});
```

### Example: Mocking Secrets Manager

```javascript
jest.mock('@aws-sdk/client-secrets-manager', () => ({
  SecretsManagerClient: jest.fn(() => ({
    send: jest.fn().mockResolvedValue({
      SecretString: JSON.stringify({ dbPassword: 'test-password' })
    })
  })),
  GetSecretValueCommand: jest.fn()
}));
```

---

## Database Testing

### Test Database Setup

Use separate test database:

```env
# .env.test
DATABASE_URL=postgresql://sybol:sybol123@localhost:5432/sybol_test
```

### Transaction Rollback Pattern

Wrap tests in transactions and rollback:

```javascript
// tests/setup.js
const { pool } = require('../src/config/database');

beforeEach(async () => {
  await pool.query('BEGIN');
});

afterEach(async () => {
  await pool.query('ROLLBACK');
});

afterAll(async () => {
  await pool.end();
});
```

### Test Fixtures

Create reusable test data:

```javascript
// tests/fixtures/users.js
module.exports = {
  validUser: {
    email: 'test@example.com',
    name: 'Test User',
    role: 'user'
  },
  adminUser: {
    email: 'admin@example.com',
    name: 'Admin User',
    role: 'admin'
  }
};
```

**Usage**:
```javascript
const { validUser } = require('../fixtures/users');

test('should create user', async () => {
  const user = await userService.createUser(validUser);
  expect(user.email).toBe(validUser.email);
});
```

---

## Test Coverage

### Coverage Goals

| Metric | Target | Critical |
|--------|--------|----------|
| Statements | 80% | 90% |
| Branches | 80% | 85% |
| Functions | 80% | 90% |
| Lines | 80% | 90% |

### Generate Coverage Report

```bash
# Run tests with coverage
npm run test:coverage

# View HTML report
open coverage/lcov-report/index.html
```

### Coverage Configuration

In `jest.config.js`:

```javascript
module.exports = {
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/server.js',      // Exclude entry points
    '!src/lambda.js',
    '!src/config/**'        // Exclude configuration
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './src/controllers/': {
      branches: 90,
      functions: 95
    }
  }
};
```

### Identify Uncovered Code

```bash
# Show uncovered lines
npm run test:coverage -- --verbose

# Coverage summary
npm run test:coverage -- --coverageReporters=text-summary
```

---

## Running Tests

### Run All Tests

```bash
npm test
```

### Run Specific Test File

```bash
npm test -- tests/unit/utils/validators.test.js
```

### Run Tests Matching Pattern

```bash
# Run all user-related tests
npm test -- --testNamePattern=user

# Run integration tests only
npm test -- tests/integration
```

### Watch Mode (Re-run on Changes)

```bash
npm test -- --watch
```

### Debug Tests in VS Code

`.vscode/launch.json`:

```json
{
  "type": "node",
  "request": "launch",
  "name": "Jest Debug",
  "program": "${workspaceFolder}/node_modules/.bin/jest",
  "args": [
    "--runInBand",
    "--no-cache",
    "${file}"
  ],
  "console": "integratedTerminal",
  "internalConsoleOptions": "neverOpen"
}
```

---

## CI Test Automation

### GitHub Actions Workflow

`.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: sybol
          POSTGRES_PASSWORD: sybol123
          POSTGRES_DB: sybol_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linter
        run: npm run lint
      
      - name: Run tests
        run: npm run test:coverage
        env:
          DATABASE_URL: postgresql://sybol:sybol123@localhost:5432/sybol_test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

---

## Best Practices

### Test Independence

Each test should be isolated:

```javascript
// Bad - Tests depend on execution order
test('create user', async () => {
  user = await createUser(data); // Sets global variable
});

test('get user', async () => {
  const fetched = await getUser(user.id); // Depends on previous test
});

// Good - Tests are independent
test('create user', async () => {
  const user = await createUser(data);
  expect(user).toHaveProperty('id');
});

test('get user', async () => {
  const user = await createUser(data);
  const fetched = await getUser(user.id);
  expect(fetched.id).toBe(user.id);
});
```

### Descriptive Test Names

```javascript
// Bad
test('user test', () => { });

// Good
test('should return 404 when user does not exist', () => { });
test('should hash password before saving user', () => { });
```

### One Assertion Per Test (When Possible)

```javascript
// Prefer
test('should return user with id', () => {
  expect(user).toHaveProperty('id');
});

test('should return user with correct email', () => {
  expect(user.email).toBe('test@example.com');
});

// Over
test('should return user', () => {
  expect(user).toHaveProperty('id');
  expect(user.email).toBe('test@example.com');
  expect(user.name).toBe('Test User');
});
```

### Test Error Handling

```javascript
test('should throw error for invalid email', async () => {
  await expect(createUser({ email: 'invalid' }))
    .rejects
    .toThrow('Invalid email format');
});
```

### Avoid Testing Implementation Details

```javascript
// Bad - Tests internal implementation
test('should call repository.save', async () => {
  const spy = jest.spyOn(repository, 'save');
  await userService.createUser(data);
  expect(spy).toHaveBeenCalled();
});

// Good - Tests behavior
test('should persist user to database', async () => {
  const user = await userService.createUser(data);
  const saved = await userRepository.findById(user.id);
  expect(saved).toEqual(user);
});
```

---

## Common Testing Patterns

### Testing Async Functions

```javascript
test('should return user', async () => {
  const user = await getUser('123');
  expect(user.id).toBe('123');
});
```

### Testing Promises

```javascript
test('should reject invalid data', () => {
  return expect(createUser({ invalid: 'data' }))
    .rejects
    .toThrow('Validation failed');
});
```

### Testing Callbacks (Legacy)

```javascript
test('should call callback with result', (done) => {
  processData((error, result) => {
    expect(error).toBeNull();
    expect(result).toBeTruthy();
    done();
  });
});
```

### Snapshot Testing

```javascript
test('should match credential structure', () => {
  const credential = createCredential(data);
  expect(credential).toMatchSnapshot();
});
```

---

## Troubleshooting Tests

### Tests Fail Intermittently

- Check for race conditions
- Ensure proper cleanup in `afterEach`
- Verify test independence

### Tests Run Slowly

- Mock external dependencies
- Use transaction rollback for database tests
- Review test setup/teardown

### Coverage Not Updating

```bash
# Clear Jest cache
npm test -- --clearCache

# Remove coverage directory
rm -rf coverage
```

---

## See Also

- [Coding Standards](coding-standards.md) - Code quality
- [Contributing](contributing.md) - PR requirements
- [Local Development](local-development.md) - Development setup

---

## Quick Reference

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm test -- --watch

# Run specific file
npm test -- path/to/test.test.js

# Run matching pattern
npm test -- --testNamePattern="user"

# Debug mode
node --inspect-brk node_modules/.bin/jest --runInBand

# Clear cache
npm test -- --clearCache
```
