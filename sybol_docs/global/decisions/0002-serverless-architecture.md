# ADR-0002: Serverless Architecture with Lambda + API Gateway

**Status:** Accepted

**Date:** 2024-Q1

**Authors:** @architect, @backend-lead

**Deciders:** @cto, @architect, @devops-lead, @finance

---

## Context and Problem Statement

Sybol is a multi-tenant verifiable credentials platform requiring backend services for:
- Credential issuance and verification (Business Logic service)
- Backoffice administration (Backoffice service)
- Credential catalog management (Catalog service)
- Identity and organization management (IOM service)
- Secure vault operations (SVault service)
- Document signing and cryptographic operations (PAdES services)

The platform needs to:
- Support multiple isolated tenants with varying workloads
- Scale from 0 to thousands of requests per second
- Minimize operational overhead for small team
- Optimize costs during low-usage periods
- Deploy rapidly with minimal infrastructure management
- Maintain high availability and fault tolerance

**Question:** What compute architecture should Sybol use for backend services?

## Decision Drivers

- **Team Size:** Small engineering team (3-5 developers), no dedicated DevOps
- **Cost Optimization:** Minimize costs during development and low-usage periods
- **Scalability:** Auto-scale per tenant workload without manual intervention
- **Operational Overhead:** Minimize infrastructure management and maintenance
- **Development Velocity:** Fast iteration and deployment cycles
- **AWS Ecosystem:** Already committed to AWS (RDS, S3, Cognito)
- **Multi-Tenancy:** Efficient resource utilization across tenants
- **Cold Start Tolerance:** Most operations are asynchronous or user-initiated
- **Regulatory Compliance:** Need audit trails and isolated execution environments

## Considered Options

### Option 1: AWS Lambda + API Gateway (Serverless)

**Description:** Event-driven, serverless compute with API Gateway for HTTP routing and Lambda functions for business logic. Each service runs as independent Lambda functions triggered by API Gateway.

**Pros:**
- ✅ Zero infrastructure management (no servers to patch or maintain)
- ✅ Auto-scales from 0 to thousands of concurrent executions
- ✅ Pay-per-execution pricing (no cost when idle)
- ✅ Built-in high availability and fault tolerance
- ✅ Native AWS service integration (RDS Proxy, S3, Cognito)
- ✅ Fast deployment (seconds, not minutes)
- ✅ Natural tenant isolation (separate invocations)
- ✅ CloudWatch logging and monitoring included
- ✅ IAM-based security model
- ✅ Support for Node.js (existing team expertise)
- ✅ API Gateway handles rate limiting and throttling
- ✅ Low barrier to entry for small team

**Cons:**
- ❌ Cold start latency (500ms-3s for first request)
- ❌ 15-minute execution time limit per invocation
- ❌ 6 MB request/response payload limit (API Gateway)
- ❌ More complex debugging and local testing
- ❌ Vendor lock-in to AWS Lambda runtime
- ❌ Concurrent execution limits (1000 default, can request increase)
- ❌ Stateless execution model (requires external state management)

**Cost Estimate (Year 1):**
- Lambda free tier: 1M requests/month + 400,000 GB-seconds compute
- Beyond free tier: $0.20 per 1M requests + $0.0000166667 per GB-second
- API Gateway: $3.50 per million requests (after 1M free)
- Estimated: $100-300/month for 10M requests/month

**Implementation Effort:** Low (1-2 weeks)

### Option 2: Amazon ECS Fargate (Managed Containers)

**Description:** Containerized services using Docker, orchestrated by ECS, running on serverless Fargate compute.

**Pros:**
- ✅ No cold starts (containers run continuously)
- ✅ No execution time limits
- ✅ Full control over container environment
- ✅ Easier local development (Docker compose)
- ✅ Portable containers (can migrate to EKS or other clouds)
- ✅ Support for long-running processes
- ✅ Standard HTTP server patterns

**Cons:**
- ❌ Always-on costs (minimum 1 vCPU + 2GB RAM per service)
- ❌ Manual scaling configuration required
- ❌ Infrastructure management (task definitions, services, load balancers)
- ❌ Slower deployment (1-3 minutes for rolling updates)
- ❌ More complex networking (VPC, subnets, security groups)
- ❌ Requires Application Load Balancer ($16/month base cost)
- ❌ Team must learn ECS concepts and Docker orchestration
- ❌ Health checks, logging configuration required

**Cost Estimate (Year 1):**
- Fargate: $0.04048 per vCPU-hour + $0.004445 per GB-hour
- For 5 services (0.25 vCPU, 0.5 GB each): ~$27/service/month = $135/month base
- Application Load Balancer: $16/month + $0.008/LCU-hour
- CloudWatch logs: $0.50/GB ingested
- Estimated: $200-400/month minimum (always-on)

