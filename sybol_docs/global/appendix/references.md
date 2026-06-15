# External References

## Purpose

This document provides a curated collection of external resources, standards documentation, AWS service references, tools, libraries, and related projects that support the Sybol platform implementation.

---

## W3C Standards and Specifications

### Verifiable Credentials

| Resource | URL | Description |
|----------|-----|-------------|
| **Verifiable Credentials Data Model v2.0** | https://www.w3.org/TR/vc-data-model-2.0/ | Core specification for verifiable credentials format, proof mechanisms, and data model |
| **Verifiable Credentials Implementation Guidelines** | https://www.w3.org/TR/vc-imp-guide/ | Best practices for implementing VC issuers, holders, and verifiers |
| **Verifiable Credentials JSON Schema** | https://www.w3.org/TR/vc-json-schema/ | JSON Schema-based credential validation |
| **Verifiable Credentials Use Cases** | https://www.w3.org/TR/vc-use-cases/ | Real-world scenarios and implementation patterns |
| **Status List 2021** | https://www.w3.org/TR/vc-status-list/ | Privacy-preserving credential revocation mechanism |
| **Bitstring Status List v1.0** | https://www.w3.org/TR/vc-bitstring-status-list/ | Efficient revocation and suspension status tracking |

**Key Concepts:**
- **Issuer**: Entity that creates and signs credentials
- **Holder**: Entity that receives and stores credentials
- **Verifier**: Entity that validates credential authenticity
- **Proof**: Cryptographic signature ensuring integrity

### Decentralized Identifiers (DIDs)

| Resource | URL | Description |
|----------|-----|-------------|
| **DID Core v1.0** | https://www.w3.org/TR/did-core/ | Specification for decentralized identifier architecture |
| **DID Specification Registries** | https://www.w3.org/TR/did-spec-registries/ | Registry of DID methods and parameters |
| **DID Resolution** | https://w3c-ccg.github.io/did-resolution/ | Protocol for resolving DIDs to DID documents |
| **DID Method Rubric** | https://w3c.github.io/did-rubric/ | Evaluation criteria for DID methods |

**Sybol Implementation:**
- DID Method: `did:sybol`
- Format: `did:sybol:{uuid}`
- Resolution: HTTP API endpoint (`/api/did-document/{did}`)

### JSON-LD and Linked Data

| Resource | URL | Description |
|----------|-----|-------------|
| **JSON-LD 1.1** | https://www.w3.org/TR/json-ld11/ | JSON-based serialization for linked data |
| **JSON-LD API 1.1** | https://www.w3.org/TR/json-ld11-api/ | Processing algorithms for JSON-LD documents |
| **Linked Data Platform** | https://www.w3.org/TR/ldp/ | RESTful API patterns for linked data |

**Context URLs:**
- W3C Credentials: `https://www.w3.org/ns/credentials/v2`
- W3C Examples: `https://www.w3.org/ns/credentials/examples/v2`

### Cryptographic Suite Specifications

| Resource | URL | Description |
|----------|-----|-------------|
| **Data Integrity 1.0** | https://www.w3.org/TR/vc-data-integrity/ | Framework for cryptographic proofs in verifiable credentials |
| **ECDSA Cryptographic Suite** | https://www.w3.org/TR/vc-di-ecdsa/ | ECDSA signature suite for P-256, P-384 curves |
| **EdDSA Cryptographic Suite** | https://www.w3.org/TR/vc-di-eddsa/ | EdDSA signature suite for Ed25519 |
| **JSON Web Signature 2020** | https://www.w3.org/community/reports/credentials/CG-FINAL-lds-jws2020-20220721/ | JWS-based proof format |

**Sybol Implementation:**
- Algorithm: ECDSA with P-256 curve (ES256)
- Key Management: AWS KMS with `ECC_NIST_P256` keys
- Proof Type: `JsonWebSignature2020`

---

## eIDAS and European Regulations

| Resource | URL | Description |
|----------|-----|-------------|
| **eIDAS Regulation (EU) 910/2014** | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R0910 | Original regulation on electronic identification and trust services |
| **eIDAS 2.0 Proposal (2021)** | https://ec.europa.eu/info/strategy/priorities-2019-2024/europe-fit-digital-age/european-digital-identity_en | Proposal for European Digital Identity Wallet |
| **eIDAS 2.0 Regulation (EU) 2024/1183** | https://eur-lex.europa.eu/eli/reg/2024/1183/oj | Amended regulation establishing European Digital Identity Framework |
| **EBSI (European Blockchain Service Infrastructure)** | https://ec.europa.eu/digital-building-blocks/wikis/display/EBSI/Home | EU blockchain infrastructure for verifiable credentials |
| **Architecture and Reference Framework (ARF)** | https://ec.europa.eu/digital-building-blocks/sites/display/EUDIGITALIDENTITYWALLET/ARF | Technical specifications for EUDI Wallet |

