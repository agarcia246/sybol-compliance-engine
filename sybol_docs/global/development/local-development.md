# Local Development Guide

## Purpose

This guide covers running Sybol services locally for development, including environment setup, database configuration, debugging, and hot reload.

---

## Environment Variables

Each service requires environment configuration. Copy and customize `.env.example` files.

### Service-Specific Variables

#### backoffice/

```env
# Server
NODE_ENV=development
PORT=3000

# Database
DATABASE_URL=postgresql://sybol:sybol123@localhost:5432/sybol_dev
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sybol_dev
DB_USER=sybol
DB_PASSWORD=sybol123

# AWS Cognito
AWS_REGION=us-east-1
COGNITO_USER_POOL_ID=us-east-1_xxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxx
COGNITO_DOMAIN=sybol-dev.auth.us-east-1.amazoncognito.com

# JWT
JWT_SECRET=local-dev-secret-change-in-production
JWT_EXPIRATION=24h

# AWS Secrets Manager (optional for local)
USE_SECRETS_MANAGER=false

# Logging
LOG_LEVEL=debug
```

#### businessLogic/

```env
# Server
NODE_ENV=development
PORT=3001

# Database
DATABASE_URL=postgresql://sybol:sybol123@localhost:5432/sybol_dev

# AWS Services
AWS_REGION=us-east-1
KMS_KEY_ID=arn:aws:kms:us-east-1:xxxxx:key/xxxxx

# Service Dependencies
CATALOG_SERVICE_URL=http://localhost:3002
BACKOFFICE_SERVICE_URL=http://localhost:3000

# JWT
JWT_SECRET=local-dev-secret-change-in-production

# Rate Limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100

# Logging
LOG_LEVEL=debug
```

#### catalog/

```env
# Server
NODE_ENV=development
PORT=3002

# Database
DATABASE_URL=postgresql://sybol:sybol123@localhost:5432/sybol_dev

# AWS
AWS_REGION=us-east-1

# JWT
JWT_SECRET=local-dev-secret-change-in-production

# Logging
LOG_LEVEL=debug
```

#### propagate/

```env
# Server
NODE_ENV=development
PORT=3003

# Database
DATABASE_URL=postgresql://sybol:sybol123@localhost:5432/sybol_dev

# AWS SES
AWS_REGION=us-east-1
SES_FROM_EMAIL=noreply@sybol-dev.com
SES_CONFIGURATION_SET=sybol-dev

# AWS SNS
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:xxxxx:sybol-notifications-dev

# Service Dependencies
BUSINESSLOGIC_SERVICE_URL=http://localhost:3001

# JWT
JWT_SECRET=local-dev-secret-change-in-production

# Logging
LOG_LEVEL=debug
```

### Global Environment Setup

Create a `.env` file at the repository root for shared variables:

```env
# AWS Configuration
AWS_PROFILE=sybol-dev
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sybol_dev
DB_USER=sybol
DB_PASSWORD=sybol123

# JWT (shared secret for local dev)
JWT_SECRET=local-dev-secret-change-in-production

# Feature Flags
ENABLE_DEBUG=true
ENABLE_SWAGGER=true
```

---

## Local PostgreSQL Setup

### Option 1: Docker (Recommended)

```bash
# Start PostgreSQL container
docker run --name sybol-postgres \
  -e POSTGRES_USER=sybol \
  -e POSTGRES_PASSWORD=sybol123 \
  -e POSTGRES_DB=sybol_dev \
  -p 5432:5432 \
  -v sybol-pg-data:/var/lib/postgresql/data \
  -d postgres:14

# Verify it's running
docker ps | grep sybol-postgres

# View logs
docker logs sybol-postgres
```

**Persistent Data**: Volume `sybol-pg-data` persists data between container restarts.

**Stop/Start**:
```bash
docker stop sybol-postgres
docker start sybol-postgres
```

**Remove Container**:
```bash
docker stop sybol-postgres
docker rm sybol-postgres
docker volume rm sybol-pg-data
```

### Option 2: Native PostgreSQL

Install PostgreSQL 14+:

**macOS**:
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Create Database**:
```bash
createdb sybol_dev
psql sybol_dev

# In psql:
CREATE USER sybol WITH PASSWORD 'sybol123';
GRANT ALL PRIVILEGES ON DATABASE sybol_dev TO sybol;
```

