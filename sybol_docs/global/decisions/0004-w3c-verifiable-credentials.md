# ADR-0004: W3C Verifiable Credentials Standard

**Status:** Accepted

**Date:** 2024-Q1

**Authors:** @architect, @crypto-lead, @product-owner

**Deciders:** @cto, @architect, @security-lead, @compliance, @business-lead

---

## Context and Problem Statement

Sybol is a verifiable credentials platform enabling issuance, storage, and verification of digital credentials. The platform must support:
- Digital identity credentials (eID, driver's license, diplomas)
- Professional certifications and qualifications
- Access control credentials
- Verifiable attestations and claims
- Cross-organization credential interoperability
- Selective disclosure (share specific claims, not entire credential)
- Cryptographic proof of authenticity
- Revocation and status checking

The platform operates in the European Union and must align with:
- eIDAS 2.0 Regulation (digital identity framework)
- EU Digital Identity Wallet requirements
- GDPR data protection principles

**Question:** What credential format and data model should Sybol use for representing and exchanging verifiable credentials?

## Decision Drivers

- **Interoperability:** Credentials must work across organizations and wallets
- **Regulatory Compliance:** eIDAS 2.0 endorses W3C standards
- **Future-Proofing:** Standard should have long-term industry support
- **Selective Disclosure:** Users control what data verifiers see
- **Privacy:** Minimize correlation and tracking across verifiers
- **Cryptographic Security:** Strong proof of authenticity and integrity
- **Portability:** Users can migrate credentials between wallets
- **Industry Adoption:** Align with emerging digital credential ecosystem
- **Revocation:** Support credential revocation and status checking
- **Developer Experience:** Clear specifications and tooling available

## Considered Options

### Option 1: W3C Verifiable Credentials (VC) Data Model

**Description:** W3C Recommendation for representing credentials in a standard, verifiable, cryptographically-secure manner. Uses JSON-LD for semantic interoperability with multiple proof formats (JWT, Data Integrity Proofs).

**Pros:**
- ✅ International W3C standard (industry consensus)
- ✅ eIDAS 2.0 explicitly references W3C VC standard
- ✅ EU Digital Identity Wallet Architecture Reference Framework (ARF) based on W3C VC
- ✅ Broad ecosystem support (Microsoft, Google, governments)
- ✅ Multiple proof formats: JWT, JSON-LD with BBS+ (selective disclosure)
- ✅ Semantic interoperability via JSON-LD contexts
- ✅ Strong privacy features (selective disclosure, unlinkability)
- ✅ Supports credential revocation (Status List 2021)
- ✅ Wallet portability (standard format)
- ✅ Rich tooling and libraries (did-jwt-vc, Veramo, etc.)
- ✅ Decentralized Identifier (DID) support for issuers

**Cons:**
- ❌ JSON-LD complexity (steep learning curve)
- ❌ Multiple proof formats (implementation choices)
- ❌ Evolving ecosystem (some specs still in draft)
- ❌ BBS+ signatures require specific cryptographic libraries
- ❌ Larger payload size compared to proprietary formats
- ❌ Need to choose DID method (did:web, did:key, did:ethr)

**Implementation Effort:** Medium (4-6 weeks for full implementation)

**Standards Compliance:**
- ✅ W3C Verifiable Credentials Data Model v1.1 (Recommendation)
- ✅ eIDAS 2.0 compliant
- ✅ EU Digital Identity Wallet ARF compliant

### Option 2: X.509 Certificates Only

**Description:** Use traditional X.509 PKI certificates (similar to SSL/TLS) as credential format with custom attribute extensions.

**Pros:**
- ✅ Mature, well-understood technology
- ✅ Strong cryptographic foundation (RSA/ECDSA signatures)
- ✅ Existing PKI infrastructure can be reused
- ✅ Certificate revocation (CRL, OCSP) well established
- ✅ Team has PKI expertise (PAdES service uses X.509)
- ✅ Smaller payload size
- ✅ FIPS 140-2 certified implementations available

**Cons:**
- ❌ Not designed for verifiable credentials use cases
- ❌ Poor selective disclosure (all-or-nothing)
- ❌ Limited semantic interoperability
- ❌ No standard for representing claims/attributes
- ❌ Not eIDAS 2.0 compliant for digital identity wallets
- ❌ Certificate chains increase complexity
- ❌ User experience challenges (binary format)
- ❌ Limited wallet portability
- ❌ Not privacy-preserving (correlation easy)
- ❌ Does not align with EU wallet initiatives

**Implementation Effort:** Low (2-3 weeks, leverage existing PAdES infrastructure)

**Standards Compliance:**
- ❌ Not eIDAS 2.0 wallet compliant
- ⚠️ Can be used alongside W3C VC for specific use cases

### Option 3: OAuth 2.0 Access Tokens (JWT)

**Description:** Use OAuth 2.0 flow with JWT access tokens containing user claims as credentials.

**Pros:**
- ✅ Widely deployed and understood
- ✅ Simple implementation (standard JWT libraries)
- ✅ Existing authentication systems support OAuth 2.0
- ✅ Short-lived tokens (automatic expiration)
- ✅ Smaller payload size
- ✅ Developer-friendly

**Cons:**
- ❌ Not designed for portable credentials
- ❌ Tied to authorization server (not user-controlled)
- ❌ No standard for credential revocation
- ❌ Poor offline verification support
- ❌ No selective disclosure
- ❌ Not eIDAS 2.0 compliant
- ❌ Limited semantic interoperability
- ❌ User doesn't "own" credentials (server-centric)
- ❌ correlation risk (JWT IDs trackable)

**Implementation Effort:** Low (1-2 weeks)

**Standards Compliance:**
- ❌ Not eIDAS 2.0 wallet compliant
- ❌ Not W3C VC compliant

### Option 4: Proprietary Credential Format

**Description:** Design custom JSON schema for credentials with custom signature mechanism.

**Pros:**
- ✅ Complete control over format
- ✅ Optimized for Sybol-specific use cases
- ✅ Simplest implementation (no external standards)
- ✅ Minimal payload size
- ✅ Fast development (no standard constraints)

**Cons:**
- ❌ Zero interoperability with other systems
- ❌ Not eIDAS 2.0 compliant (regulatory risk)
- ❌ Cannot participate in EU digital wallet ecosystem
- ❌ No portability (vendor lock-in for users)
- ❌ Security risks (custom crypto is dangerous)
- ❌ No community support or tooling
- ❌ Requires custom wallet implementation
- ❌ Limited adoption potential
- ❌ Migration path to standards unclear

**Implementation Effort:** Medium (3-4 weeks)

**Standards Compliance:**
- ❌ Not eIDAS 2.0 compliant (business risk)
- ❌ Not W3C VC compliant

## Decision Outcome

**Chosen option:** "W3C Verifiable Credentials Data Model" because it is the international standard for verifiable credentials, mandated by eIDAS 2.0, and provides the interoperability, privacy, and future-proofing required for a European digital identity wallet platform.

### Expected Positive Consequences

- **Regulatory Compliance:** Aligns with eIDAS 2.0 and EU wallet requirements (legal requirement)
- **Interoperability:** Credentials work across wallets and verifiers
- **Future-Proof:** Industry momentum behind W3C VC standard
- **User Empowerment:** User-controlled credentials (not server-dependent)
- **Privacy by Design:** Selective disclosure and unlinkability
- **Ecosystem Participation:** Can integrate with EU Digital Identity Wallet infrastructure
- **Trust:** Standards-based approach increases platform credibility
- **Portability:** Users can export credentials to other W3C VC wallets
- **Innovation:** Enables advanced features (zero-knowledge proofs, BBS+)

### Expected Negative Consequences

- **Complexity:** JSON-LD and multiple proof formats have learning curve
- **Implementation Time:** More complex than proprietary format
- **Payload Size:** Larger credentials compared to minimal formats
- **Library Dependencies:** Need to evaluate and choose VC libraries
- **DID Method Selection:** Must choose DID method (did:web recommended)
- **Evolving Standards:** Some VC specs still maturing (manageable risk)

### Mitigation Strategies

- **JSON-LD Complexity:**
  - Use simplified JSON-LD contexts (avoid deeply nested contexts)
  - Provide internal training on W3C VC concepts
  - Use existing libraries (Veramo, did-jwt-vc) instead of building from scratch
  - Create internal documentation and examples
  
- **Implementation Complexity:**
  - Phase 1: JWT-based VCs (simpler, faster to market)
  - Phase 2: JSON-LD with Data Integrity Proofs (richer features)
  - Phase 3: BBS+ signatures (selective disclosure)
  - Incremental adoption reduces risk
  
- **Payload Size:**
  - Use compact JSON-LD contexts
  - Implement credential caching in wallet
  - Use QR codes for in-person verification (compressed)
  
- **DID Method Choice:**
  - Start with did:web (simple, no blockchain required)
  - Document migration path to did:key or did:ethr if needed
  - DID method abstraction in code (swappable)
  
- **Library Selection:**
  - Evaluate: Veramo, SpruceID, Digital Bazaar libraries
  - Choose based on: documentation, maintenance, eIDAS 2.0 support
  - Contribute back to open-source libraries (build reputation)

## Implementation Details

### Required Changes

**Backend Services:**
```
services/businessLogic/src/
  vc/
    issuer.js              # Issue W3C VCs
    verifier.js            # Verify W3C VCs
    revocation.js          # Status List 2021 management
    schema-registry.js     # JSON-LD context definitions
  did/
    resolver.js            # DID resolution (did:web)
    registry.js            # Issuer DID management
```

**Credential Structure (Example):**
```json
{
  "@context": [
    "https://www.w3.org/2018/credentials/v1",
    "https://sybol.eu/contexts/credentials/v1"
  ],
  "type": ["VerifiableCredential", "EducationalCredential"],
  "issuer": "did:web:sybol.eu:issuers:university-madrid",
  "issuanceDate": "2024-03-10T10:00:00Z",
  "credentialSubject": {
    "id": "did:key:z6Mkr...",
    "degree": {
      "type": "BachelorDegree",
      "name": "Computer Science"
    }
  },
  "proof": {
    "type": "JsonWebSignature2020",
    "created": "2024-03-10T10:00:00Z",
    "verificationMethod": "did:web:sybol.eu:issuers:university-madrid#key-1",
    "proofPurpose": "assertionMethod",
    "jws": "eyJhbGciOiJFZERTQSIsImI2NCI6ZmFsc2UsImNyaXQiOlsiYjY0Il19..."
  }
}
```

**DID Document (did:web):**
```json
{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:web:sybol.eu:issuers:university-madrid",
  "verificationMethod": [{
    "id": "did:web:sybol.eu:issuers:university-madrid#key-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:web:sybol.eu:issuers:university-madrid",
    "publicKeyMultibase": "z6Mkr..."
  }],
  "assertionMethod": ["#key-1"]
}
```

**Web App Integration:**
```
webApps/wwc/src/
  vc/
    wallet.js              # W3C VC wallet functionality
    presentation.js        # Verifiable Presentation creation
    qr-code.js             # QR code for credential sharing
```

### Dependencies

- `@digitalbazaar/vc` ^5.0.0 - W3C VC library
- `did-jwt-vc` ^3.2.0 - JWT-based VCs
- `did-resolver` ^4.1.0 - DID resolution
- `@transmute/did-key-ed25519` ^0.3.0 - did:key support
- `@transmute/did-key-web-crypto` ^0.3.0 - did:web support
- `jsonld` ^8.0.0 - JSON-LD processing
- `@digitalcredentials/jsonld-signatures` ^9.3.0 - Signature suites

### Supported Credential Types (Initial)

1. **Identity Credential** - Basic identity attributes (name, DOB, nationality)
2. **Professional Credential** - Certifications, licenses
3. **Educational Credential** - Diplomas, degrees
4. **Organization Membership** - Employee credentials, affiliations
5. **Access Credential** - Permissions, entitlements

### Revocation Strategy

Use W3C Status List 2021:
- Bitstring-based revocation list
- Hosted at: `https://sybol.eu/credentials/status/{statusListId}`
- Efficient checking (single HTTP request)
- Privacy-preserving (verifier cannot determine which credential checked)

### Migration Path

*Not applicable - greenfield implementation*

## Validation

**Success Criteria:**
- ✅ Issue W3C VC compliant credentials
- ✅ Verify W3C VC credentials successfully
- ✅ Credentials validate using third-party W3C VC validators
- ✅ DID documents resolve correctly (did:web)
- ✅ Revocation checking functional (Status List 2021)
- ✅ Verifiable Presentations created successfully
- ✅ Credentials portable to other W3C VC wallets
- ✅ eIDAS 2.0 technical requirements met

**Monitoring:**
- Credential issuance success rate > 99.5%
- Verification success rate > 99.9%
- DID resolution latency < 500ms
- Revocation check latency < 1 second
- Number of credential types issued (track adoption)

## Related Decisions

- [ADR-0001: AWS Cognito Authentication](0001-aws-cognito-authentication.md) - Authentication separate from credential identity
- [ADR-0003: Multi-Tenant Database Design](0003-multi-tenant-database-design.md) - Credential storage per tenant
- PAdES Service: X.509 certificates used for document signatures (complementary to W3C VC)

## References

- [W3C Verifiable Credentials Data Model v1.1](https://www.w3.org/TR/vc-data-model/)
- [eIDAS 2.0 Regulation](https://digital-strategy.ec.europa.eu/en/policies/eidas-regulation)
- [EU Digital Identity Wallet Architecture Reference Framework](https://github.com/eu-digital-identity-wallet/architecture-and-reference-framework)
- [W3C Decentralized Identifiers (DIDs) v1.0](https://www.w3.org/TR/did-core/)
- [Status List 2021](https://w3c-ccg.github.io/vc-status-list-2021/)
- [Verifiable Credentials Implementation Guidelines](https://w3c.github.io/vc-imp-guide/)
- [BBS+ Signatures for Selective Disclosure](https://w3c-ccg.github.io/ldp-bbs2020/)

## Notes

- **Proof Format:** Phase 1 uses JWT (simpler), Phase 2 migrates to JSON-LD Data Integrity Proofs
- **DID Method:** Starting with did:web (no blockchain), may add did:ethr for Ethereum integration
- **Selective Disclosure:** BBS+ signatures for selective disclosure planned for Phase 3
- **Zero-Knowledge Proofs:** Not in initial scope, evaluate for future privacy enhancements
- **mDL Integration:** ISO 18013-5 mobile driver's license support planned (uses CBOR + W3C VC)

---

**Review Date:** 2025-Q4 (Re-evaluate when eIDAS 2.0 implementation guidelines finalized)  
**Last Updated:** March 10, 2026  
**Status:** In Production since 2024-Q3
