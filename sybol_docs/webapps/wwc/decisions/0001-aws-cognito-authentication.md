# ADR-0001: AWS Cognito for User Authentication

**Status:** Accepted

**Date:** 2024-Q2

**Authors:** @tech-lead, @backend-team

**Deciders:** @architect, @security-lead, @product-owner

---

## Context and Problem Statement

WWC requires a robust authentication and authorization system to manage users (Holders, Issuers, Verifiers) with support for:
- Traditional email/password authentication
- Multi-Factor Authentication (MFA)
- Password recovery and self-service account management
- OAuth 2.0 / OpenID Connect standards
- Integration with AWS infrastructure (S3, Lambda, CloudWatch)
- Session management with JWT tokens
- User attribute management (tenant ID, roles, permissions)

The system must be secure, scalable, and minimize development effort while aligned with regulatory requirements (GDPR, eIDAS 2.0).

**Question:** What authentication provider should WWC use?

## Decision Drivers

- **Security Requirements:** MFA, secure token storage, audit logging
- **AWS Ecosystem Integration:** Already using AWS S3, Lambda, CloudWatch
- **Time to Market:** Need production-ready solution quickly
- **Compliance:** GDPR compliance, SOC 2, ISO 27001 certifications needed
- **Scalability:** Must handle 10K+ users initially, 100K+ future
- **Cost:** Budget constraints for initial deployment
- **Team Expertise:** Team has AWS experience, limited identity provider experience
- **Maintenance:** Prefer managed service over self-hosted
- **Multi-Tenant Support:** Need tenant isolation and customization

## Considered Options

### Option 1: AWS Cognito

**Description:** Fully managed authentication service by AWS with User Pools for user directory and Identity Pools for AWS credentials.

**Pros:**
- ✅ Native AWS integration (S3, Lambda, API Gateway)
- ✅ Fully managed service (no infrastructure to maintain)
- ✅ Built-in MFA support (SMS, TOTP)
- ✅ Compliance certifications (SOC, ISO, HIPAA, PCI DSS)
- ✅ Pay-as-you-go pricing (50K MAU free tier)
- ✅ JWT token-based authentication
- ✅ Advanced security features (compromised credential detection)
- ✅ Custom attributes for tenant ID and roles
- ✅ SDK support for JavaScript (AWS SDK v3)
- ✅ Trigger functions with Lambda for custom flows

**Cons:**
- ❌ Vendor lock-in to AWS ecosystem
- ❌ Limited customization of hosted UI
- ❌ Migration complexity if switching providers
- ❌ Learning curve for AWS-specific concepts
- ❌ Costs scale with active users

**Cost:** 
- Free tier: 50,000 MAU (Monthly Active Users)
- Beyond: $0.0055 per MAU
- Estimated Year 1: $0-500/month

**Implementation Effort:** Medium (2-3 weeks)

### Option 2: Auth0

**Description:** Third-party identity-as-a-service platform with extensive integrations and customization options.

**Pros:**
- ✅ Rich feature set (passwordless, social login, anomaly detection)
- ✅ Excellent documentation and community
- ✅ Highly customizable UI
- ✅ Multi-cloud support (not locked to AWS)
- ✅ Advanced rules engine
- ✅ Better flexibility for future migrations

**Cons:**
- ❌ Additional vendor relationship and contract
- ❌ Higher cost ($240/month minimum for production)
- ❌ Less native AWS integration (requires custom work)
- ❌ No free tier for production use
- ❌ External dependency (not in AWS VPC)
- ❌ Requires learning Auth0-specific concepts

**Cost:**
- Essential plan: $240/month (1,000 MAU base)
- Estimated Year 1: $2,880-5,000/month

**Implementation Effort:** Medium (2-3 weeks)

### Option 3: Keycloak (Self-Hosted)

**Description:** Open-source identity and access management solution supporting OAuth 2.0, OpenID Connect, and SAML.

**Pros:**
- ✅ No licensing costs (open source)
- ✅ Full control and customization
- ✅ No vendor lock-in
- ✅ Standards-based (OAuth 2.0, OIDC)
- ✅ Large community and ecosystem
- ✅ Multi-tenancy support built-in

**Cons:**
- ❌ Infrastructure management required (EC2, RDS, high availability)
- ❌ Security updates and patches our responsibility
- ❌ DevOps overhead (monitoring, backups, scaling)
- ❌ No AWS native integration (custom coding needed)
- ❌ Team lacks Keycloak expertise
- ❌ Longer implementation time

**Cost:**
- Software: Free
- Infrastructure: $300-800/month (EC2, RDS, Load Balancer)
- DevOps time: $1,000-2,000/month equivalent

**Implementation Effort:** High (6-8 weeks)

### Option 4: Custom Built Solution

**Description:** Build authentication system from scratch using Node.js, JWT, bcrypt, and PostgreSQL.

**Pros:**
- ✅ Complete control over features
- ✅ No third-party dependencies
- ✅ Optimized for exact requirements
- ✅ No recurring licensing costs

**Cons:**
- ❌ Significant development time (3+ months)
- ❌ Security risks (home-grown crypto is dangerous)
- ❌ Compliance burden (SOC 2 audit for custom auth)
- ❌ Ongoing maintenance and security updates
- ❌ No MFA, password recovery out of the box
- ❌ Delays product launch significantly
- ❌ Team must become security experts

