# ADR-0001: AWS Cognito for User Authentication

**Status:** Accepted

**Date:** 2024-Q2

**Authors:** @tech-lead, @backend-team

**Deciders:** @architect, @security-lead, @product-owner

---

## Context and Problem Statement

The Sybol platform requires a robust authentication and authorization system to manage users across all services (Backoffice, Business Logic, Catalog, IOM, SVault) with support for:
- Traditional email/password authentication
- Multi-Factor Authentication (MFA)
- Password recovery and self-service account management
- OAuth 2.0 / OpenID Connect standards
- Integration with AWS infrastructure (S3, Lambda, CloudWatch, RDS)
- Session management with JWT tokens
- User attribute management (tenant ID, roles, permissions)
- Support for multiple user types (Holders, Issuers, Verifiers, Administrators)

The system must be secure, scalable, and minimize development effort while aligned with regulatory requirements (GDPR, eIDAS 2.0).

**Question:** What authentication provider should Sybol use across all platform services?

## Decision Drivers

- **Security Requirements:** MFA, secure token storage, audit logging, credential protection
- **AWS Ecosystem Integration:** Already using AWS Lambda, RDS, S3, CloudWatch
- **Time to Market:** Need production-ready solution quickly for multiple services
- **Compliance:** GDPR compliance, SOC 2, ISO 27001 certifications needed
- **Scalability:** Must handle 10K+ users initially, 100K+ future across all tenants
- **Cost:** Budget constraints for initial multi-service deployment
- **Team Expertise:** Team has AWS experience, limited identity provider experience
- **Maintenance:** Prefer managed service over self-hosted infrastructure
- **Multi-Tenant Support:** Need tenant isolation and customization across platform
- **Service Integration:** Must work seamlessly with all backend services (Node.js/Express)

## Considered Options

### Option 1: AWS Cognito

**Description:** Fully managed authentication service by AWS with User Pools for user directory and Identity Pools for AWS credentials.

**Pros:**
- ✅ Native AWS integration (S3, Lambda, API Gateway, RDS)
- ✅ Fully managed service (no infrastructure to maintain)
- ✅ Built-in MFA support (SMS, TOTP, email)
- ✅ Compliance certifications (SOC, ISO, HIPAA, PCI DSS)
- ✅ Pay-as-you-go pricing (50K MAU free tier)
- ✅ JWT token-based authentication (standard format)
- ✅ Advanced security features (compromised credential detection, adaptive authentication)
- ✅ Custom attributes for tenant ID and roles
- ✅ SDK support for JavaScript and Node.js (AWS SDK v3)
- ✅ Trigger functions with Lambda for custom auth flows
- ✅ User pool groups for role-based access control
- ✅ Fine-grained access control via IAM policies

**Cons:**
- ❌ Vendor lock-in to AWS ecosystem
- ❌ Limited customization of hosted UI
- ❌ Migration complexity if switching providers
- ❌ Learning curve for AWS-specific concepts
- ❌ Costs scale with active users
- ❌ Some advanced features require custom Lambda triggers

**Cost:** 
- Free tier: 50,000 MAU (Monthly Active Users)
- Beyond: $0.0055 per MAU
- Estimated Year 1: $0-500/month
- MFA: $0.15 per authentication for SMS (TOTP free)

**Implementation Effort:** Medium (2-3 weeks)

### Option 2: Auth0

**Description:** Third-party identity-as-a-service platform with extensive integrations and customization options.

**Pros:**
- ✅ Rich feature set (passwordless, social login, anomaly detection)
- ✅ Excellent documentation and community
- ✅ Highly customizable UI and branding
- ✅ Multi-cloud support (not locked to AWS)
- ✅ Advanced rules engine for complex auth logic
- ✅ Better flexibility for future migrations
- ✅ Extensive third-party integrations

**Cons:**
- ❌ Additional vendor relationship and contract
- ❌ Higher cost ($240/month minimum for production)
- ❌ Less native AWS integration (requires custom work)
- ❌ No free tier for production use
- ❌ External dependency (not in AWS VPC)
- ❌ Requires learning Auth0-specific concepts
- ❌ Additional network latency for auth calls