**Implementation Effort:** Medium (3-4 weeks)

### Option 3: Amazon EKS (Kubernetes)

**Description:** Full Kubernetes cluster managed by AWS EKS for container orchestration with maximum flexibility.

**Pros:**
- ✅ Industry-standard orchestration (Kubernetes)
- ✅ Maximum flexibility and control
- ✅ Cloud-agnostic (easy to migrate to GCP/Azure)
- ✅ Advanced deployment strategies (canary, blue-green)
- ✅ Rich ecosystem of tools and add-ons
- ✅ Horizontal pod autoscaling
- ✅ Service mesh capabilities (Istio, Linkerd)

**Cons:**
- ❌ Steep learning curve (Kubernetes complexity)
- ❌ High base cost ($73/month for control plane + node costs)
- ❌ Significant operational overhead (cluster upgrades, security patches)
- ❌ Overkill for small team and current scale
- ❌ Requires dedicated DevOps expertise
- ❌ Complex networking and security model
- ❌ Longer development and deployment cycles
- ❌ More failure modes to manage

**Cost Estimate (Year 1):**
- EKS control plane: $73/month
- Worker nodes: 3x t3.medium ($0.0416/hour) = $90/month minimum
- Load balancer, storage, networking: $50/month
- Estimated: $213/month minimum + operational overhead

**Implementation Effort:** High (8-12 weeks)

### Option 4: EC2-Based Deployment (Traditional Servers)

**Description:** Backend services deployed on EC2 instances with Node.js/Express, managed manually or with Auto Scaling Groups.

**Pros:**
- ✅ Full control over server environment
- ✅ No cold starts or execution limits
- ✅ Simple deployment model (SSH and deploy)
- ✅ Traditional architecture (familiar to all developers)
- ✅ Can run long-running jobs
- ✅ No container or serverless abstractions

**Cons:**
- ❌ Full infrastructure management responsibility
- ❌ Manual security patching (OS, Node.js, dependencies)
- ❌ Always-on costs even when idle
- ❌ Manual scaling configuration and monitoring
- ❌ High availability requires multi-AZ setup (complexity)
- ❌ Need load balancer management
- ❌ Disaster recovery and backup strategy required
- ❌ DevOps overhead for small team
- ❌ Slower deployments (restart services)

**Cost Estimate (Year 1):**
- 2x t3.small instances (high availability): $30/month
- Application Load Balancer: $16/month
- EBS storage: $10/month
- CloudWatch monitoring: $10/month
- Estimated: $66/month minimum

**Implementation Effort:** Medium (2-3 weeks)

## Decision Outcome

**Chosen option:** "AWS Lambda + API Gateway (Serverless)" because it optimally balances cost efficiency, scalability, operational simplicity, and development velocity for Sybol's multi-tenant architecture and small team size.

### Expected Positive Consequences

- **Cost Savings:** Pay only for actual usage, $0 when idle (critical for startup)
- **Zero Operations:** No server maintenance, patching, or capacity planning
- **Automatic Scaling:** Each tenant's workload scales independently
- **Fast Iteration:** Deploy new versions in seconds, rollback instantly
- **Multi-Tenant Efficiency:** Natural isolation between tenant executions
- **Built-in Resilience:** AWS manages fault tolerance and high availability
- **Focus on Business Logic:** Team writes code, not manages infrastructure
- **Audit Trail:** CloudWatch logs every invocation for compliance
- **Security:** Isolated execution environments per request

### Expected Negative Consequences

- **Cold Start Latency:** First request after idle period takes 500ms-3s
- **Architecture Constraints:** Must design for stateless, short-lived executions
- **AWS Coupling:** Tight integration with Lambda runtime and AWS services
- **Debugging Complexity:** Distributed logs, harder to replicate locally
- **Payload Limits:** Large file uploads require S3 direct upload strategy
- **Execution Time Limits:** Long-running jobs need Step Functions or async processing
- **Cost Unpredictability:** Costs scale with actual usage (good and bad)

### Mitigation Strategies

- **Cold Starts:**
  - Use provisioned concurrency for critical endpoints (catalog search, credential verification)
  - Implement warming strategies (scheduled pings every 5 minutes)
  - Optimize function initialization (lazy load dependencies)
  - Use Node.js 20.x runtime (faster cold starts)
  
- **Architecture Constraints:**
  - Design stateless services from start
  - Use RDS for persistent state
  - Use S3 for large files and documents
  - Use SQS for async processing
  - Implement idempotent operations
  
- **Debugging:**
  - Use AWS SAM Local for local testing
  - Implement structured logging (JSON)
  - Use X-Ray for distributed tracing
  - Create comprehensive integration tests
  - Use Lambda Insights for performance monitoring
  