**Key eIDAS 2.0 Changes:**
- Mandatory European Digital Identity (EUDI) Wallets for all member states
- Cross-border recognition of electronic identification
- Support for qualified electronic signatures and seals
- Privacy-preserving selective disclosure mechanisms

### GDPR (General Data Protection Regulation)

| Resource | URL | Description |
|----------|-----|-------------|
| **GDPR Full Text** | https://gdpr-info.eu/ | Complete GDPR regulation with commentary |
| **GDPR Articles** | https://gdpr.eu/tag/gdpr/ | Article-by-article explanation |
| **Data Protection Impact Assessment (DPIA)** | https://gdpr.eu/data-protection-impact-assessment-template/ | Template for privacy impact assessments |

**Relevant for Sybol:**
- Article 17: Right to erasure ("right to be forgotten")
- Article 20: Right to data portability
- Article 25: Data protection by design and default
- Article 32: Security of processing

---

## AWS Service Documentation

### Compute

| Service | Documentation | Description |
|---------|---------------|-------------|
| **AWS Lambda** | https://docs.aws.amazon.com/lambda/ | Serverless compute service |
| **Lambda Container Images** | https://docs.aws.amazon.com/lambda/latest/dg/images-create.html | Running Lambda with Docker containers |
| **Lambda Best Practices** | https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html | Performance and cost optimization |
| **Lambda Power Tuning** | https://github.com/alexcasalboni/aws-lambda-power-tuning | Tool for optimizing Lambda memory allocation |

### Networking

| Service | Documentation | Description |
|---------|---------------|-------------|
| **Amazon VPC** | https://docs.aws.amazon.com/vpc/ | Virtual private cloud networking |
| **API Gateway** | https://docs.aws.amazon.com/apigateway/ | HTTP API and REST API management |
| **API Gateway HTTP APIs** | https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html | Optimized low-latency APIs |
| **CloudFront** | https://docs.aws.amazon.com/cloudfront/ | Content delivery network |

### Database

| Service | Documentation | Description |
|---------|---------------|-------------|
| **Amazon RDS** | https://docs.aws.amazon.com/rds/ | Managed relational database service |
| **Aurora Serverless v2** | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html | Auto-scaling Aurora PostgreSQL |
| **RDS Proxy** | https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html | Connection pooling for Lambda |
| **PostgreSQL on RDS** | https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html | PostgreSQL-specific features |

### Security

| Service | Documentation | Description |
|---------|---------------|-------------|
| **AWS Cognito** | https://docs.aws.amazon.com/cognito/ | User authentication and authorization |
| **Cognito User Pools** | https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html | Identity provider configuration |
| **AWS KMS** | https://docs.aws.amazon.com/kms/ | Key Management Service |
| **KMS Asymmetric Keys** | https://docs.aws.amazon.com/kms/latest/developerguide/symmetric-asymmetric.html | Public key cryptography with KMS |
| **AWS Secrets Manager** | https://docs.aws.amazon.com/secretsmanager/ | Secrets storage and rotation |
| **IAM Roles and Policies** | https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html | Access management |
| **STS AssumeRole** | https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html | Temporary credential generation |

### Storage

| Service | Documentation | Description |
|---------|---------------|-------------|
| **Amazon S3** | https://docs.aws.amazon.com/s3/ | Object storage |
| **S3 Static Website Hosting** | https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html | Hosting frontend applications |
| **S3 Lifecycle Policies** | https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html | Automatic data archiving |

### Monitoring

| Service | Documentation | Description |
|---------|---------------|-------------|
| **CloudWatch** | https://docs.aws.amazon.com/cloudwatch/ | Monitoring and observability |
| **CloudWatch Logs** | https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/ | Centralized log management |
| **CloudWatch Alarms** | https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html | Automated alerting |
| **X-Ray** | https://docs.aws.amazon.com/xray/ | Distributed tracing |

### Infrastructure as Code

| Tool | Documentation | Description |
|------|---------------|-------------|
| **AWS CDK** | https://docs.aws.amazon.com/cdk/ | Cloud Development Kit (TypeScript) |
| **CDK Patterns** | https://cdkpatterns.com/ | Reusable CDK architecture patterns |
| **AWS CloudFormation** | https://docs.aws.amazon.com/cloudformation/ | Infrastructure as code (JSON/YAML) |

---

## Tools and Libraries

### JavaScript/Node.js

