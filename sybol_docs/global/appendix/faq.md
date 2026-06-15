# Frequently Asked Questions (FAQ)

## Purpose

This document answers common questions about the Sybol platform, covering architecture decisions, deployment procedures, authentication, troubleshooting, multi-tenancy, development workflows, and cost optimization.

---

## Architecture Questions

### Why did Sybol choose a serverless architecture?

Sybol uses AWS Lambda and API Gateway for several strategic reasons:

- **Cost Efficiency**: Pay-per-execution pricing eliminates idle costs during low-usage periods
- **Auto-Scaling**: Lambda automatically scales from 0 to thousands of concurrent executions
- **Operational Simplicity**: No servers to maintain, patch, or monitor for a small engineering team
- **Multi-Tenant Efficiency**: Natural isolation between tenant requests with independent invocations
- **Fast Deployment**: Updates deploy in seconds without infrastructure management

For detailed analysis, see [ADR-0002: Serverless Architecture](../decisions/0002-serverless-architecture.md).

### Why use database-per-tenant instead of shared database?

Database-per-tenant provides maximum isolation:

- **Data Isolation**: Complete physical separation of tenant data
- **Security Compliance**: Meets strict regulatory requirements (eIDAS 2.0, GDPR)
- **Independent Scaling**: Each tenant database scales independently
- **Blast Radius Containment**: Issues in one tenant never affect others
- **Custom Schema Evolution**: Tenants can have different schema versions during migrations

Trade-offs include higher operational complexity and per-tenant costs, but the security and compliance benefits outweigh concerns for credential infrastructure.

See [Multi-Tenancy Architecture](../architecture/multi-tenancy.md) for details.

### Why PostgreSQL instead of NoSQL databases?

PostgreSQL was chosen for:

- **ACID Transactions**: Critical for credential state management (issued → revoked)
- **Rich Query Capabilities**: Complex joins for credential relationships and presentations
- **JSON Support**: Native JSONB for flexible credential schemas
- **Mature Ecosystem**: Well-understood by engineering team
- **Aurora Serverless**: Auto-scaling capability with relational guarantees

Credential systems require strong consistency and transactional integrity, which PostgreSQL provides better than eventual-consistency NoSQL solutions.

### Why not use AWS ECS or Kubernetes instead of Lambda?

Lambda was selected over container orchestration platforms because:

- **Team Size**: Small team (3-5 developers) lacks dedicated DevOps resources
- **Cost Profile**: Always-on ECS costs ($135+/month) vs. Lambda pay-per-use ($20-60/month)
- **Operational Overhead**: ECS/Kubernetes require significant management, Lambda is fully managed
- **Usage Pattern**: Credential operations are request-driven, not long-running processes

For teams with DevOps expertise or long-running workload requirements, ECS Fargate would be appropriate. See [ADR-0002](../decisions/0002-serverless-architecture.md).

### What is the purpose of each microservice?

| Service | Responsibility |
|---------|----------------|
| **backoffice** | Platform administration, user management, tenant onboarding, KYB verification |
| **businessLogic** | Verifiable credential lifecycle (issuance, presentation, verification) |
| **catalog** | Credential templates, schemas, claim definitions |
| **propagate** | Cross-tenant event propagation, credential delivery notifications |

This separation ensures clear boundaries, independent scaling, and security isolation.

---

## Deployment Questions

### How do I deploy the core infrastructure for the first time?

Follow these steps:

1. **Prerequisites**: Install AWS CDK, Node.js 18+, and configure AWS credentials
2. **Navigate to CoreInfra**: `cd infraestructure/CoreInfra`
3. **Install dependencies**: `npm install`
4. **Deploy**: `./deploy-core-infra.sh`
5. **Verify**: Check AWS Console for VPC, RDS, Lambda, API Gateway resources

Detailed steps in [Infrastructure Setup](../operations/infrastructure-setup.md).

### How do I update a Lambda function with new code?

**Method 1: Automated (Recommended)**

