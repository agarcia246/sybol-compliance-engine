# src/credentials/ — Darius

Your job here is to take the unsigned VC payload from Javier and submit
it to Sybol's businessLogic API to get back a fully signed Verifiable Credential.

Before you can implement this, you need three things from Iñigo.
You are the one who reaches out to him for these — contact him directly:

1. The issuer DID value for Sybol
2. Confirmation that MEDIA_COMPLIANCE_CREDENTIAL is registered
   in the Sybol catalog schema
3. Whether the signing endpoint is /credentials/issue or a
   dedicated signing endpoint

Contact Iñigo at: inigo@sybol.id
Copy Javier on any technical questions so he stays in the loop.

While you are waiting for the above, scaffold the API call with
placeholder values so the structure is ready to plug in the moment
Iñigo confirms. The function signature, request format, error handling,
and response parsing should all be done — just swap in the real values.

Also make sure errors are surfaced clearly to the team.
If the Sybol API returns unexpected responses or schema mismatches,
log them in detail and flag in the WhatsApp group immediately.

# Darius — Credentials, Deployment, Railway & CI/CD

## Overview

My contribution focused on deployment infrastructure, environment integration, and preparation of the credential issuance pipeline.

The repository now includes:

* Railway deployment configuration
* Qdrant integration through environment variables
* Railway health checks
* Startup resilience when Qdrant is unavailable
* CI pipeline through GitHub Actions
* Unit tests covering API startup and dependency injection
* Documentation for automatic deployment from GitHub

---

# Task Completed

## Railway Deployment

The FastAPI service is configured for Railway using:

```toml
[deploy]
startCommand = "sh -c 'uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT}'"
healthcheckPath = "/health"
restartPolicyType = "on_failure"
```

### Health Endpoint

The application exposes:

```http
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

Railway uses this endpoint to determine deployment success.

---

## Qdrant Integration

The project uses Qdrant as the vector database for the RAG subsystem.

### Required Environment Variables

```env
QDRANT_URL=http://<qdrant-host>:6333
QDRANT_API_KEY=<optional>
```

### Railway Setup

A dedicated Railway service should be created using:

```text
qdrant/qdrant
```

A persistent volume must be attached and mounted at:

```text
/qdrant/storage
```

The FastAPI service communicates with Qdrant through Railway private networking.

---

## Startup Resilience

The API was modified so that a temporary Qdrant outage does not crash the application.

During startup:

```python
try:
    ...
except Exception:
    ...
```

The application continues serving requests and remains healthy even if the vector index cannot be built.

This prevents Railway deployment failures caused by unavailable dependencies.

---

# Credential Issuance

The credential issuance endpoint remains dependent on final information from Sybol.

Pending information:

1. Issuer DID
2. MEDIA_COMPLIANCE_CREDENTIAL registration confirmation
3. Final signing endpoint specification

Expected integration:

```text
FastAPI
    ↓
Sybol Business Logic API
    ↓
Signed Verifiable Credential
```

Placeholder scaffolding has been prepared and can be completed once the final API details are provided.

---

# CI Pipeline

GitHub Actions CI is configured through:

```text
.github/workflows/ci.yml
```

Pipeline triggers:

```yaml
push:
  branches:
    - devel

pull_request:
  branches:
    - devel
    - main
```

The pipeline executes:

### Dependency Installation

```bash
poetry install --with dev
```

### Linting

```bash
poetry run ruff check --fix src tests
poetry run black src tests
```

### Type Checking

```bash
cd src && poetry run mypy .
```

### Testing

```bash
poetry run pytest -q --cov=src
```

Coverage threshold:

```text
80%
```

Current coverage exceeds the requirement.

---

# Local Development

## Install Dependencies

```bash
poetry install --with dev
```

## Configure Environment

```bash
cp src/.env.example src/.env
```

Populate:

```env
QDRANT_URL=http://localhost:6333
MISTRAL_API_KEY=...
```

## Run API

```bash
PYTHONPATH=src poetry run uvicorn api.main:app --reload
```

Verify:

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

---

# Railway Deployment Guide

## Initial Deployment

Install Railway CLI:

```bash
npm install -g @railway/cli
```

Login:

```bash
railway login
```

Deploy:

```bash
railway up
```

View logs:

```bash
railway logs
```

---

# Automatic Deployments from Main

## Prerequisites

The repository owner must:

1. Own or have admin access to the repository
2. Connect GitHub to Railway
3. Grant Railway GitHub App access to the repository

---

## Configure Railway

Open:

```text
Service
    → Source
    → Connect Repo
```

Select:

```text
Repository: sybol-compliance-engine
```

Enable:

```text
Auto Deploy = ON
```

Set branch:

```text
main
```

---

## Deployment Flow

```text
Developer
    ↓
Push to main
    ↓
GitHub Actions CI
    ↓
Tests Pass
    ↓
Railway Auto Deploy
    ↓
Production Environment
```

---

## Verifying Deployment

After every deployment:

```bash
curl https://<railway-domain>/health
```

Expected:

```json
{
  "status": "ok"
}
```

Additionally verify:

```bash
railway logs
```

No startup exceptions should appear.

---

# Repository Handover Notes

Before merging to main:

* Ensure all tests pass
* Ensure Qdrant service is running
* Ensure Railway environment variables are configured
* Ensure Railway is connected to the GitHub repository
* Ensure Auto Deploy targets the `main` branch

After these steps, deployments become fully automatic and no manual `railway up` commands are required.