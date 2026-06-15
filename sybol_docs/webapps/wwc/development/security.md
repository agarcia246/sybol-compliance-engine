# Security Policy

## Supported Versions

We take security seriously and are committed to ensuring the safety of WWC and its users. The following versions are currently supported with security updates:

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| 0.1.x   | :white_check_mark: | Current stable release |
| < 0.1   | :x:                | Not supported |

**Note:** As WWC handles sensitive identity credentials and personal data, we strongly recommend always using the latest version.

## Security Features

WWC implements multiple layers of security:

### Authentication & Authorization
- **AWS Cognito Integration** - Enterprise-grade user authentication
- **Multi-Factor Authentication (MFA)** - Optional 2FA for enhanced security
- **JWT Token Management** - Secure token storage and automatic refresh
- **Role-Based Access Control (RBAC)** - Granular permissions per user

### Data Protection
- **Encrypted Communication** - All API calls over HTTPS/TLS
- **Token Encryption** - Sensitive tokens encrypted in browser storage
- **Input Sanitization** - Protection against XSS attacks
- **CORS Policy** - Restricted cross-origin requests

### Credential Security
- **W3C Standard Compliance** - Verifiable Credentials best practices
- **Blockchain Verification** - Immutable credential proof storage
- **Signature Verification** - Cryptographic validation using JOSE
- **Status List Checking** - Real-time credential revocation checks

### Infrastructure
- **Docker Container Isolation** - Minimal attack surface
- **CSP Headers** - Content Security Policy enforcement
- **Dependency Scanning** - Regular vulnerability audits
- **Secure Secrets Management** - Environment-based configuration

## Reporting a Vulnerability

**We take all security reports seriously.** If you discover a security vulnerability in WWC, please help us protect our users by reporting it responsibly.

### 🚨 DO NOT create a public GitHub issue for security vulnerabilities

### How to Report

1. **Email**: Send details to **security@sybol.id** (preferred)
2. **Subject Line**: "WWC Security Vulnerability - [Brief Description]"
3. **Encryption**: Use our PGP key for sensitive information (available on request)

### What to Include

Please provide as much information as possible:

- **Vulnerability Type** (e.g., XSS, CSRF, authentication bypass, data exposure)
- **Affected Component** (e.g., login flow, credential issuance, API endpoint)
- **Steps to Reproduce** - Detailed reproduction steps
- **Proof of Concept** - Code, screenshots, or video demonstration
- **Impact Assessment** - Your analysis of potential damage
- **Affected Versions** - Which versions are vulnerable
- **Suggested Fix** (optional) - If you have remediation ideas

### Example Report Format

```markdown
## Vulnerability Summary
Brief description of the issue

## Affected Component
- File/Module: src/services/cognito.js
- Version: 0.1.0

## Severity Assessment
[Critical/High/Medium/Low] - Your assessment

## Steps to Reproduce
1. Navigate to login page
2. Enter credentials: [details]
3. Observe behavior: [details]

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Impact
Potential consequences of exploitation

## Suggested Mitigation
(Optional) Your fix recommendations

## Additional Context
Screenshots, logs, environment details
```

## Response Timeline

We are committed to responding promptly:

| Timeline | Action |
|----------|--------|
| **24 hours** | Initial acknowledgment of your report |
| **72 hours** | Preliminary assessment and severity classification |
| **7 days** | Detailed response with remediation plan |
| **30 days** | Security patch released (for critical vulnerabilities) |
| **90 days** | Public disclosure (coordinated with reporter) |

**Note:** Timelines may vary based on complexity. We will keep you informed throughout the process.

## Severity Classification

We use the following severity levels based on CVSS v3.1:

### Critical (9.0-10.0)
- Authentication bypass allowing unauthorized access
- Remote code execution vulnerabilities
- Direct access to user credentials or private keys
- Blockchain signing key exposure

### High (7.0-8.9)
- Cross-site scripting (XSS) with credential theft potential
- SQL injection or data exposure
- Authorization bypass affecting multiple users
- Token theft or session hijacking

### Medium (4.0-6.9)
- CSRF vulnerabilities with limited impact
- Information disclosure (non-sensitive)
- Denial of service (DoS) with limited availability impact
- Insecure configurations

### Low (0.1-3.9)
- Security best practice violations
- Minor information leaks
- Issues requiring significant user interaction

## Disclosure Policy

### Coordinated Disclosure

We follow responsible disclosure practices:

1. **Report Received** - We acknowledge and begin investigation
2. **Fix Developed** - We develop and test patches
3. **Patch Released** - Security update deployed to production
4. **Coordinated Announcement** - Public disclosure after 90 days or when fix is deployed
5. **Credit Given** - We acknowledge reporters (unless anonymity requested)

### Bug Bounty Program

We do not currently offer a formal bug bounty program, but we:

- Publicly acknowledge security researchers (Hall of Fame)
- Provide detailed technical feedback
- Consider rewards on a case-by-case basis for critical findings

## Security Best Practices for Users

### Developers

- Always use the latest version of WWC
- Keep dependencies updated: `npm audit` and `npm audit fix`
- Never commit `.env` files or credentials to version control
- Use environment variables for all secrets
- Enable MFA for AWS Cognito users
- Review `CHANGELOG.md` for security-related updates

### Deployments

- Use HTTPS/TLS in all environments (including development)
- Implement rate limiting on authentication endpoints
- Configure AWS Cognito password policies (minimum 8 characters, complexity)
- Enable CloudWatch logging for security monitoring
- Regularly rotate AWS credentials and tokens
- Use AWS Secrets Manager or Parameter Store for production secrets

### Users

- Enable Multi-Factor Authentication (MFA) in account settings
- Use strong, unique passwords (password manager recommended)
- Verify credential issuer authenticity before accepting credentials
- Review permission requests carefully
- Log out from shared devices
- Report suspicious activity immediately

## Security Audit History

| Date | Type | Conducted By | Status | Report |
|------|------|--------------|--------|--------|
| TBD | External Penetration Test | TBD | Planned | - |
| TBD | Dependency Audit | Internal | Planned | - |

## Compliance & Standards

WWC adheres to:

- **W3C Verifiable Credentials** - Standard implementation
- **GDPR** - Data protection and privacy requirements
- **eIDAS 2.0** - European digital identity regulation alignment
- **OWASP Top 10** - Web application security best practices
- **AWS Well-Architected Framework** - Security pillar

## Security Contacts

- **Security Team**: security@sybol.id
- **Emergency Contact**: (Include 24/7 contact if available)
- **Security Advisories**: Subscribe to GitHub Security Advisories

## Acknowledgments

We thank the following security researchers for responsible disclosure:

- *No reports received yet - be the first!*

## Additional Resources

- [Authentication Implementation Guide](docs/AUTH_IMPLEMENTATION.md)
- [Security Architecture](docs/architecture/security-architecture.md)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [W3C Verifiable Credentials Security Considerations](https://www.w3.org/TR/vc-data-model/#security-considerations)

---

**Last Updated:** March 5, 2026

Thank you for helping keep WWC and our users safe! 🔒