**Cost:**
- Essential plan: $240/month (1,000 MAU base)
- Additional users: $0.24 per MAU
- Estimated Year 1: $2,880-6,000/month

**Implementation Effort:** Medium (2-3 weeks)

### Option 3: Keycloak (Self-Hosted)

**Description:** Open-source identity and access management solution supporting OAuth 2.0, OpenID Connect, and SAML.

**Pros:**
- ✅ No licensing costs (open source)
- ✅ Full control and customization
- ✅ No vendor lock-in
- ✅ Standards-based (OAuth 2.0, OIDC, SAML)
- ✅ Large community and ecosystem
- ✅ Multi-tenancy support built-in
- ✅ Flexible deployment options

**Cons:**
- ❌ Infrastructure management required (EC2, RDS, high availability)
- ❌ Security updates and patches our responsibility
- ❌ DevOps overhead (monitoring, backups, scaling, disaster recovery)
- ❌ No AWS native integration (custom coding needed)
- ❌ Team lacks Keycloak expertise
- ❌ Longer implementation time
- ❌ Database management complexity

**Cost:**
- Software: Free
- Infrastructure: $300-800/month (EC2, RDS, Load Balancer)
- DevOps time: $1,000-2,000/month equivalent
- Total Estimated Year 1: $15,600-33,600

**Implementation Effort:** High (6-8 weeks)

### Option 4: Custom Built Solution

**Description:** Build authentication system from scratch using Node.js, JWT, bcrypt, and PostgreSQL.

**Pros:**
- ✅ Complete control over features
- ✅ No third-party dependencies
- ✅ Optimized for exact requirements
- ✅ No recurring licensing costs
- ✅ Direct database integration

**Cons:**
- ❌ Significant development time (3+ months)
- ❌ Security risks (home-grown crypto is dangerous)
- ❌ Compliance burden (SOC 2 audit for custom auth)
- ❌ Ongoing maintenance and security updates
- ❌ No MFA, password recovery out of the box
- ❌ Delays product launch significantly
- ❌ Team must become security experts
- ❌ Liability for security breaches

**Cost:**
- Development: $40,000-80,000 (3-6 months * developer salary)
- Security audit: $15,000-30,000
- Ongoing maintenance: High (20-30% developer time)

**Implementation Effort:** Very High (12-16 weeks)

## Decision Outcome

**Chosen option:** "AWS Cognito" because it provides the optimal balance of security, scalability, AWS integration, cost-effectiveness, and time-to-market for the Sybol platform's specific needs.

### Expected Positive Consequences

- **Fast Implementation:** Production-ready authentication across all services in 2-3 weeks
- **Security:** Enterprise-grade security out of the box with AWS compliance certifications
- **Cost-Effective:** Free tier covers initial users, scales predictably
- **Maintenance-Free:** AWS handles patching, updates, infrastructure management
- **Native Integration:** Seamless integration with Lambda, API Gateway, S3, RDS
- **Team Velocity:** Team can leverage existing AWS knowledge
- **Scalability:** Auto-scales to millions of users without infrastructure changes
- **Multi-Service Support:** Single authentication system for all platform services
- **Audit Trail:** CloudWatch logs provide complete authentication audit history

### Expected Negative Consequences

- **AWS Lock-In:** Migration to another provider would be complex and costly
- **Customization Limits:** Hosted UI customization is limited (must use custom UI for advanced branding)
- **Documentation Gaps:** Some advanced Cognito features poorly documented
- **Cost Scaling:** Costs increase linearly with user growth (predictable but concerning at scale)
- **Lambda Dependency:** Custom auth flows require Lambda trigger management

### Mitigation Strategies

- **Lock-In Risk:** 
  - Abstract authentication logic in service layer wrappers
  - Use standard JWT tokens (portable to other providers)
  - Document migration path in recovery procedures
  - Maintain authentication interface abstraction
  
- **Customization Limits:**
  - Build custom authentication UI for Backoffice and WWC
  - Leverage Lambda triggers for custom business logic
  - Use Cognito API directly for programmatic access
  
- **Documentation:**
  - Create comprehensive internal documentation for each service
  - Document all Cognito configurations in infrastructure as code (CDK)
  - Maintain runbooks for common operations
  
