# ADR-0003: Database-Per-Tenant Isolation Strategy

**Status:** Accepted

**Date:** 2024-Q1

**Authors:** @architect, @backend-lead, @dba

**Deciders:** @cto, @architect, @security-lead, @compliance

---

## Context and Problem Statement

Sybol is a multi-tenant verifiable credentials platform serving multiple organizations (tenants), each requiring:
- Complete data isolation for security and compliance
- Independent backup and restore capabilities
- Tenant-specific performance optimization
- Custom schema extensions per tenant (future)
- Support for tenant data export and migration
- Compliance with GDPR, eIDAS 2.0, and data residency requirements

Each tenant stores sensitive data including:
- User credentials and identity information
- Verifiable credentials and proofs
- Cryptographic keys and certificates
- Audit logs and transaction history
- Organization-specific configurations

**Question:** What multi-tenancy database architecture should Sybol implement to ensure security, isolation, scalability, and compliance?

## Decision Drivers

- **Data Isolation:** Absolute separation of tenant data (regulatory requirement)
- **Security:** Prevent cross-tenant data leakage (critical for trust)
- **Compliance:** GDPR right to erasure, data export, audit requirements
- **Scalability:** Support 100+ tenants without performance degradation
- **Backup/Restore:** Independent tenant data recovery
- **Migration:** Enable tenant offboarding and data portability
- **Performance:** Tenant-specific optimization and resource allocation
- **Cost:** Balance isolation benefits against operational costs
- **Operational Complexity:** Manageable for small team
- **Schema Evolution:** Future ability to customize per tenant

## Considered Options

### Option 1: Database-Per-Tenant (Separate Databases)

**Description:** Each tenant gets a dedicated PostgreSQL database on RDS. All tenant data physically separated with independent credentials, backups, and configurations.

**Pros:**
- ✅ Maximum data isolation (physical separation)
- ✅ No risk of cross-tenant data leakage
- ✅ Independent backups and point-in-time recovery per tenant
- ✅ Easy tenant offboarding (drop database)
- ✅ Tenant-specific performance tuning (indexes, caching)
- ✅ Custom schema extensions per tenant possible
- ✅ Simplified GDPR compliance (right to erasure)
- ✅ Clear audit boundaries
- ✅ Database-level access control
- ✅ Independent scaling per tenant (future: dedicated RDS instance)
- ✅ Easier tenant data export/migration

**Cons:**
- ❌ Higher operational complexity (manage N databases)
- ❌ Database count limits (40 databases per RDS instance default)
- ❌ Schema migration complexity (must update N databases)
- ❌ Connection pool overhead (separate pools per tenant)
- ❌ Monitoring complexity (N databases to watch)
- ❌ Backup storage costs scale linearly with tenants
- ❌ Cross-tenant analytics require federation

**Cost Impact:**
- RDS instance cost: Same (shared instance for multiple DBs)
- Storage: Slightly higher overhead (metadata per database)
- Backups: Linear growth with tenant count
- Estimated: +10-15% over single database approach

**Implementation Effort:** Medium (3-4 weeks)

### Option 2: Schema-Per-Tenant (Shared Database)

**Description:** Single PostgreSQL database with separate schema per tenant. Each tenant's tables live in isolated schema namespace.

**Pros:**
- ✅ Good logical isolation
- ✅ Easier cross-tenant analytics (same database)
- ✅ Single database to manage
- ✅ Simpler connection pooling
- ✅ Easier schema migrations (single database)
- ✅ Lower backup overhead
- ✅ Simpler monitoring

**Cons:**
- ❌ Logical isolation only (not physical)
- ❌ Shared resources (CPU, memory, connections)
- ❌ Risk of noisy neighbor problem
- ❌ More complex application logic (schema switching)
- ❌ Harder tenant offboarding (drop schema + cleanup)
- ❌ Shared backup (cannot restore single tenant independently)
- ❌ PostgreSQL schema limits (practical limit ~1000 schemas)
- ❌ More complex access control (application-level)
- ❌ Potential for SQL injection across schemas

**Cost Impact:**
- Slightly lower infrastructure complexity
- Same RDS instance cost

**Implementation Effort:** Medium (2-3 weeks)

### Option 3: Row-Level Tenant Identifier (Shared Tables)

**Description:** Single database, single schema, all tables have `tenant_id` column. Application filters all queries by tenant_id.

**Pros:**
- ✅ Simplest database structure
- ✅ Easy cross-tenant reporting and analytics
- ✅ Single schema migration
- ✅ Minimal database management overhead
- ✅ Efficient resource utilization
- ✅ Standard ORM patterns (Sequelize supports tenant scoping)