```bash
cd lambdas/{service-name}
docker build -t sybol/{service-name}:latest .
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin {account-id}.dkr.ecr.eu-west-1.amazonaws.com
docker tag sybol/{service-name}:latest {account-id}.dkr.ecr.eu-west-1.amazonaws.com/sybol/{service-name}:latest
docker push {account-id}.dkr.ecr.eu-west-1.amazonaws.com/sybol/{service-name}:latest
aws lambda update-function-code --function-name {service-name} --image-uri {account-id}.dkr.ecr.eu-west-1.amazonaws.com/sybol/{service-name}:latest
```

**Method 2: Using Infrastructure Script**

```bash
cd infraestructure/CoreInfra
./update-lambda-image.sh {service-name}
```

See [Deployment Procedures](../operations/deployment-procedures.md) for details.

### How do I roll back a Lambda deployment if something goes wrong?

**Option 1: Redeploy Previous Image**

```bash
aws lambda update-function-code \
  --function-name businesslogic \
  --image-uri {account-id}.dkr.ecr.eu-west-1.amazonaws.com/sybol/businesslogic:{previous-tag}
```

**Option 2: Use Lambda Versions**

If you published a version before deployment:

```bash
aws lambda update-alias \
  --function-name businesslogic \
  --name prod \
  --function-version {previous-version}
```

**Recommendation**: Always tag Docker images with commit SHA or version number:

```bash
docker tag sybol/businesslogic:latest sybol/businesslogic:v1.2.3
docker tag sybol/businesslogic:latest sybol/businesslogic:git-abc123
```

### How long does tenant onboarding take?

**Automated Onboarding**: ~5-10 minutes

Breakdown:
1. Domain and certificate provisioning: 2-3 minutes (ACM validation)
2. CDK stack deployment: 3-5 minutes (CloudFront, S3, IAM, KMS)
3. Database and secrets setup: 1-2 minutes
4. Frontend deployment: 1 minute

**Manual Onboarding** (if following docs step-by-step): ~30-45 minutes

Use the automated script for efficiency:

```bash
cd infraestructure/ClientInfra
./onboard-client.sh repsol
```

See [Tenant Onboarding](../operations/tenant-onboarding.md).

### Can I deploy different service versions independently?

Yes. Each Lambda function is deployed independently:

- Update `businesslogic` without affecting `catalog`
- Deploy `backoffice` fixes without touching `propagate`

However, consider API contract compatibility:
- If `businessLogic` depends on `catalog` API changes, coordinate deployments
- Use feature flags for breaking changes
- Test integration in staging environment first

---

## Authentication Questions

### How do I set up multi-factor authentication (MFA)?

**For Admin Users (Required):**

1. User signs in for the first time
2. Application prompts for MFA enrollment
3. User scans QR code with authenticator app (Google Authenticator, Authy)
4. User enters 6-digit TOTP code to verify
5. MFA is enabled for future logins

**Administrator Enforcement:**

```bash
aws cognito-idp set-user-mfa-preference \
  --username user@example.com \
  --software-token-mfa-settings Enabled=true,PreferredMfa=true \
  --user-pool-id eu-west-1_XXXXXXXXX
```

See [Authentication](../security/authentication.md) for detailed MFA setup.

### How do I recover access if a user loses their MFA device?

**Administrator Recovery Process:**

1. Verify user identity through alternative means (email verification, support ticket)
2. Disable MFA for the user:

```bash
aws cognito-idp admin-set-user-mfa-preference \
  --username user@example.com \
  --user-pool-id eu-west-1_XXXXXXXXX \
  --software-token-mfa-settings Enabled=false
```

3. Instruct user to re-enroll with new device on next login
4. Document the incident for audit trail

**Best Practice**: Encourage users to save backup codes or register multiple devices.

### How long do JWT tokens last? How do I refresh them?

**Token Lifetimes:**

| Token Type | Lifetime | Use Case |
|------------|----------|----------|
| Access Token | 1 hour | API authorization |
| ID Token | 1 hour | User identity claims |
| Refresh Token | 30 days | Token renewal |

**Refreshing Tokens:**