| Library | Repository | Purpose |
|---------|------------|---------|
| **AWS SDK for JavaScript v3** | https://github.com/aws/aws-sdk-js-v3 | AWS service clients (modular) |
| **jose** | https://github.com/panva/jose | JWT, JWS, JWE operations |
| **jsonld.js** | https://github.com/digitalbazaar/jsonld.js | JSON-LD processing |
| **did-resolver** | https://github.com/decentralized-identity/did-resolver | Universal DID resolver |
| **uuid** | https://github.com/uuidjs/uuid | UUID generation |
| **pg** | https://github.com/brianc/node-postgres | PostgreSQL client |
| **Express** | https://expressjs.com/ | Web application framework |

**Example: JWT Signing with KMS**

```javascript
import { KMSClient, SignCommand } from "@aws-sdk/client-kms";
import { importJWK, SignJWT } from "jose";

const kms = new KMSClient({ region: "eu-west-1" });

async function signJWT(payload, keyId) {
  const jwt = new SignJWT(payload)
    .setProtectedHeader({ alg: "ES256", kid: keyId })
    .setIssuedAt()
    .setExpirationTime("1y");
  
  const signingInput = await jwt.sign(/* custom KMS signer */);
  return signingInput;
}
```

### PDF Processing

| Library | Repository | Purpose |
|---------|------------|---------|
| **pdf-lib** | https://github.com/Hopding/pdf-lib | PDF creation and modification |
| **node-forge** | https://github.com/digitalbazaar/forge | PKI and cryptography |
| **pdfjs-dist** | https://github.com/mozilla/pdf.js | PDF parsing and rendering |

**Sybol PAdES Service:** Uses `pdf-lib` for adding digital signatures to PDF documents.

### Verifiable Credentials Libraries

| Library | Repository | Purpose |
|---------|------------|---------|
| **verifiable-credentials-js** | https://github.com/digitalbazaar/vc-js | W3C VC issuance and verification |
| **jsonld-signatures** | https://github.com/digitalbazaar/jsonld-signatures | JSON-LD cryptographic signatures |
| **did-jwt** | https://github.com/decentralized-identity/did-jwt | JWT-based verifiable credentials |
| **credential-status** | https://github.com/digitalbazaar/credential-status | Status list management |

### Frontend (React)

| Library | Repository | Purpose |
|---------|------------|---------|
| **React** | https://react.dev/ | UI framework |
| **Amazon Cognito Identity SDK** | https://github.com/aws-amplify/amplify-js | Cognito authentication for web |
| **QR Code Generator** | https://github.com/soldair/node-qrcode | QR code generation for credential sharing |
| **React Query** | https://tanstack.com/query/latest | Data fetching and caching |

---

## Development Tools

### Testing

| Tool | URL | Purpose |
|------|-----|---------|
| **Jest** | https://jestjs.io/ | JavaScript testing framework |
| **Supertest** | https://github.com/ladjs/supertest | HTTP API testing |
| **Playwright** | https://playwright.dev/ | End-to-end browser testing |
| **AWS SAM CLI** | https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html | Local Lambda testing |

### Linting and Formatting

| Tool | URL | Purpose |
|------|-----|---------|
| **ESLint** | https://eslint.org/ | JavaScript linting |
| **Prettier** | https://prettier.io/ | Code formatting |
| **Husky** | https://typicode.github.io/husky/ | Git hooks for pre-commit checks |

### CI/CD

| Tool | URL | Purpose |
|------|-----|---------|
| **GitHub Actions** | https://github.com/features/actions | CI/CD automation |
| **Docker** | https://www.docker.com/ | Container runtime |
| **AWS CDK Deploy** | https://docs.aws.amazon.com/cdk/latest/guide/cli.html | Infrastructure deployment |

---

## Standards Organizations

| Organization | URL | Focus |
|--------------|-----|-------|
| **W3C (World Wide Web Consortium)** | https://www.w3.org/ | Web standards, including VCs and DIDs |
| **DIF (Decentralized Identity Foundation)** | https://identity.foundation/ | DID methods and protocols |
| **IETF (Internet Engineering Task Force)** | https://www.ietf.org/ | Internet protocols (JWT, JWS, JSON) |
| **OpenID Foundation** | https://openid.net/ | OpenID Connect and OAuth 2.0 |
| **Kantara Initiative** | https://kantarainitiative.org/ | Identity assurance frameworks |

---

## Related Projects and Platforms

### Open Source Verifiable Credential Platforms

| Project | URL | Description |
|---------|-----|-------------|
| **Veramo** | https://veramo.io/ | TypeScript framework for verifiable data |
| **Trinsic** | https://trinsic.id/ | VC infrastructure platform |
| **Walt.id** | https://walt.id/ | Open-source SSI toolkit |
| **Hyperledger Aries** | https://www.hyperledger.org/use/aries | Enterprise SSI protocol suite |
| **Sphereon SSI SDK** | https://github.com/Sphereon-Opensource | Modular SSI components |