**Cons:**
- ❌ No physical isolation (highest risk)
- ❌ Application bugs can leak data across tenants
- ❌ Complex access control (entirely application-level)
- ❌ Difficult tenant offboarding (delete with tenant_id filter)
- ❌ Risk of missing WHERE tenant_id clause (data leakage)
- ❌ Cannot customize schema per tenant
- ❌ Shared indexes (performance issues at scale)
- ❌ No independent backups
- ❌ GDPR compliance complexity (right to erasure)
- ❌ Audit trail complexity
- ❌ Higher security risk (single point of failure)

**Cost Impact:**
- Lowest infrastructure complexity
- Same RDS instance cost

**Implementation Effort:** Low (1-2 weeks)

### Option 4: Hybrid Approach (Database Pools + Row-Level)

**Description:** Small tenants share databases with row-level isolation, large tenants get dedicated databases.

**Pros:**
- ✅ Balance cost and isolation
- ✅ Premium tier for large tenants
- ✅ Cost-effective for small tenants
- ✅ Flexible architecture

**Cons:**
- ❌ Most complex to implement and maintain
- ❌ Two different code paths (bugs and edge cases)
- ❌ Difficult to promote tenant from shared to dedicated
- ❌ Monitoring complexity
- ❌ Unclear boundary (when to split tenants)

**Cost Impact:**
- Variable based on tenant distribution

**Implementation Effort:** High (6-8 weeks)

## Decision Outcome

**Chosen option:** "Database-Per-Tenant (Separate Databases)" because it provides maximum data isolation, security, and compliance alignment critical for a verifiable credentials platform handling sensitive identity data.

### Expected Positive Consequences

- **Security Confidence:** Physical separation eliminates cross-tenant data leakage
- **Compliance Simplified:** GDPR right to erasure = drop database
- **Independent Recovery:** Restore single tenant without affecting others
- **Performance Isolation:** No noisy neighbor issues
- **Clean Offboarding:** Simple tenant deletion and data export
- **Trust Factor:** "Your data in separate database" is marketing advantage
- **Audit Clarity:** Clear boundaries for security audits
- **Future Flexibility:** Can move large tenants to dedicated RDS instances
- **Regulation Alignment:** Meets strict data residency requirements

### Expected Negative Consequences

- **Operational Complexity:** Must manage multiple databases (automation critical)
- **Schema Migrations:** Need tooling to migrate all tenant databases
- **Connection Overhead:** Separate connection pools per tenant
- **Monitoring Burden:** More databases to monitor for health/performance
- **Cost Scaling:** Backup storage grows linearly with tenants
- **Database Limits:** RDS instance limit of 40 databases (must plan for growth)

### Mitigation Strategies

- **Operational Complexity:**
  - Automate database provisioning via CDK/CloudFormation
  - Create tenant onboarding CLI tool
  - Implement database naming convention: `sybol_tenant_{tenantId}`
  - Use RDS Proxy for connection pooling
  - Document all operational procedures
  
- **Schema Migrations:**
  - Build automated migration runner (iterate all tenant DBs)
  - Implement migration rollback capability
  - Test migrations on staging clone first
  - Use database migration library (Sequelize migrations)
  - Maintain migration version tracking per tenant
  - Run migrations in parallel (faster deployment)
  
- **Connection Pooling:**
  - Use RDS Proxy (managed connection pooling)
  - Lazy connection initialization (connect on first request)
  - Connection pool per tenant with small max size (5 connections)
  - Close idle connections after timeout
  
- **Monitoring:**
  - CloudWatch dashboard aggregating all tenant DBs
  - Automated alerts on performance degradation
  - Weekly database health report (automated script)
  - Use RDS Performance Insights
  
- **Database Limits:**
  - Plan for multiple RDS instances (cluster approach)
  - Monitor database count proactively
  - Design tenant distribution strategy
  - Consider Aurora Serverless v2 for large tenant count

- **Cost Management:**
  - Optimize backup retention (7 days standard, 30 days premium)
  - Use automated lifecycle policies for old snapshots
  - Monitor storage growth per tenant

## Implementation Details

### Required Changes

**Infrastructure (AWS CDK):**
```
infraestructure/CoreInfra/lib/
  rds-multi-tenant-stack.ts      # RDS instance configuration
  rds-proxy-stack.ts              # RDS Proxy for connection pooling
  tenant-database-construct.ts    # Reusable database construct
  
infraestructure/ClientInfra/lib/
  tenant-onboarding-stack.ts      # Automate tenant database creation
```