```javascript
import { CognitoIdentityProviderClient, InitiateAuthCommand } from "@aws-sdk/client-cognito-identity-provider";

const client = new CognitoIdentityProviderClient({ region: "eu-west-1" });

const command = new InitiateAuthCommand({
  AuthFlow: "REFRESH_TOKEN_AUTH",
  ClientId: process.env.COGNITO_CLIENT_ID,
  AuthParameters: {
    REFRESH_TOKEN: refreshToken
  }
});

const response = await client.send(command);
const { AccessToken, IdToken } = response.AuthenticationResult;
```

Frontend applications should automatically refresh tokens 5 minutes before expiration.

### How does STS AssumeRole work for tenant isolation?

**Flow:**

1. User authenticates with Cognito (receives ID token with `custom:tenant_id`)
2. BusinessLogic Lambda receives authenticated request
3. Lambda extracts `tenant_id` from JWT claims
4. Lambda assumes tenant-specific IAM role:

```javascript
const { STSClient, AssumeRoleCommand } = require("@aws-sdk/client-sts");

const sts = new STSClient({ region: "eu-west-1" });
const roleArn = `arn:aws:iam::${accountId}:role/TenantRole-${tenantId}-admin`;

const assumeRoleResponse = await sts.send(new AssumeRoleCommand({
  RoleArn: roleArn,
  RoleSessionName: `session-${tenantId}-${Date.now()}`
}));

const { AccessKeyId, SecretAccessKey, SessionToken } = assumeRoleResponse.Credentials;
```

5. Lambda uses temporary credentials to access tenant-specific KMS keys and secrets
6. Tenant resources enforce access via IAM policies and KMS key policies

This ensures tenants cannot access each other's encryption keys or database credentials.

See [Security Architecture](../architecture/security-architecture.md).

---

## Troubleshooting Questions

### Why am I getting "Unable to connect to database" errors?

**Common Causes:**

1. **Lambda not in VPC subnets**
   - Verify Lambda configuration includes `sybol-public-subnet-1a` and `sybol-public-subnet-1b`
   - Check Lambda execution role has `AWSLambdaVPCAccessExecutionRole`

2. **Security Group misconfiguration**
   - RDS security group must allow ingress on port 5432 from Lambda security group
   - Verify: RDS-sg allows inbound from lambda-sg

3. **Incorrect database credentials**
   - Verify secret in Secrets Manager matches database user
   - Check `DB_HOST` environment variable is correct RDS endpoint

4. **RDS instance stopped or unavailable**
   - Check RDS cluster status in AWS Console

**Debug Steps:**

```bash
# Test from Lambda
aws lambda invoke --function-name businesslogic \
  --payload '{"path":"/health","httpMethod":"GET"}' \
  response.json

# Check CloudWatch logs
aws logs tail /aws/lambda/businesslogic --follow
```

See [Troubleshooting Guide](../operations/troubleshooting.md).

### Why are Lambda functions slow on first request (cold start)?

**Cold Start Explanation:**

Lambda functions in Docker containers have 2-5 second cold starts:
1. Container image pulled from ECR (~1-2s)
2. Runtime initialization (~0.5-1s)
3. Application bootstrapping (~0.5-1s)
4. Database connection pool initialization (~0.5-1s)

**Mitigation Strategies:**

1. **Provisioned Concurrency** (costs more):
   ```bash
   aws lambda put-provisioned-concurrency-config \
     --function-name businesslogic \
     --provisioned-concurrent-executions 2
   ```

2. **Optimize container image size**:
   - Use multi-stage Docker builds
   - Remove unnecessary dependencies
   - Use Alpine Linux base image

3. **Lazy initialization**:
   - Don't connect to database in global scope
   - Initialize connections on first request

4. **Scheduled warm-up**:
   - EventBridge rule invokes Lambda every 5 minutes with `/health` request

**Acceptable for Sybol use case**: Most credential operations are user-initiated and can tolerate 2-3s latency occasionally.

### How do I debug Lambda function errors in production?

**Step 1: Check CloudWatch Logs**

```bash
# Tail live logs
aws logs tail /aws/lambda/businesslogic --follow --since 5m

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/businesslogic \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000
```

**Step 2: Add Structured Logging**

```javascript
// Good: Structured JSON logs
console.log(JSON.stringify({
  level: "ERROR",
  message: "Failed to issue credential",
  tenantId: "repsol",
  error: error.message,
  stack: error.stack,
  timestamp: new Date().toISOString()
}));
```

