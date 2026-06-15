# ADR-0002: W3C Verifiable Credentials and VEIA Dual Standard Support

**Status:** Accepted

**Date:** 2024-Q2

**Authors:** @architect, @standards-team

**Deciders:** @cto, @product-owner, @compliance-lead

---

## Context and Problem Statement

WWC is designed as a digital wallet for verifiable credentials. The ecosystem of verifiable credentials is rapidly evolving with multiple competing and complementary standards:

- **W3C Verifiable Credentials Data Model** - Global standard by W3C (JSON-LD based)
- **VEIA Trust Framework** - JWT-based credentials popular in certain regions
- **ISO/IEC 18013-5 mDL** - Mobile driver's license standard
- **OpenID4VC** - OpenID Foundation's credential format

Our target markets include:
- European Union - eIDAS 2.0 compliance requiring W3C VC support
- Latin America - VEIA adoption by government entities
- Global enterprises - Varied requirements

**Question:** Which credential standard(s) should WWC support to maximize interoperability and market reach?

## Decision Drivers

- **Market Requirements:** Multiple regions using different standards
- **Regulatory Compliance:** eIDAS 2.0 mandates W3C VC
- **Customer Demand:** Existing VEIA deployments in government sector
- **Interoperability:** Need to work with multiple issuers and verifiers
- **Future-Proofing:** Standards landscape is still maturing
- **Development Complexity:** Supporting multiple formats increases complexity
- **Verification Costs:** More standards = more verification code
- **Time to Market:** Supporting one standard is faster
- **Blockchain Integration:** W3C VC has better blockchain tooling

## Considered Options

### Option 1: W3C Verifiable Credentials Only

**Description:** Support only W3C Verifiable Credentials Data Model v1.1+ with JSON-LD canonicalization and linked data signatures.

**Pros:**
- ✅ Global standard with wide adoption
- ✅ eIDAS 2.0 compliant
- ✅ Rich ecosystem (libraries, tools, validators)
- ✅ JSON-LD provides semantic interoperability
- ✅ Multiple signature suites (EdDSA, ECDSA, RSA)
- ✅ Status List 2021 for revocation
- ✅ Better blockchain integration (Ethereum, IPFS)
- ✅ Simpler codebase (one standard)

**Cons:**
- ❌ Misses Latin American VEIA market
- ❌ Cannot work with existing VEIA government systems
- ❌ JSON-LD complexity (canonicalization, context resolution)
- ❌ Larger payload size
- ❌ Customers request VEIA support

**Implementation Effort:** Medium (4 weeks)

### Option 2: VEIA Trust Framework Only

**Description:** Support only VEIA JWT-based credentials with custom claims structure.

**Pros:**
- ✅ Simpler JWT format (easier to implement)
- ✅ Smaller payload size
- ✅ Better performance (no JSON-LD processing)
- ✅ Government adoption in target markets
- ✅ Existing issuer integrations available
- ✅ Standard JWT libraries (jose)

**Cons:**
- ❌ Not eIDAS 2.0 compliant
- ❌ Regional standard (limited international reach)
- ❌ Less semantic interoperability
- ❌ Fewer tools and libraries
- ❌ Limited revocation mechanisms
- ❌ Blockchain integration requires custom work
- ❌ No W3C ecosystem benefits

**Implementation Effort:** Low (2 weeks)

### Option 3: W3C + VEIA Dual Support (Hybrid)

**Description:** Support both W3C Verifiable Credentials and VEIA JWT credentials with abstraction layer for unified handling.

**Pros:**
- ✅ Maximum market coverage (EU + Latin America)
- ✅ Regulatory compliance (eIDAS 2.0 via W3C)
- ✅ Customer flexibility (issuers choose format)
- ✅ Future-proofed (covers both emerging standards)
- ✅ Competitive advantage (rivals support only one)
- ✅ Can bridge between ecosystems
- ✅ Wallet can convert between formats

**Cons:**
- ❌ Increased development complexity (2x standards)
- ❌ More testing required
- ❌ Larger bundle size (more libraries)
- ❌ Maintenance overhead for both standards
- ❌ UI complexity (users see different formats)
- ❌ Longer development time

**Implementation Effort:** High (6-8 weeks)

### Option 4: Universal Resolver Pattern

**Description:** Build credential-agnostic system that detects and routes to appropriate handlers dynamically.

**Pros:**
- ✅ Supports W3C, VEIA, and future standards
- ✅ Extensible architecture
- ✅ Clean separation of concerns

**Cons:**
- ❌ Over-engineering for current needs
- ❌ Complex abstraction layer
- ❌ Risk of leaky abstractions
- ❌ Significantly longer development time

**Implementation Effort:** Very High (12+ weeks)

## Decision Outcome

**Chosen option:** "W3C + VEIA Dual Support (Hybrid)" because market research shows 60% of target customers require W3C (eIDAS 2.0) and 40% require VEIA, with 15% needing both. The competitive advantage and revenue potential justify the additional complexity.

### Expected Positive Consequences

- **Market Coverage:** Can sell to EU, Latin America, and global enterprises
- **Regulatory Compliance:** Meets eIDAS 2.0 requirements
- **Customer Satisfaction:** Flexibility increases win rate
- **Future-Proof:** Handles evolving standards landscape
- **Competitive Moat:** Rivals typically support only one standard
- **Revenue Impact:** 25-30% larger addressable market

### Expected Negative Consequences

- **Development Time:** +2-3 weeks vs single standard
- **Code Complexity:** Two verification paths to maintain
- **Bundle Size:** +120KB (jsonld library is heavy)
- **Testing Matrix:** 2x test cases for credential operations
- **Documentation Burden:** Must document both standards
- **Support Complexity:** Support team needs training on both