- **Payload Limits:**
  - Use S3 pre-signed URLs for file uploads
  - Return references instead of large data
  - Implement pagination for list operations
  
- **Execution Time Limits:**
  - Break long operations into smaller steps
  - Use Step Functions for orchestration
  - Async processing with SQS/SNS
  - Stream processing for large datasets

- **Cost Management:**
  - Set CloudWatch billing alarms
  - Monitor per-function costs weekly
  - Optimize memory allocation (cost/performance balance)
  - Implement request caching where appropriate

## Implementation Details

### Required Changes

**Infrastructure (AWS CDK):**
```
infraestructure/CoreInfra/lib/
  lambda-service-stack.ts       # Lambda function definitions
  api-gateway-stack.ts           # API Gateway REST API
  lambda-layers-stack.ts         # Shared dependencies layer
  rds-proxy-stack.ts             # RDS Proxy for connection pooling
```

**Service Structure:**
```
services/[service-name]/
  src/
    handlers/                    # Lambda handler functions
      get-credentials.js
      create-credential.js
    middleware/                  # Auth, validation, logging
    services/                    # Business logic
    models/                      # Data models
  package.json
  Dockerfile                     # For Lambda container images
  deploy/
    lambda-config.json           # Function configuration
```

**API Gateway Configuration:**
- REST API with custom domain
- JWT authorizer using Cognito
- Request validation schemas
- API Gateway caching (1 minute TTL)
- Rate limiting: 1000 req/s per API key
- CORS configuration

**Lambda Configuration:**
- Runtime: Node.js 20.x
- Memory: 512 MB (optimized per function)
- Timeout: 30 seconds (most), 5 minutes (SVault operations)
- Environment variables: encrypted with KMS
- Reserved concurrency: 100 per service (prevent runaway costs)
- VPC configuration for RDS access

### Dependencies

- `@aws-sdk/*` (v3) - AWS service clients
- `express` (on Lambda via `serverless-http`) - Optional HTTP handling
- `aws-lambda` - TypeScript types
- `@middy/core` - Middleware engine for Lambda
- `@aws-lambda-powertools/*` - Logging, tracing, metrics

### Deployment Strategy

1. Package functions using CDK Asset bundling (esbuild)
2. Deploy via CDK (infrastructure + code together)
3. Use Lambda versions and aliases for traffic shifting
4. Blue-green deployments for zero downtime
5. Automated rollback on CloudWatch alarm triggers

### Migration Path

*Not applicable - greenfield implementation*

All services designed for Lambda from inception.

## Validation

**Success Criteria:**
- ✅ All services deployed and operational on Lambda
- ✅ P95 latency < 2 seconds (including cold starts)
- ✅ P99 latency < 5 seconds
- ✅ 99.9% success rate for all endpoints
- ✅ Monthly compute costs < $300 for first 6 months
- ✅ Zero operational incidents related to infrastructure
- ✅ Deployment time < 5 minutes per service
- ✅ Developer satisfaction with deployment process

**Monitoring:**
- CloudWatch metrics: invocations, errors, duration, throttles
- X-Ray tracing: end-to-end request flow
- Lambda Insights: memory usage, cold starts
- Custom metrics: business logic errors, tenant activity
- Cost Explorer: daily cost tracking by service
- Alarms: error rate > 1%, P99 latency > 10s, cost > $500/month

## Related Decisions

- [ADR-0001: AWS Cognito Authentication](0001-aws-cognito-authentication.md) - JWT authorizer integration
- [ADR-0003: Multi-Tenant Database Design](0003-multi-tenant-database-design.md) - RDS Proxy usage for Lambda
- Infrastructure: Lambda Layer for shared dependencies
- Infrastructure: API Gateway custom domain and routing

## References

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Serverless Architectures with AWS Lambda](https://d1.awsstatic.com/whitepapers/serverless-architectures-with-aws-lambda.pdf)
- [API Gateway Developer Guide](https://docs.aws.amazon.com/apigateway/)
- [AWS Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning)
- [The Serverless Framework](https://www.serverless.com/framework/docs/)

## Notes

- **Container Images:** We use Lambda container images (up to 10GB) for PAdES services with large dependencies
- **Provisioned Concurrency:** Reserved for future optimization if cold starts become issue
- **Step Functions:** Planned for document signing workflows (multi-step orchestration)
- **EventBridge:** Will integrate for event-driven architecture (Phase 2)
- **Local Testing:** Using AWS SAM Local + LocalStack for development

---

**Review Date:** 2025-Q2 (Re-evaluate if operational overhead grows or costs exceed $500/month)  
**Last Updated:** March 10, 2026  
**Status:** In Production since 2024-Q3