**Step 3: Enable X-Ray Tracing** (optional)

```bash
aws lambda update-function-configuration \
  --function-name businesslogic \
  --tracing-config Mode=Active
```

**Step 4: Invoke Locally**

```bash
# Run Lambda container locally
docker run -p 9000:8080 \
  -e DB_HOST=localhost \
  -e DB_PASSWORD=password \
  sybol/businesslogic:latest

# Test
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"path":"/credentials","httpMethod":"POST","body":"{}"}'
```

### What should I do if a tenant reports missing credentials?

**Diagnostic Checklist:**

1. **Verify credential was issued**:
   ```sql
   SELECT id, status, issued_at 
   FROM credentials 
   WHERE holder_id = 'user@example.com' 
   ORDER BY issued_at DESC;
   ```

2. **Check credential status**:
   - Status should be `issued`, not `revoked` or `suspended`
   - Verify expiration date has not passed

3. **Check propagation events**:
   ```sql
   SELECT * FROM propagation_events 
   WHERE credential_id = 'credential-uuid' 
   ORDER BY created_at DESC;
   ```

4. **Verify frontend fetched credential**:
   - Check CloudFront access logs
   - Verify API Gateway request logs

5. **Test credential retrieval API**:
   ```bash
   curl -X GET "https://api.sybol.id/api/bl/credentials/{id}" \
     -H "Authorization: Bearer {access-token}"
   ```

**Common Issues:**
- Credential issued but propagation event failed → Retry propagation
- Frontend cached old credential list → Clear browser cache
- User logged in with wrong account → Verify tenant_id in JWT

---

## Multi-Tenancy Questions

### How is data isolated between tenants?

**Multi-Layer Isolation:**

1. **Database-Level**: Each tenant has a separate PostgreSQL database (`tenant_{tenantId}`)
2. **IAM-Level**: Each tenant has dedicated IAM roles with restricted permissions
3. **KMS-Level**: Each tenant has separate encryption keys with key policies
4. **Application-Level**: Tenant ID extracted from JWT claims and validated on every request
5. **Secret-Level**: Database credentials stored in tenant-specific Secrets Manager entries

**Example Enforcement:**

```javascript
// Extract tenant ID from Cognito JWT
const tenantId = jwtPayload["custom:tenant_id"];

// Assume tenant-specific role
const roleArn = `arn:aws:iam::${accountId}:role/TenantRole-${tenantId}-admin`;
const credentials = await assumeRole(roleArn);

// Connect to tenant-specific database
const dbName = `tenant_${tenantId}`;
const dbClient = new PostgresClient({ database: dbName, credentials });
```

This defense-in-depth approach ensures tenants cannot access each other's data even if application logic fails.

### Can tenants have custom domains for their wallets?

Yes. Each tenant can have a custom subdomain:

- Default: `{tenantId}.staging.wallet.sybol.id`
- Custom: `wallet.repsol.com` (tenant-owned domain)

**Setup for Custom Domain:**

1. Tenant creates DNS CNAME record pointing to CloudFront distribution
2. Request ACM certificate for custom domain in `us-east-1`
3. Update CloudFront distribution with alternate domain name
4. Update DNS to point to CloudFront distribution

This requires tenant DNS access and coordination with Sybol operations team.

### How many tenants can the platform support?

**Technical Limits:**

| Resource | Limit | Bottleneck Point |
|----------|-------|------------------|
| Lambda Concurrent Executions | 1,000 (default) | ~200 tenants under load |
| RDS Aurora Connections | 5,000 (max) | ~250 tenants simultaneously active |
| KMS Keys | 10,000 (soft limit) | ~5,000 tenants |
| S3 Buckets | 1,000 (hard limit per account) | **1,000 tenants** |
| CloudFront Distributions | 200 (default quota) | **200 tenants** |

**Practical Scaling:**

- **0-50 tenants**: No resource concerns
- **50-200 tenants**: Request CloudFront quota increase
- **200-1000 tenants**: Request S3 bucket quota increase, consider multi-account strategy
- **1000+ tenants**: Implement multi-account architecture with AWS Organizations

