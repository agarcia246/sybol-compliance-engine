# BusinessLogic API - Verifiable Credentials Management

## Overview
Complete API for managing Verifiable Credentials, Credential Requests, Presentations, and Presentation Requests with JWT token generation following W3C standards.

## Architecture
- **Express.js** - Web framework with security middleware
- **PostgreSQL** - Database with JSONB support for flexible credential data
- **JWT** - W3C Verifiable Credentials token generation
- **AWS Lambda** - Serverless deployment with API Gateway v2.0 support

## Database Setup

### 1. Create Database and Schema
```sql
CREATE DATABASE businesslogic_db;
\c businesslogic_db;
```

### 2. Execute Schema
```bash
psql -U username -d businesslogic_db -f database/schema.sql
```

## Environment Variables

Create `.env` file:
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=businesslogic_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_SSL=false

# JWT
JWT_SECRET=your-super-secret-key
JWT_ISSUER=did:example:issuer123
JWT_EXPIRES_IN=24h

# Server
PORT=3000
NODE_ENV=development
```

## Installation & Running

### Local Development
```bash
# Install dependencies
npm install

# Run database migrations
npm run db:migrate

# Start development server
npm run dev

# Start production server
npm start
```

### Docker
```bash
# Build image
docker build -t businesslogic-api .

# Run container
docker run -p 3000:3000 --env-file .env businesslogic-api
```

## API Endpoints

### Health Check
- `GET /api/bl/health` - Service health status

### Credentials
- `POST /api/bl/credentials` - Create credential
- `GET /api/bl/credentials` - List credentials (paginated)
- `GET /api/bl/credentials/:id` - Get credential by ID
- `POST /api/bl/credentials/:id` - Update credential
- `PATCH /api/bl/credentials/:id/issue` - Issue credential (generates JWT)
- `PATCH /api/bl/credentials/:id/revoke` - Revoke credential

### Credential Requests
- `POST /api/bl/credential-requests` - Create credential request
- `GET /api/bl/credential-requests` - List requests (paginated)
- `GET /api/bl/credential-requests/:id` - Get request by ID
- `POST /api/bl/credential-requests/:id` - Update request
- `PATCH /api/bl/credential-requests/:id/approve` - Approve request
- `PATCH /api/bl/credential-requests/:id/reject` - Reject request

### Presentations
- `POST /api/bl/presentations` - Create presentation
- `GET /api/bl/presentations` - List presentations (paginated)
- `GET /api/bl/presentations/:id` - Get presentation by ID
- `POST /api/bl/presentations/:id` - Update presentation
- `PATCH /api/bl/presentations/:id/verify` - Verify presentation

### Presentation Requests
- `POST /api/bl/presentation-requests` - Create presentation request
- `GET /api/bl/presentation-requests` - List requests (paginated)
- `GET /api/bl/presentation-requests/:id` - Get request by ID
- `POST /api/bl/presentation-requests/:id` - Update request
- `PATCH /api/bl/presentation-requests/:id/respond` - Respond to request
- `PATCH /api/bl/presentation-requests/:id/expire` - Expire request

## Request/Response Examples

### Create Credential
```json
POST /api/bl/credentials
{
  "subjectId": "did:example:subject123",
  "issuerId": "did:example:issuer456",
  "credentialType": "UniversityDegree",
  "claims": {
    "degree": "Bachelor of Science",
    "university": "Example University",
    "graduationDate": "2023-06-15"
  }
}
```

### Issue Credential (Generate JWT)
```json
PATCH /api/bl/credentials/:id/issue
{
  "evidence": [
    {
      "type": "DocumentVerification",
      "document": "diploma.pdf"
    }
  ]
}
```

Response includes W3C compliant JWT token following the credExample.json structure.

## JWT Structure
Generated JWTs follow W3C Verifiable Credentials specification:
- **Header**: JWT type and algorithm
- **Payload**: VC with context, type, issuer, credentialSubject, evidence, proof
- **Signature**: HMAC-SHA256 signature (development) / RSA256 (production)

## Security Features
- **Rate Limiting**: 100 requests per 15 minutes per IP
- **Helmet**: Security headers protection
- **CORS**: Cross-origin resource sharing
- **Input Validation**: Joi schema validation
- **SQL Injection Protection**: Parameterized queries
- **Error Handling**: Comprehensive error responses

## Database Schema
- **credentials**: Main credential storage with JSONB claims
- **credential_requests**: Credential issuance requests
- **presentations**: Credential presentations for verification
- **presentation_requests**: Requests for credential presentations
- **Indexes**: Optimized queries on status, dates, and subject IDs
- **Triggers**: Automatic updated_at timestamps

## Development
```bash
# Run tests
npm test

# Run with watch mode
npm run dev

# Check code style
npm run lint

# Database migrations
npm run db:migrate
npm run db:rollback
```

## Deployment

### AWS Lambda
The service includes Lambda handler with API Gateway v2.0 support:
```bash
# Deploy using Serverless Framework
serverless deploy
```

### Production Considerations
- Use environment variables for secrets
- Enable SSL/TLS for database connections
- Implement proper logging and monitoring
- Use RSA256 for JWT signing in production
- Set up backup and disaster recovery

## Monitoring
- Health check endpoint for load balancers
- Structured logging for debugging
- Error tracking and alerting
- Performance monitoring

## Contributing
1. Fork repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request