### Mitigation Strategies

- **Complexity Management:**
  - Abstract common operations in unified interface
  - Create resolver pattern: `credentialResolver(credential)` detects type
  - Separate services: `w3c.js` and `veia.js` with shared interface
  
- **Bundle Size:**
  - Lazy load `jsonld` library only when W3C credentials encountered
  - Consider WebAssembly for JSON-LD canonicalization (future)
  
- **Testing:**
  - Shared test fixtures for both formats
  - Parameterized tests for common operations
  - Integration tests with real issuers for both standards
  
- **Documentation:**
  - Clear API docs showing both formats
  - Migration guide between formats
  - Developer examples for both standards

## Implementation Details

### Required Changes

**Service Layer:**

**`src/services/w3c.js`** - W3C Verifiable Credentials handler
```javascript
- w3cCredentialResolver(credential)
- w3cPresentationResolver(presentation)
- w3cStatusCheck(credential)
- verifyW3CSignature(credential)
```

**`src/services/veia.js`** - VEIA Trust Framework handler
```javascript
- veiaCredentialResolver(credential)
- veiaPresentationResolver(presentation)
- extractClaimsFromCredential(credential)
- verifyVEIASignature(credential)
```

**`src/services/sybol.js`** - Unified API wrapper
```javascript
- detectCredentialType(credential)
- resolveCredential(credential) // routes to w3c/veia
- verifyCredential(credential)
- createPresentation(credentials, request)
```

**UI Components:**
- Credential cards that handle both formats
- Presentation builder supporting both types
- Format indicator badge (W3C logo vs VEIA logo)

### Dependencies

**W3C Support:**
- `jsonld` ^8.3.2 - JSON-LD processing
- `@digitalbazaar/vc` (optional, may implement ourselves)

**VEIA Support:**
- `jose` ^5.9.6 - JWT operations (already used for Cognito)

**Both:**
- `ethers` ^6.13.4 - Blockchain verification

### Architecture

```
Credential Flow:
┌─────────────────┐
│   Credential    │
│   (unknown)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  detectType()   │  ← Checks @context (W3C) vs typ:"JWT" (VEIA)
└────────┬────────┘
         │
    ┌────┴─────┐
    ↓          ↓
┌────────┐ ┌──────────┐
│ w3c.js │ │ veia.js  │
└────┬───┘ └─────┬────┘
     │           │
     └──────┬────┘
            ↓
    ┌──────────────┐
    │   Verified   │
    │  Credential  │
    └──────────────┘
```

## Validation

**Success Criteria:**
- ✅ Can import and verify W3C credentials from 3+ issuers
- ✅ Can import and verify VEIA credentials from government issuer
- ✅ Presentation creation works for both formats
- ✅ Verification success rate > 99%
- ✅ Status checking (revocation) works for both
- ✅ Bundle size increase < 150KB gzipped
- ✅ Implementation completed in 8 weeks

**Monitoring:**
- Track credential type distribution (W3C vs VEIA ratio)
- Verification failure rates per type
- Performance metrics (time to verify each type)
- User confusion metrics (support tickets by type)

**Validation Results (2025-Q1):**
- ✅ W3C: 68% of credentials
- ✅ VEIA: 32% of credentials
- ✅ Bundle size: +118KB (within target)
- ✅ No verification failures attributable to dual support

## Related Decisions

- Depends on [ADR-0001: AWS Cognito Authentication](0001-aws-cognito-authentication.md) - User identity separate from credentials
- Influences frontend architecture (credential display components)
- Related to blockchain integration ADR (future)

## References

- [W3C Verifiable Credentials Data Model v1.1](https://www.w3.org/TR/vc-data-model/)
- [W3C VC Implementation Guide](https://www.w3.org/TR/vc-imp-guide/)
- [VEIA Trust Framework Specification](https://veia.org/specifications)
- [eIDAS 2.0 European Digital Identity Wallet](https://digital-strategy.ec.europa.eu/en/policies/eidas-regulation)
- [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/)
- [Status List 2021](https://w3c-ccg.github.io/vc-status-list-2021/)

## Notes

### W3C vs VEIA Key Differences

| Aspect | W3C VC | VEIA |
|--------|--------|------|
| **Format** | JSON-LD | JWT |
| **Signature** | Linked Data Proofs | JWS (JSON Web Signature) |
| **Context** | @context URLs | Custom claims |
| **Size** | Larger (150-300KB) | Smaller (10-50KB) |
| **Semantics** | Rich (linked data) | Basic (flat claims) |
| **Tooling** | Mature W3C ecosystem | Limited libraries |
| **Blockchain** | Native support | Custom integration |
| **Revocation** | Status List 2021 | Custom mechanisms |

### Design Decisions

1. **Type Detection:** Check for `@context` (W3C) or `typ: "JWT"` (VEIA) header
2. **Storage:** Store credentials as-is (no conversion) to preserve signatures
3. **Display:** Unified UI with format badge indicator
4. **Conversion:** Don't auto-convert between formats (lossy operation)
5. **Verification:** Each format verifies using appropriate library
6. **Presentation:** Support mixed presentations (W3C + VEIA in one presentation)

### Future Considerations

- **ISO mDL Support:** Mobile driver's license standard (potential ADR-0005)
- **OpenID4VC:** OpenID Foundation format (monitoring adoption)
- **SD-JWT VC:** Selective disclosure with JWT (W3C working group item)
- **Credential Translation:** Build W3C ↔ VEIA converter service

---

**Review Date:** 2025-Q4 (Re-evaluate when ISO mDL adoption increases)  
**Last Updated:** March 5, 2026  
**Status:** In Production, performing well with 68/32 split