For most use cases, single-account supports 200-500 tenants comfortably.

### What is the onboarding time for a new tenant?

Automated onboarding: **~5-10 minutes**

Manual verification steps add time:
- KYB (Know Your Business) verification: 1-3 business days
- Custom domain setup: 2-4 hours (DNS propagation)
- Custom frontend branding: 1-2 hours (design review)

See [Tenant Onboarding](../operations/tenant-onboarding.md).

---

## Development Questions

### How do I set up a local development environment?

**Prerequisites:**

- Node.js 18+
- Docker Desktop
- PostgreSQL 17.4 (or Docker container)
- AWS CLI configured

**Steps:**

1. **Clone repository**:
   ```bash
   git clone https://github.com/sybol/sybol-platform.git
   cd sybol-platform
   ```

2. **Set up local database**:
   ```bash
   docker run -d \
     -e POSTGRES_PASSWORD=postgres \
     -p 5432:5432 \
     postgres:17.4-alpine
   ```

3. **Configure environment variables**:
   ```bash
   cd services/businessLogic
   cp .env.example .env
   # Edit .env with local values
   ```

4. **Install dependencies and run**:
   ```bash
   npm install
   npm run dev
   ```

See [Local Development Guide](../development/local-development.md).

### How do I test Lambda functions locally?

**Method 1: Docker Container**

```bash
cd services/businessLogic
docker build -t businesslogic:local .
docker run -p 9000:8080 \
  --env-file .env.local \
  businesslogic:local

# Test
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"path":"/credentials","httpMethod":"GET"}'
```

**Method 2: AWS SAM (Serverless Application Model)**

```bash
sam local start-api --env-vars env.json
```

**Method 3: Direct Node.js Execution**

```bash
cd services/businessLogic
npm run dev  # Runs Express server on port 3001
```

**Recommendation**: Use Docker for production-like environment, Express for rapid iteration.

### What testing strategy does Sybol use?

**Test Pyramid:**

1. **Unit Tests** (~70% coverage target):
   - Jest for Node.js services
   - Test business logic, utilities, model validation
   - Mock external dependencies (database, AWS services)

2. **Integration Tests** (~20%):
   - Test API endpoints with real database (test container)
   - Verify database migrations
   - Test credential issuance flow end-to-end

3. **E2E Tests** (~10%):
   - Playwright for frontend wallet application
   - Test complete user journeys (signup, receive credential, present)

**Running Tests:**

```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests
cd webApps/wwc
npm run test:e2e
```

See [Testing Strategy](../development/testing-strategy.md).

### How do I contribute code to the project?

**Contribution Workflow:**

1. **Create feature branch**:
   ```bash
   git checkout -b feature/add-credential-templates
   ```

2. **Write code following standards**:
   - ESLint configuration enforced
   - Prettier for code formatting
   - See [Coding Standards](../development/coding-standards.md)

3. **Write tests**:
   - Unit tests for new functions
   - Update integration tests if API changes

4. **Commit with conventional commits**:
   ```bash
   git commit -m "feat(catalog): add credential template versioning"
   ```

5. **Push and create pull request**:
   ```bash
   git push origin feature/add-credential-templates
   ```

6. **Code review and approval**:
   - At least one approval required
   - All tests must pass
   - Linting must pass

See [Contributing Guide](../development/contributing.md).

---

## Cost Questions

### How much does Sybol cost to run per month?

**Cost Summary:**

- **Core infrastructure**: ~$60/month (1M requests/month)
- **Per tenant**: ~$4/month per tenant

**Examples:**

| Scenario | Monthly Cost |
|----------|--------------|
| 1 tenant, low usage (10K req/mo) | $65 |
| 5 tenants, moderate usage (100K req/mo) | $85 |
| 20 tenants, high usage (1M req/mo) | $140 |
| 50 tenants, enterprise usage (5M req/mo) | $350 |