**Cost:**
- Development: $40,000-80,000 (3-6 months * developer salary)
- Security audit: $15,000-30,000
- Ongoing maintenance: High

**Implementation Effort:** Very High (12-16 weeks)

## Decision Outcome

**Chosen option:** "AWS Cognito" because it provides the optimal balance of security, scalability, AWS integration, cost-effectiveness, and time-to-market for our specific needs.

### Expected Positive Consequences

- **Fast Implementation:** Production-ready in 2-3 weeks
- **Security:** Enterprise-grade security out of the box with AWS compliance
- **Cost-Effective:** Free tier covers initial users, scales predictably
- **Maintenance-Free:** AWS handles patching, updates, infrastructure
- **Native Integration:** Seamless S3 access for user files via Identity Pools
- **Team Velocity:** Team can leverage existing AWS knowledge
- **Scalability:** Auto-scales to millions of users without infrastructure changes

### Expected Negative Consequences

- **AWS Lock-In:** Migration to another provider would be complex and costly
- **Customization Limits:** Hosted UI customization is limited (must use custom UI for branding)
- **Documentation Gaps:** Some advanced Cognito features poorly documented
- **Cost Scaling:** Costs increase linearly with user growth (predictable but concerning at scale)

### Mitigation Strategies

- **Lock-In Risk:** 
  - Abstract authentication logic in `services/cognito.js` wrapper
  - Use standard JWT tokens (portable to other providers)
  - Document migration path in ADR-recovery document
  
- **Customization Limits:**
  - Build custom authentication UI (not using hosted UI)
  - Leverage Lambda triggers for custom business logic
  
- **Documentation:**
  - Create comprehensive internal documentation (`docs/AUTH_IMPLEMENTATION.md`)
  - Document all Cognito configurations in infrastructure as code (CDK)

- **Cost Scaling:**
  - Monitor MAU growth closely
  - Implement user lifecycle management (delete inactive users)
  - Re-evaluate pricing at 50K MAU milestone

## Implementation Details

### Required Changes

**Infrastructure (AWS CDK):**
- Create Cognito User Pool with MFA enabled
- Configure User Pool Client for web application
- Create Cognito Identity Pool for AWS credential federation
- Set up Lambda triggers for custom auth flows
- Configure S3 bucket policies for user-specific access

**Application Code:**
- `src/services/cognito.js` - Authentication service wrapper
  - signUp(), signIn(), signOut()
  - confirmSignUp(), forgotPassword(), resetPassword()
  - getCurrentUser(), refreshSession()
  - MFA setup and verification
- `src/context/AuthContext.js` - React Context for auth state
- `src/helpers/axios.helper.js` - Token refresh interceptors

**Configuration:**
- Environment variables:
  - `REACT_APP_AWS_COGNITO_USER_POOL_ID`
  - `REACT_APP_AWS_COGNITO_CLIENT_ID`
  - `REACT_APP_AWS_REGION`

### Dependencies

- `@aws-sdk/client-cognito-identity-provider` ^3.987.0
- `@aws-sdk/client-cognito-identity` ^3.983.0
- `@aws-sdk/credential-provider-cognito-identity` ^3.972.3

### Migration Path

*Not applicable - greenfield implementation*

## Validation

**Success Criteria:**
- ✅ User can sign up, sign in, sign out successfully
- ✅ MFA enrollment and verification works
- ✅ Password recovery flow completes end-to-end
- ✅ Token refresh happens automatically before expiration
- ✅ Authentication success rate > 99.5%
- ✅ Implementation completed in < 3 weeks
- ✅ Zero security incidents in first 6 months

**Monitoring:**
- CloudWatch metrics for failed login attempts
- Alert on authentication failure rate > 5%
- Track MAU growth for cost projections
- Monthly security audit of Cognito configuration

## Related Decisions

- Influences [ADR-0003: Context API over Redux](0003-context-api-over-redux.md) - Auth state management
- Related to Infrastructure ADR: Cognito User Pool Configuration (in CoreInfra repo)

## References

- [AWS Cognito Documentation](https://docs.aws.amazon.com/cognito/)
- [Cognito Security Best Practices](https://docs.aws.amazon.com/cognito/latest/developerguide/security.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [W3C Verifiable Credentials - Authentication](https://www.w3.org/TR/vc-data-model/#authentication)
- [eIDAS 2.0 Authentication Requirements](https://digital-strategy.ec.europa.eu/en/policies/eidas-regulation)

## Notes

- **Alternative Evaluated Later:** We briefly considered Azure AD B2C but ruled it out due to lack of AWS integration
- **Social Login:** Deferred to Phase 2 - Cognito supports but not needed for MVP
- **Enterprise SSO:** Future requirement - Cognito supports SAML federation
- **Biometric Auth:** Cognito supports WebAuthn/FIDO2 for future passwordless flows

---

**Review Date:** 2025-Q2 (Re-evaluate when reaching 50K MAU)  
**Last Updated:** March 5, 2026  
**Status:** In Production since 2024-Q3