**Database Naming Convention:**
- Master database: `sybol_master` (tenant registry)
- Tenant databases: `sybol_tenant_{tenantId}` (e.g., `sybol_tenant_acme123`)

**Database Schema:**
Each tenant database contains:
- `credentials` - Issued verifiable credentials
- `users` - Tenant users (Holders, Issuers, Verifiers)
- `organizations` - Organization details
- `audit_logs` - Compliance audit trail
- `vault_entries` - Secure vault data (SVault service)
- `documents` - Document metadata (PAdES service)
- `templates` - Credential templates (Catalog service)

**Migration System:**
```javascript
// services/database/migrate-all-tenants.js
async function migrateAllTenants() {
  const tenants = await getTenantList();
  for (const tenant of tenants) {
    const db = await connectTenantDB(tenant.id);
    await runMigration(db, tenant.id);
  }
}
```

**Connection Management:**
```javascript
// services/common/db-manager.js
class TenantDatabaseManager {
  constructor() {
    this.pools = new Map(); // tenantId -> connection pool
  }
  
  async getConnection(tenantId) {
    if (!this.pools.has(tenantId)) {
      this.pools.set(tenantId, createPool(tenantId));
    }
    return this.pools.get(tenantId);
  }
}
```

**Tenant Provisioning:**
```bash
# infraestructure/ClientInfra/onboard-client.sh
./onboard-client.sh --tenant-id acme123 --tier standard
# Creates:
# - RDS database: sybol_tenant_acme123
# - Database user: acme123_user
# - Initial schema migration
# - Tenant registry entry
```

### Dependencies

- PostgreSQL 15.x on RDS
- RDS Proxy (for connection pooling)
- Sequelize ORM ^6.35.0 (multi-database support)
- `pg` driver ^8.11.0
- Custom migration runner tool

### Backup Strategy

- **Automated Snapshots:** Daily at 3 AM UTC
- **Retention:** 7 days standard, 30 days premium tier
- **Manual Snapshots:** Before major migrations
- **Point-in-Time Recovery:** Enabled (5-minute granularity)
- **Cross-Region Backup:** Critical tenants only (compliance requirement)

### Migration Path

*Not applicable - greenfield implementation*

## Validation

**Success Criteria:**
- ✅ Each tenant has isolated PostgreSQL database
- ✅ Zero cross-tenant data leakage incidents
- ✅ Schema migrations complete successfully across all tenants
- ✅ Independent backup/restore tested and validated
- ✅ Tenant onboarding automated (< 5 minutes)
- ✅ Tenant offboarding clean (no data remnants)
- ✅ Connection pooling efficient (< 100ms connection time)
- ✅ Monitoring covers all tenant databases

**Monitoring:**
- CloudWatch metrics: connections, CPU, storage, IOPS per database
- RDS Performance Insights: slow queries per tenant
- Custom metrics: tenant database count, storage growth rate
- Alerts: high connection count, storage > 80%, failed migrations
- Weekly report: database health, storage usage, backup status

## Related Decisions

- [ADR-0001: AWS Cognito Authentication](0001-aws-cognito-authentication.md) - Cognito tenantId attribute maps to database selection
- [ADR-0002: Serverless Architecture](0002-serverless-architecture.md) - RDS Proxy usage for Lambda connections
- Infrastructure: RDS instance sizing and configuration
- Security: Database encryption at rest (KMS)

## References

- [Multi-Tenant Database Architectures](https://docs.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/storage-data)
- [AWS Multi-Tenant SaaS Storage Strategies](https://docs.aws.amazon.com/whitepapers/latest/saas-storage-strategies/database-per-tenant.html)
- [PostgreSQL Schema Documentation](https://www.postgresql.org/docs/current/ddl-schemas.html)
- [GDPR Right to Erasure Implementation](https://gdpr.eu/right-to-be-forgotten/)
- [RDS Proxy Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-best-practices.html)

## Notes

- **Database Limit:** RDS PostgreSQL supports 40 databases per instance (AWS limit)
- **Future Optimization:** Large tenants may get dedicated RDS instance (Aurora)
- **Analytics:** Cross-tenant analytics via master database aggregation (no direct tenant DB access)
- **Development:** Local development uses single Docker PostgreSQL with multiple databases
- **Testing:** CI/CD creates temporary tenant databases for integration tests

---

**Review Date:** 2025-Q1 (Re-evaluate when reaching 30+ tenants or operational burden increases)  
**Last Updated:** March 10, 2026  
**Status:** In Production since 2024-Q3