- **Cost Scaling:**
  - Monitor MAU growth closely via CloudWatch
  - Implement user lifecycle management (delete inactive users)
  - Re-evaluate pricing at 50K MAU milestone
  - Consider Reserved Capacity for predictable workloads

## Implementation Details

### Required Changes

**Infrastructure (AWS CDK):**
- Create Cognito User Pool with MFA enabled
- Configure User Pool Client for each application (Backoffice, WWC)
- Create Cognito Identity Pool for AWS credential federation
- Set up Lambda triggers for custom auth flows
- Configure user pool groups for RBAC (admin, issuer, verifier, holder)
- Set up custom attributes: tenantId, role, organizationId
- Enable advanced security features (compromised credential check)
- Configure password policies and account recovery

**Backend Services Integration:**
- All services (Backoffice, Business Logic, Catalog, IOM, SVault):
  - JWT token validation middleware
  - Token refresh logic
  - User context extraction from tokens
  - Role-based authorization checks
  - Tenant isolation based on Cognito attributes

**Frontend Applications:**
- `webApps/wwc`: Cognito SDK integration for wallet UI
- `services/backoffice`: Admin authentication and user management
- Implement token storage (secure, httpOnly cookies)
- Automatic token refresh before expiration

**Configuration:**
- Environment variables for all services:
  - `AWS_COGNITO_USER_POOL_ID`
  - `AWS_COGNITO_CLIENT_ID`
  - `AWS_REGION`
  - `JWT_ISSUER` (for validation)

### Dependencies

- `@aws-sdk/client-cognito-identity-provider` ^3.987.0
- `@aws-sdk/client-cognito-identity` ^3.983.0
- `@aws-sdk/credential-provider-cognito-identity` ^3.972.3
- `jsonwebtoken` ^9.0.0 (for JWT validation in backend)
- `aws-jwt-verify` ^4.0.0 (for Cognito JWT verification)

### Migration Path

*Not applicable - greenfield implementation*

## Validation

**Success Criteria:**
- ✅ User can sign up, sign in, sign out successfully across all applications
- ✅ MFA enrollment and verification works for all user types
- ✅ Password recovery flow completes end-to-end
- ✅ Token refresh happens automatically before expiration
- ✅ Authentication success rate > 99.5%
- ✅ Authorization checks work correctly per tenant
- ✅ Implementation completed in < 3 weeks
- ✅ Zero security incidents in first 6 months
- ✅ All services use consistent authentication mechanism

**Monitoring:**
- CloudWatch metrics for failed login attempts (per service)
- Alert on authentication failure rate > 5%
- Track MAU growth for cost projections
- Monthly security audit of Cognito configuration
- Monitor token refresh failures
- Track MFA adoption rate

## Related Decisions

- [ADR-0003: Multi-Tenant Database Design](0003-multi-tenant-database-design.md) - Tenant isolation complements Cognito tenantId attribute
- Infrastructure CDK: CoreInfra Cognito User Pool Configuration
- WWC ADR-0003: Context API for Auth State Management

## References

- [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [Cognito Security Best Practices](https://docs.aws.amazon.com/cognito/latest/developerguide/security.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [W3C Verifiable Credentials - Authentication](https://www.w3.org/TR/vc-data-model/#authentication)
- [eIDAS 2.0 Authentication Requirements](https://digital-strategy.ec.europa.eu/en/policies/eidas-regulation)
- [JWT Best Current Practices](https://datatracker.ietf.org/doc/html/rfc8725)

## Notes

- **Alternative Evaluated Later:** We briefly considered Azure AD B2C but ruled it out due to lack of AWS integration
- **Social Login:** Deferred to Phase 2 - Cognito supports but not needed for MVP
- **Enterprise SSO:** Future requirement - Cognito supports SAML federation
- **Biometric Auth:** Cognito supports WebAuthn/FIDO2 for future passwordless flows
- **API Key Authentication:** Some machine-to-machine services may use API keys instead of Cognito

---

**Review Date:** 2025-Q2 (Re-evaluate when reaching 50K MAU)  
**Last Updated:** March 10, 2026  
**Status:** In Production since 2024-Q3
