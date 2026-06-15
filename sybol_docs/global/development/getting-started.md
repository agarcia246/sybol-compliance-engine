# Getting Started with Sybol Development

## Purpose

This guide walks you through setting up the Sybol development environment and deploying your first changes.

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Minimum Version | Purpose |
|------|-----------------|---------|
| Node.js | 18+ | Runtime for services and infrastructure |
| npm | 8+ | Package management |
| Docker | 20+ | Container runtime for local development |
| Docker Compose | 2+ | Multi-container orchestration |
| AWS CLI | 2+ | AWS service interaction |
| Git | 2.30+ | Version control |
| PostgreSQL Client | 14+ | Database access (psql) |

### Verify Prerequisites

```bash
node --version    # Should be 18.x or higher
npm --version     # Should be 8.x or higher
docker --version  # Should be 20.x or higher
aws --version     # Should be 2.x
git --version
psql --version
```

### AWS Configuration

Configure AWS credentials for development environment:

```bash
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Output format: `json`

Request development AWS credentials from your team lead.

---

## Repository Setup

### Clone Repository

```bash
git clone <repository-url>
cd sybolRelases
```

### Understand Repository Structure

```
sybolRelases/
├── services/           # Backend microservices (Lambda containers)
│   ├── backoffice/     # Admin and user management
│   ├── businessLogic/  # Core credential operations
│   ├── catalog/        # Schema and template management
│   └── propagate/      # Credential propagation
├── infraestructure/    # AWS CDK infrastructure code
│   ├── CoreInfra/      # Core AWS resources (VPC, RDS, Cognito)
│   └── ClientInfra/    # Client-specific resources
├── lambdas/            # Utility Lambda functions
├── webApps/            # React frontend applications
├── docs/               # Project documentation (you are here)
└── deploy/             # Deployment scripts
```

See [Repository Structure](repository-structure.md) for detailed breakdown.

---

## Initial Setup

### Step 1: Install Dependencies

Install dependencies for all services:

```bash
# Core infrastructure
cd infraestructure/CoreInfra
npm install
cd ../..

# Client infrastructure
cd infraestructure/ClientInfra
npm install
cd ../..

# Services
cd services/backoffice
npm install
cd ../businessLogic
npm install
cd ../catalog
npm install
cd ../propagate
npm install
cd ../..
```

**Tip**: Create a script to automate this for your workflow.

### Step 2: Environment Configuration

Each service requires environment variables. Copy example files:

```bash
# For each service
cd services/backoffice
cp .env.example .env
# Edit .env with your configuration
```

Required variables for most services:

```env
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://user:password@localhost:5432/sybol_dev
AWS_REGION=us-east-1
COGNITO_USER_POOL_ID=<your-cognito-pool-id>
COGNITO_CLIENT_ID=<your-cognito-client-id>
JWT_SECRET=<dev-jwt-secret>
```

See [Local Development](local-development.md) for detailed environment setup.

### Step 3: Database Setup

Start local PostgreSQL:

```bash
# Using Docker
docker run --name sybol-postgres \
  -e POSTGRES_USER=sybol \
  -e POSTGRES_PASSWORD=sybol123 \
  -e POSTGRES_DB=sybol_dev \
  -p 5432:5432 \
  -d postgres:14
```

Run migrations:

```bash
cd services/database
# Run migration scripts
psql -h localhost -U sybol -d sybol_dev -f migrations/001_initial_schema.sql
```

### Step 4: First Build

Build and test a service:

```bash
cd services/backoffice

# Install dependencies (if not done)
npm install

# Run linting
npm run lint

# Run tests
npm test

# Start service locally
npm run dev
```

Expected output:
```
Server running on port 3000
Connected to database
```

Test the service:

```bash
curl http://localhost:3000/health
# Expected: {"status":"ok"}
```

---

## Deploy to Development Environment

### Step 1: Deploy Core Infrastructure

```bash
cd infraestructure/CoreInfra
npm run build
npm run deploy
```

This creates:
- VPC and networking
- RDS PostgreSQL database
- Cognito user pool
- ECR repositories
- Lambda IAM roles

### Step 2: Build and Push Service Images

```bash
cd services/backoffice

# Build Docker image
docker build -t sybol-backoffice:dev .

# Tag for ECR
docker tag sybol-backoffice:dev <account-id>.dkr.ecr.<region>.amazonaws.com/sybol-backoffice:dev

# Login to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

# Push image
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/sybol-backoffice:dev
```

### Step 3: Update Lambda Functions

```bash
cd infraestructure/CoreInfra

# Update Lambda with new image
./update-lambda-image.sh sybol-backoffice dev
```

### Step 4: Verify Deployment

```bash
# Get Lambda function URL
aws lambda get-function-url-config --function-name sybol-backoffice-dev

# Test endpoint
curl <function-url>/health
```

---

## Common Issues and Solutions

### Port Already in Use

```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Docker Image Build Fails

```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t sybol-backoffice:dev .
```

### Database Connection Fails

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
psql -h localhost -U sybol -d sybol_dev -c "SELECT 1;"
```

### AWS Credentials Issues

```bash
# Verify credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

---

## Next Steps

Now that your environment is ready:

1. **Learn the Codebase**: Read [Repository Structure](repository-structure.md)
2. **Local Development**: Set up [Local Development Environment](local-development.md)
3. **Code Standards**: Review [Coding Standards](coding-standards.md)
4. **Testing**: Understand [Testing Strategy](testing-strategy.md)
5. **Contribute**: Follow [Contributing Guidelines](contributing.md)

## Quick Reference Commands

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Lint code
npm run lint

# Start service (with hot reload)
npm run dev

# Build Docker image
docker build -t <service-name>:dev .

# Deploy infrastructure
cd infraestructure/CoreInfra && npm run deploy
```

## Getting Help

- **Documentation**: Check `docs/` folder
- **API Documentation**: See `docs/api/`
- **Architecture**: Read `docs/architecture/`
- **Team Chat**: [Your team channel]
- **Issues**: Create GitHub issue with `question` label

---

## Checklist

Before considering setup complete:

- [ ] Prerequisites installed and verified
- [ ] Repository cloned
- [ ] Dependencies installed for all services
- [ ] Environment variables configured
- [ ] Local PostgreSQL running
- [ ] At least one service starts successfully
- [ ] Tests pass for at least one service
- [ ] Development infrastructure deployed to AWS
- [ ] Service deployed to development environment
- [ ] Can access service health endpoint

Welcome to Sybol development! 🚀