See [AWS Resources - Cost Estimates](aws-resources.md#cost-estimates-eu-west-1) for detailed breakdown.

### What are the main cost drivers?

**Top 5 Cost Drivers:**

1. **RDS Aurora Serverless**: $45/month (~70% of core costs)
   - Scales based on ACU (0.5-2 ACU auto-scaling)
   - Optimization: Use Aurora Serverless v2 pause feature (not yet implemented)

2. **Lambda Compute**: $8-20/month (variable with usage)
   - 512 MB memory × execution time
   - Optimization: Reduce memory if profiling shows low utilization

3. **API Gateway**: $3.50 per 1M requests
   - Optimization: Cache responses when possible

4. **KMS Keys**: $2/month per tenant (2 keys × $1)
   - Fixed cost, cannot optimize

5. **CloudFront**: $0.85-2/month per tenant
   - Optimization: Increase cache TTL, use regional cache

### How can I reduce costs?

**Cost Optimization Strategies:**

1. **RDS Aurora Capacity**:
   - Monitor ACU usage with CloudWatch
   - Reduce max ACU if consistently under-utilized
   - Consider Aurora Serverless v2 pause (not yet supported for PostgreSQL 17)

2. **Lambda Memory Allocation**:
   - Use AWS Lambda Power Tuning tool
   - May discover 256 MB is sufficient (reduces costs 50%)

3. **CloudWatch Log Retention**:
   - Current: 7 days (reasonable)
   - Consider: 3 days for non-production environments

4. **S3 Lifecycle Policies**:
   - Move infrequently accessed frontend assets to S3 Intelligent-Tiering
   - Delete old deployment artifacts

5. **API Response Caching**:
   - Cache catalog responses (schema definitions rarely change)
   - Cache DID documents (immutable once created)

6. **Development Environment**:
   - Stop RDS in dev environment overnight
   - Use on-demand instances instead of reserved

**Expected Savings**: 20-30% reduction ($140/month → $100/month for 20 tenants)

### Is there a free tier?

**AWS Free Tier Coverage (First 12 Months):**

- **Lambda**: 1M requests/month + 400,000 GB-seconds compute (free forever)
- **API Gateway**: 1M HTTP API requests/month (12 months)
- **Cognito**: Up to 50,000 MAU (free forever)
- **CloudFront**: 1 TB data transfer + 10M requests/month (12 months)
- **S3**: 5 GB storage + 20,000 GET requests/month (12 months)

**After Free Tier:**
- Small usage (~1-5 tenants) costs $65-85/month
- Most AWS charges are pay-per-use with no minimum

**Recommendation**: Deploy to AWS free tier account for first year to minimize costs during development and early adoption.

---

## Compliance and Security Questions

### Is Sybol compliant with GDPR?

**GDPR Compliance Features:**

1. **Data Minimization**: Only essential user data stored
2. **Right to Erasure**: `DELETE /users/{id}` endpoint removes all personal data
3. **Data Portability**: `GET /users/{id}/export` returns all user data in JSON format
4. **Consent Management**: Credentials include explicit user consent records
5. **Encryption**: Data encrypted at rest (RDS encryption) and in transit (TLS 1.3)
6. **Audit Trails**: All database operations logged to CloudWatch

**AWS GDPR Compliance**: AWS services used by Sybol are GDPR-compliant (see AWS DPA).

**Recommendation**: Conduct full GDPR audit with legal counsel before production launch.

### How does Sybol implement eIDAS 2.0 compliance?

**eIDAS 2.0 Requirements:**

1. **Qualified Electronic Signatures (QES)**:
   - PAdES Lambda implements qualified signatures using AWS CloudHSM or KMS
   - See [Cryptography](../security/cryptography.md)

2. **Verifiable Credentials**:
   - W3C Verifiable Credentials 2.0 standard
   - JSON-LD with cryptographic proofs

3. **Decentralized Identifiers (DIDs)**:
   - `did:sybol` method registered
   - DID documents stored in backoffice database

4. **Trust Framework**:
   - Anchored to European Blockchain Service Infrastructure (EBSI) (roadmap)

See [Key Concepts - eIDAS 2.0](../overview/key-concepts.md) for detailed explanation.

---

## References

- [Architecture Overview](../architecture/system-overview.md)
- [Troubleshooting Guide](../operations/troubleshooting.md)
- [Operations Runbook](../operations/README.md)
- [Security Documentation](../security/README.md)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