### Database Migrations

Run migrations from the `database` service:

```bash
cd services/database

# Run all migrations
psql -h localhost -U sybol -d sybol_dev -f migrations/001_initial_schema.sql
psql -h localhost -U sybol -d sybol_dev -f migrations/002_add_credentials.sql
# ... etc
```

### Test Database Connection

```bash
psql -h localhost -U sybol -d sybol_dev -c "SELECT version();"
```

Expected output shows PostgreSQL version.

---

## Running Services

### Single Service

Run one service at a time:

```bash
cd services/backoffice
npm install
npm run dev
```

Expected output:
```
[nodemon] starting `node src/server.js`
Server running on port 3000
Database connected successfully
```

### Multiple Services

Use separate terminal windows/tabs:

**Terminal 1: backoffice**
```bash
cd services/backoffice && npm run dev
```

**Terminal 2: businessLogic**
```bash
cd services/businessLogic && npm run dev
```

**Terminal 3: catalog**
```bash
cd services/catalog && npm run dev
```

**Terminal 4: propagate**
```bash
cd services/propagate && npm run dev
```

### Using Docker Compose (Future Enhancement)

If a `docker-compose.yml` is created:

```bash
# Start all services
docker-compose up

# Start specific services
docker-compose up backoffice businessLogic

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backoffice

# Stop all services
docker-compose down
```

---

## Service Discovery

Services need to know each other's URLs. For local development:

| Service | Local URL |
|---------|-----------|
| backoffice | http://localhost:3000 |
| businessLogic | http://localhost:3001 |
| catalog | http://localhost:3002 |
| propagate | http://localhost:3003 |

Configure these in each service's `.env`:

```env
BACKOFFICE_SERVICE_URL=http://localhost:3000
BUSINESSLOGIC_SERVICE_URL=http://localhost:3001
CATALOG_SERVICE_URL=http://localhost:3002
PROPAGATE_SERVICE_URL=http://localhost:3003
```

---

## Working with AWS Cognito Locally

### Challenge

AWS Cognito requires valid AWS credentials and configuration even for local development.

### Solutions

#### Option 1: Use Dev Environment Cognito

Point local services to the development AWS Cognito pool:

```env
COGNITO_USER_POOL_ID=us-east-1_DevPoolId
COGNITO_CLIENT_ID=DevClientId
COGNITO_REGION=us-east-1
```

**Pros**: Real authentication flow  
**Cons**: Requires AWS access, shares dev pool

#### Option 2: Mock Cognito (Testing Only)

For unit/integration tests, mock Cognito responses:

```javascript
// tests/mocks/cognito.js
jest.mock('@aws-sdk/client-cognito-identity-provider', () => ({
  CognitoIdentityProviderClient: jest.fn(),
  AdminGetUserCommand: jest.fn(),
  // ... other mocked commands
}));
```

#### Option 3: Local JWT Generation

For isolated local development, generate test JWTs:

```bash
# Create test user token
node scripts/generateTestJWT.js
```

Use in requests:
```bash
curl -H "Authorization: Bearer <test-jwt>" http://localhost:3000/api/users
```

**⚠️ Warning**: Never use test JWTs in production.

---

## Hot Reload / Watch Mode

Services use `nodemon` for automatic restart on file changes.

### Start with Hot Reload

```bash
npm run dev
```

### Nodemon Configuration

Default configuration in `package.json`:

```json
{
  "scripts": {
    "dev": "NODE_ENV=development nodemon src/server.js"
  }
}
```

### Custom Nodemon Config

Create `nodemon.json`:

```json
{
  "watch": ["src"],
  "ext": "js,json",
  "ignore": ["tests", "node_modules"],
  "exec": "node src/server.js",
  "env": {
    "NODE_ENV": "development"
  }
}
```

---

## Debugging with VS Code

### Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Backoffice Service",
      "program": "${workspaceFolder}/services/backoffice/src/server.js",
      "cwd": "${workspaceFolder}/services/backoffice",
      "envFile": "${workspaceFolder}/services/backoffice/.env",
      "console": "integratedTerminal",
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "type": "node",
      "request": "launch",
      "name": "Debug BusinessLogic Service",
      "program": "${workspaceFolder}/services/businessLogic/src/server.js",
      "cwd": "${workspaceFolder}/services/businessLogic",
      "envFile": "${workspaceFolder}/services/businessLogic/.env",
      "console": "integratedTerminal",
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "type": "node",
      "request": "attach",
      "name": "Attach to Running Service",
      "port": 9229,
      "restart": true,
      "skipFiles": ["<node_internals>/**"]
    }
  ]
}
```

### Start Debugging

1. Open service file (e.g., `services/backoffice/src/server.js`)
2. Set breakpoints (click left margin)
3. Press `F5` or select debug configuration
4. Service starts in debug mode

### Debug Running Service

Start service with inspect flag:

```bash
node --inspect src/server.js
```

Then attach VS Code debugger using "Attach to Running Service" configuration.

---

## Testing Locally

### Run All Tests

```bash
cd services/backoffice
npm test
```

### Run Specific Test File

```bash
npm test -- tests/controllers/userController.test.js
```

### Watch Mode (Re-run on Changes)

```bash
npm test -- --watch
```

### Coverage Report

```bash
npm run test:coverage
```

View coverage report at `coverage/lcov-report/index.html`.

---

## API Testing

### Using curl

```bash
# Health check
curl http://localhost:3000/health

# Login (get JWT)
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"test123"}'

# Authenticated request
curl http://localhost:3000/api/users \
  -H "Authorization: Bearer <jwt-token>"
```

### Using Postman

Import collection from `services/backoffice/Backoffice_API.postman_collection.json`.

**Setup**:
1. Open Postman
2. File → Import → Select JSON file
3. Configure environment variables:
   - `baseUrl`: `http://localhost:3000`
   - `jwt`: (obtained from login request)

### Using HTTPie

```bash
# Install HTTPie
brew install httpie

# Health check
http GET http://localhost:3000/health

# Login
http POST http://localhost:3000/auth/login username=admin password=test123

# Authenticated request
http GET http://localhost:3000/api/users "Authorization: Bearer <jwt>"
```

---

## Logging

### Log Levels

Services use console logging with levels:

- `error`: Critical issues
- `warn`: Warning messages
- `info`: General information
- `debug`: Detailed debugging (development only)

### Configure Log Level

In `.env`:

```env
LOG_LEVEL=debug
```

### View Logs

Logs appear in the terminal running the service.

### Structured Logging (Future)

Consider adding Winston or Pino for structured logging:

```javascript
const winston = require('winston');
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console()
  ]
});
```

---

## Common Local Development Issues

### Port Already in Use

```bash
# Find process
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Database Connection Refused

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Start if stopped
docker start sybol-postgres

# Check connection
psql -h localhost -U sybol -d sybol_dev
```

### Module Not Found Errors

```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### AWS Credential Errors

```bash
# Verify credentials
aws sts get-caller-identity

# Reconfigure
aws configure --profile sybol-dev

# Use profile
export AWS_PROFILE=sybol-dev
```

### CORS Errors (Frontend Development)

Configure CORS in service:

```javascript
// src/middleware/cors.js
const cors = require('cors');

app.use(cors({
  origin: 'http://localhost:3000', // Frontend URL
  credentials: true
}));
```

---

## Performance Tips

### Reduce Startup Time

- Use `npm ci` instead of `npm install` (faster, uses package-lock.json)
- Cache `node_modules` in Docker builds

### Optimize Hot Reload

- Configure nodemon to watch only necessary folders
- Exclude `node_modules`, `tests`, and build artifacts

### Database Connection Pooling

Configure pg pool:

```javascript
const { Pool } = require('pg');
const pool = new Pool({
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

---

## Next Steps

- **Code Standards**: Review [Coding Standards](coding-standards.md)
- **Testing**: Follow [Testing Strategy](testing-strategy.md)
- **Contributing**: Read [Contributing Guidelines](contributing.md)
- **API Documentation**: See [API Documentation](../api/README.md)

---

## Quick Reference

```bash
# Start PostgreSQL
docker start sybol-postgres

# Run service with hot reload
cd services/<service-name> && npm run dev

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Debug mode
node --inspect src/server.js

# Check health
curl http://localhost:<port>/health

# View database
psql -h localhost -U sybol -d sybol_dev
```