### European Initiatives

| Project | URL | Description |
|---------|-----|-------------|
| **EBSI** | https://ec.europa.eu/digital-building-blocks/wikis/display/EBSI/ | European Blockchain Service Infrastructure |
| **ESSIF (European Self-Sovereign Identity Framework)** | https://essif-lab.eu/ | Research and innovation for SSI |
| **EUDI Wallet Reference Implementation** | https://github.com/eu-digital-identity-wallet | Official European Digital Identity Wallet |

### Identity Verification Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Sumsub** | https://sumsub.com/ | KYC/KYB verification (used by Sybol) |
| **Onfido** | https://onfido.com/ | Identity verification |
| **Jumio** | https://www.jumio.com/ | ID document verification |

---

## Educational Resources

### Books

| Title | Author | Description |
|-------|--------|-------------|
| **Self-Sovereign Identity** | Alex Preukschat, Drummond Reed | Comprehensive guide to decentralized identity |
| **Learning Verifiable Credentials** | Snorre Lothar von Gohren Edwin | Practical VC implementation |

### Courses and Tutorials

| Resource | URL | Description |
|----------|-----|-------------|
| **W3C Verifiable Credentials Tutorial** | https://www.w3.org/TR/vc-imp-guide/ | Official implementation guide |
| **Decentralized Identity Foundation Tutorials** | https://identity.foundation/education/ | DID and VC learning resources |
| **AWS Serverless Workshops** | https://serverlessland.com/workshops | Hands-on Lambda workshops |

### Blogs and Community

| Resource | URL | Description |
|----------|-----|-------------|
| **W3C Credentials Community Group** | https://w3c-ccg.github.io/ | Open standards development |
| **DIF Blog** | https://blog.identity.foundation/ | Decentralized identity updates |
| **AWS Architecture Blog** | https://aws.amazon.com/blogs/architecture/ | Serverless patterns and best practices |

---

## API References

### REST API Standards

| Standard | URL | Description |
|----------|-----|-------------|
| **OpenAPI Specification 3.1** | https://spec.openapis.org/oas/latest.html | RESTful API documentation format |
| **JSON:API** | https://jsonapi.org/ | API design specification |
| **RFC 7807 - Problem Details** | https://tools.ietf.org/html/rfc7807 | Standard error response format |

### Cryptographic Standards

| Standard | URL | Description |
|----------|-----|-------------|
| **RFC 7515 - JSON Web Signature (JWS)** | https://tools.ietf.org/html/rfc7515 | Digital signature format for JSON |
| **RFC 7517 - JSON Web Key (JWK)** | https://tools.ietf.org/html/rfc7517 | Public key representation |
| **RFC 7519 - JSON Web Token (JWT)** | https://tools.ietf.org/html/rfc7519 | Token format for claims |
| **RFC 8032 - Edwards-Curve Digital Signature Algorithm** | https://tools.ietf.org/html/rfc8032 | EdDSA signature scheme |

---

## Compliance and Certification

| Framework | URL | Description |
|-----------|-----|-------------|
| **ISO/IEC 27001** | https://www.iso.org/isoiec-27001-information-security.html | Information security management |
| **SOC 2** | https://www.aicpa.org/soc2 | Security and availability controls |
| **PCI DSS** | https://www.pcisecuritystandards.org/ | Payment card data security |
| **AWS Compliance Programs** | https://aws.amazon.com/compliance/programs/ | AWS certification and attestations |

---

## Community and Support

### Forums and Discussion

| Platform | URL | Description |
|----------|-----|-------------|
| **W3C Credentials CG Mailing List** | https://lists.w3.org/Archives/Public/public-credentials/ | Technical discussions on VCs |
| **DIF Slack** | https://difdn.slack.com/ | Decentralized identity community |
| **AWS Developer Forums** | https://forums.aws.amazon.com/ | AWS technical support |
| **Stack Overflow** | https://stackoverflow.com/questions/tagged/verifiable-credentials | VC implementation questions |

### Issue Trackers

| Project | URL | Purpose |
|---------|-----|---------|
| **W3C VC Data Model Issues** | https://github.com/w3c/vc-data-model/issues | Report spec issues |
| **DID Core Issues** | https://github.com/w3c/did-core/issues | DID specification feedback |
| **AWS SDK Issues** | https://github.com/aws/aws-sdk-js-v3/issues | Report SDK bugs |

---

## References

- [Environment Variables](environment-variables.md)
- [AWS Resources](aws-resources.md)
- [FAQ](faq.md)
- [Security Architecture](../architecture/security-architecture.md)
