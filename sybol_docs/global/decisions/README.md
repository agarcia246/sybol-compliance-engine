# Architecture Decision Records (ADRs)

## Purpose

This directory contains Architecture Decision Records (ADRs) for the Sybol platform. An ADR documents a significant architectural decision made during the design and development of the system, including the context, alternatives considered, and rationale for the chosen approach.

ADRs serve as:
- Historical reference for design decisions
- Onboarding documentation for new team members
- Decision-making framework for future changes
- Communication tool between stakeholders

## ADR Status Definitions

- **Proposed**: Under discussion, not yet decided
- **Accepted**: Decision made and implemented
- **Deprecated**: Decision no longer relevant but kept for historical context
- **Superseded**: Replaced by a newer ADR (reference the successor)

## All Decision Records

| ADR | Title | Status | Date | Summary |
|-----|-------|--------|------|---------|
| [0001](0001-aws-cognito-authentication.md) | AWS Cognito for User Authentication | Accepted | 2024-Q2 | Use AWS Cognito as platform-wide authentication provider for all Sybol services |
| [0002](0002-serverless-architecture.md) | Serverless Architecture with Lambda + API Gateway | Accepted | 2024-Q1 | Deploy backend services using AWS Lambda and API Gateway over container-based alternatives |
| [0003](0003-multi-tenant-database-design.md) | Database-Per-Tenant Isolation Strategy | Accepted | 2024-Q1 | Implement multi-tenancy using isolated databases per tenant for security and compliance |
| [0004](0004-w3c-verifiable-credentials.md) | W3C Verifiable Credentials Standard | Accepted | 2024-Q1 | Adopt W3C VC standard as primary credential format for interoperability and eIDAS 2.0 alignment |
| [0005](0005-lambda-vpc-blockchain-connectivity.md) | Lambda VPC Blockchain Connectivity | Accepted | 2024-Q1 | Connect Lambda functions to blockchain nodes via VPC for secure and low-latency communication |
| [0006](0006-catalog-w3c-data-model-alignment.md) | Catalog Service W3C Data Model Alignment | Proposed | 2024-Q1 | Evolve Catalog entities (Document, Claim, Form) to map explicitly to W3C VC types, credentialSubject properties and VP Request templates |

## Creating New ADRs

### When to Create an ADR

Create an ADR when making decisions that:
- Impact system architecture or design
- Have long-term consequences
- Involve significant trade-offs
- Require stakeholder alignment
- Change existing architectural patterns

### ADR Template

```markdown
# ADR-XXXX: [Decision Title]

**Status:** [Proposed|Accepted|Deprecated|Superseded by ADR-YYYY]

**Date:** YYYY-MM-DD

**Authors:** @author1, @author2

**Deciders:** @decision-makers

---

## Context and Problem Statement

[Describe the context and problem requiring a decision]

**Question:** [Specific question being answered]

## Decision Drivers

- **Driver 1:** Description
- **Driver 2:** Description

## Considered Options

### Option 1: [Name]

**Description:** [Brief description]

**Pros:**
- ✅ Advantage 1
- ✅ Advantage 2

**Cons:**
- ❌ Disadvantage 1
- ❌ Disadvantage 2

**Cost:** [Estimate]

**Implementation Effort:** [Low|Medium|High]

[Repeat for each option]

## Decision Outcome

**Chosen option:** "[Option Name]" because [rationale]

### Expected Positive Consequences

- Consequence 1
- Consequence 2

### Expected Negative Consequences

- Consequence 1
- Consequence 2

### Mitigation Strategies

- **Risk 1:**
  - Mitigation approach

## Implementation Details

### Required Changes

[Technical details]

### Dependencies

[Required libraries, services, etc.]

## Validation

**Success Criteria:**
- ✅ Criterion 1
- ✅ Criterion 2

**Monitoring:**
- Metric 1
- Metric 2

## Related Decisions

- [ADR-YYYY: Related Decision](YYYY-title.md)

## References

- [Reference 1](url)

---

**Review Date:** [When to re-evaluate]  
**Last Updated:** [Date]
```

### Naming Convention

ADRs are numbered sequentially: `XXXX-descriptive-title.md`
- Use 4-digit zero-padded numbers (0001, 0002, ...)
- Use lowercase with hyphens for title
- Keep titles concise and descriptive

### Process

1. **Draft**: Create ADR with "Proposed" status
2. **Review**: Share with technical leads and architects
3. **Discussion**: Gather feedback and iterate
4. **Decision**: Update status to "Accepted" or "Rejected"
5. **Implementation**: Execute the decision
6. **Review**: Periodically re-evaluate (set review dates)

## References

- [ADR GitHub Organization](https://adr.github.io/)
- [When Should I Write an ADR?](https://engineering.atspotify.com/2020/04/when-should-i-write-an-architecture-decision-record/)
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

---

**Last Updated:** March 10, 2026
