# Migration — Staging → v1.2.0

**Date:** 2026-04-13  
**Target environment:** staging (`sybol-staging.cbw24k06qybn.eu-west-1.rds.amazonaws.com`)  
**Migration script:** `database/migrations/staging/milestone_v1.2.0.sql`  
**Branch:** `feature/eddera-poc`

---

## Context

A differential schema analysis between the dev (`sybol-backoffice`) and staging (`sybol-staging`) RDS instances identified that staging is 1–2 development cycles behind dev across all three database groups: `backoffice`, `catalog`, and per-tenant wallet databases.

This migration brings staging up to the same structural level as dev.

---

## Scope

### 1. `backoffice` database

New tables (no data risk — purely additive):

| Table | Purpose |
|---|---|
| `bm_contracts` | Blockchain Manager contract registry (chain_id, address, ABI) |
| `entities` | Tenant entity metadata (business name, CIF) |
| `kyb_verifications` | Know-Your-Business verification records (Sumsub integration) |
| `referrals` | User referral tracking |
| `smart_contracts` | Smart contract instances (supersedes bm_contracts in new services) |
| `users` | Platform user registry (Cognito id, email, role, onboarding state) |

---

### 2. `catalog` database

#### Additive column changes (safe)

**`documents`** — 11 new columns:

| Column | Type | Purpose |
|---|---|---|
| `standards` | jsonb | Referenced standards (ISO, eIDAS…) |
| `version` | character varying | Document schema version |
| `vc_type` | jsonb | VC `@type` array for W3C serialization |
| `context` | jsonb | VC `@context` array |
| `schema_url` | character varying | JSON Schema URL for credential validation |
| `compliance_regions` | jsonb | Applicable compliance regions |
| `issuer_requirements` | jsonb | Constraints on who may issue this document |
| `revocation` | jsonb | Revocation configuration (StatusList2021 etc.) |
| `expiry_policy` | jsonb | Default expiry rules |
| `selective_disclosure` | boolean | SD-JWT enabled flag |
| `display` | jsonb | Visual display metadata |

**`claims`** — 8 new columns:

| Column | Type | Purpose |
|---|---|---|
| `semantic_id` | character varying | Semantic URI for the claim |
| `path` | character varying | JSONPath location in the VC payload |
| `constraints` | jsonb | Validation constraints |
| `regex_flags` | character varying | Flags for regex_pattern |
| `essential` | boolean | Claim is mandatory for VP |
| `selective_disclosure_policy` | character varying | SD disclosure policy |
| `source_type` | character varying | Data source type |
| `display` | jsonb | Visual display metadata |

**`forms`** — 6 new columns:

| Column | Type | Purpose |
|---|---|---|
| `version` | character varying | Form schema version |
| `purpose` | text | Human-readable purpose |
| `credential_requirements` | jsonb | Which credentials the holder must present |
| `format_preferences` | jsonb | Preferred VC format (jwt_vc, ldp_vc…) |
| `response_expiry_seconds` | integer | Response window |
| `compliance_regions` | jsonb | Applicable compliance regions |

---

#### Destructive column change — `form_sections` ⚠️

**Risk: DATA MIGRATION REQUIRED**

Staging has real data in plain-text columns that dev has replaced with i18n-structured JSON:

| Staging (current) | Dev (target) | Action |
|---|---|---|
| `title character varying` | *(removed)* | Migrate → `translations` jsonb, then DROP |
| `description text` | *(removed)* | Migrate → `translations` jsonb, then DROP |
| *(absent)* | `translations jsonb` | ADD with default language `es` |

6 rows in staging have non-null title/description. The migration reads those values, serializes them to `{"es": "<value>", "en": "<value>"}` (using the Spanish text for both until manual translation is provided), creates the `translations` column, then drops the old columns.

**Dependent views:** The views `forms_with_schema` and `form_documents_relation` reference `form_sections` columns. The migration script drops both views **before** altering columns, then recreates them with the v2 definitions (matching `services/catalog/database/schema.sql`) after all column changes are complete.

---

#### Structural column rename — `form_fields` ⚠️

**Risk: LOW — columns are currently empty in staging (31 rows, all NULL)**

| Staging (current) | Dev (target) | Action |
|---|---|---|
| `label_override character varying` | `label_override_translations jsonb` | DROP + ADD (data empty) |
| `help_text text` | `help_text_translations jsonb` | DROP + ADD (data empty) |

Additionally, dev adds these new columns to `form_fields`:

| Column | Type |
|---|---|
| `or_group_index` | integer |
| `origin_reference` | character varying |
| `widget_ui` | character varying |
| `constraints_override` | jsonb |
| `sort_order` | integer |
| `label_override_translations` | jsonb |
| `help_text_translations` | jsonb |

---

### 3. Per-tenant wallet databases (`tenant_*`)

The same schema change must be applied to all 6 staging tenant databases:  
`tenant_alsa`, `tenant_dataie`, `tenant_repsol`, `tenant_solred`, `tenant_sybol`, `tenant_tritemius`

#### New tables (additive):

| Table | Purpose |
|---|---|
| `batch_processes` | Bulk credential issuance process tracking |
| `batch_credential_intents` | Individual rows within a batch process |
| `batch_process_log` | Row-level log for batch processing |
| `bm_chains` | Blockchain chain registry |
| `bm_signers` | KMS-backed blockchain signing keys |
| `bm_nonces` | Nonce management per chain/signer |
| `bm_transactions` | Blockchain transaction log |
| `bm_event_subscriptions` | Smart contract event subscription config |
| `hedera_identities` | Hedera DID registry per tenant |
| `evidence_url_traces` | Audit trail for credential evidence URLs |

#### Column additions on existing tables:

| Table | Column | Type | Default |
|---|---|---|---|
| `alerts` | `updated_at` | timestamp with time zone | `NOW()` |
| `presentations` | `delegations` | jsonb | `NULL` |
| `credentials` | `evidence_url` | character varying | `NULL` |

---

## 4. AWS Infrastructure — KMS Lambdas (staging)

**Date applied:** 2026-04-14  
**Status:** Done ✅

### Lambda environment variables

All 4 KMS staging Lambdas were deployed without the `AWS_ACCOUNT_ID` environment variable, which the code requires to construct IAM role ARNs for tenant isolation via STS AssumeRole.

| Lambda | Variable | Value |
|---|---|---|
| `sybol-kms-key-ed25519-staging` | `AWS_ACCOUNT_ID` | `111891094335` |
| `sybol-kms-key-p256-staging` | `AWS_ACCOUNT_ID` | `111891094335` |
| `sybol-kms-key-rsa-staging` | `AWS_ACCOUNT_ID` | `111891094335` |
| `sybol-kms-key-secp256k1-staging` | `AWS_ACCOUNT_ID` | `111891094335` |

### IAM — TenantKmsRole per tenant

Each tenant requires a dedicated IAM role (`TenantKmsRole-{tenantId}`) that scopes KMS operations to keys tagged with that tenant's ID. This is the primary isolation mechanism (defense-in-depth: IAM-level enforcement independent of application code).

| Role | Action | Status |
|---|---|---|
| `TenantKmsRole-repsol` | Updated trust policy (added `sybol-kms-lambda-staging-role`) | ✅ |
| `TenantKmsRole-sybol` | Updated trust policy (added `sybol-kms-lambda-staging-role`) | ✅ |
| `TenantKmsRole-alsa` | Created with trust + tenant-scoped policy | ✅ |
| `TenantKmsRole-dataie` | Created with trust + tenant-scoped policy | ✅ |
| `TenantKmsRole-solred` | Created with trust + tenant-scoped policy | ✅ |
| `TenantKmsRole-tritemius` | Created with trust + tenant-scoped policy | ✅ |

Each role's `TenantKmsPermissions` inline policy enforces:
- `kms:CreateKey` — only if `aws:RequestTag/tenantId` matches the tenant
- `kms:DescribeKey`, `GetPublicKey`, `DisableKey`, `ListResourceTags`, `TagResource` — only if `aws:ResourceTag/tenantId` matches
- `tag:GetResources` — unrestricted (used for listing keys by tag)

Trust policy: both `sybol-kms-lambda-dev-role` and `sybol-kms-lambda-staging-role`.

### IAM — Lambda execution role fix

The staging Lambda execution role (`sybol-kms-lambda-staging-role`) was missing the `sts:AssumeRole` permission needed to assume tenant roles. The dev role had it (`AllowAssumeTenantKmsRoles-dev`), but staging didn't.

| Role | Policy added | Resource |
|---|---|---|
| `sybol-kms-lambda-staging-role` | `AllowAssumeTenantKmsRoles-staging` | `arn:aws:iam::111891094335:role/TenantKmsRole-*` |

### IAM — TenantRole KMS signing fix

The `TenantRole-{tenant}-stagingadmin` roles used by the businessLogic Lambda for JWT signing had an incorrect KMS resource pattern. The policy allowed `kms:Sign` on `arn:aws:kms:...:tenant/{tenant}/stagingadmin-*` which doesn't match actual KMS key ARNs (`key/{uuid}`).

Updated to use tag-based isolation (same pattern as TenantKmsRole):

| Role | Old Resource | New Resource + Condition |
|---|---|---|
| `TenantRole-alsa-stagingadmin` | `tenant/alsa/stagingadmin-*` | `key/*` + `aws:ResourceTag/tenantId = alsa` |
| `TenantRole-dataie-stagingadmin` | `tenant/dataie/stagingadmin-*` | `key/*` + `aws:ResourceTag/tenantId = dataie` |
| `TenantRole-repsol-stagingadmin` | `tenant/repsol/stagingadmin-*` | `key/*` + `aws:ResourceTag/tenantId = repsol` |
| `TenantRole-solred-stagingadmin` | `tenant/solred/stagingadmin-*` | `key/*` + `aws:ResourceTag/tenantId = solred` |
| `TenantRole-sybol-stagingadmin` | `tenant/sybol/stagingadmin-*` | `key/*` + `aws:ResourceTag/tenantId = sybol` |
| `TenantRole-tritemius-stagingadmin` | `tenant/tritemius/stagingadmin-*` | `key/*` + `aws:ResourceTag/tenantId = tritemius` |

Actions allowed: `kms:Sign`, `kms:GetPublicKey`, `kms:DescribeKey` — only on keys tagged with the tenant's own `tenantId`.

**Tenant isolation preserved:** each role can only sign with keys tagged as belonging to its own tenant. AWS IAM evaluates the `aws:ResourceTag/tenantId` condition at request time, blocking cross-tenant access independently of application code.

### Lambda permission — POST /api/bo/email

Added missing Lambda resource-based policy for API Gateway route `POST /api/bo/email` (same pattern as the `/api/bo/did-document` fix).

| Lambda | Statement | Source ARN |
|---|---|---|
| `backoffice-staging` | `apigw-bo-email-post` | `gnholtnwob/*/POST/api/bo/email` |

---

## Troubleshooting — Issues encountered during migration

### 1. Table permissions on new tenant tables

**Symptom:** `GET /api/bl/hedera/did-status` → 500 `"permission denied for table hedera_identities"`  
**Cause:** The 10 new tables in tenant DBs were created by `postgres` (superuser). The Lambda DB users (`{tenant}_stagingadmin`, `propagate_system`) had no grants on them.  
**Fix:** `GRANT SELECT, INSERT, UPDATE, DELETE ON <new_tables> TO {tenant_role}` + `GRANT USAGE, SELECT ON ALL SEQUENCES` for all 6 tenant DBs.

### 2. Entities table empty — missing seed data

**Symptom:** `GET /api/bo/entities/repsol` → 404  
**Cause:** The migration created `backoffice.entities` table (`CREATE TABLE IF NOT EXISTS`) but did not insert seed data. Entity data only existed inside `did_documents.entity` (JSONB column), not in the standalone `entities` table.  
**Fix:**
```sql
INSERT INTO entities (tenant, business_name, cif) VALUES
  ('alsa', 'Ajuntament de Castello', 'B82059478'),
  ('dataie', 'Facsa S.A.', 'A12000022'),
  ('repsol', 'Repsol S.A.', 'A78374725'),
  ('solred', 'SOLRED S.A.', 'A79707345'),
  ('sybol', 'Sybol', 'B19886555'),
  ('tritemius', 'Tritemius Labs S.L.', 'B75989566');
```

### 3. DID migration did:sybol → did:web

**Symptom:** Multiple 500/409 errors on contacts, presentations, credential operations.  
**Cause:** Staging used `did:sybol:{uuid}` format while the codebase had migrated to `did:web:{domain}:tenants:{tenant}`. The code's `isValidDidFormat()` and `didWebResolver` only accept `did:web`.  
**Fix:** Full DID migration — see section 5 (DID Migration).  
**Note:** This required cleaning all tenant DB data (contacts, credentials, presentations, etc.) and regenerating DID documents with new P256 KMS keys.

### 4. KMS signing — TenantRole resource mismatch

**Symptom:** `POST /api/bl/presentation-requests` → 500 `"Access denied to KMS key"`  
**Cause:** `TenantRole-{tenant}-stagingadmin` had `kms:Sign` permission but with wrong resource pattern (`tenant/{tenant}/stagingadmin-*` instead of `key/*`). The pattern expected KMS aliases that don't exist; actual keys have ARN `key/{uuid}`.  
**Fix:** Updated all 6 roles to use `Resource: key/*` with `Condition: aws:ResourceTag/tenantId = {tenant}` for tag-based isolation.

### 5. Lambda permissions — specific API Gateway routes

**Symptom:** `POST /api/bo/email` and `GET /api/bo/did-document` → 500 `{"message":"Internal Server Error"}` (API GW default).  
**Cause:** API Gateway HTTP API specific routes (`POST /api/bo/email`, `GET /api/bo/did-document`) need their own Lambda invoke permission. The catch-all `{proxy+}` permission does NOT cover routes with explicit path definitions.  
**Fix:** Added `lambda:InvokeFunction` permissions for each specific route via `aws lambda add-permission`.

### 6. Missing column — credentials.evidence_url

**Symptom:** `POST /api/bl/credentials/:id` (update with evidence_url) → 500 `"column \"evidence_url\" of relation \"credentials\" does not exist"`  
**Cause:** The `evidence_url` column on `credentials` was present in dev but missing from the migration script. It was not caught in the original differential analysis.  
**Fix:** `ALTER TABLE credentials ADD COLUMN IF NOT EXISTS evidence_url CHARACTER VARYING;` applied to all 6 tenant DBs. Migration script and docs updated.

### 8. Duplicate did:web resolver Lambda (DEV only — inconsistent with staging)

**Date applied:** 2026-04-16 (DEV only)
**Status:** ⚠️ Inconsistent between environments — see disclaimer below

**Symptom:** During the staging migration (step 3 — DID migration), a standalone Lambda `sybol-did-resolver-staging` was created to serve `GET /tenants/{tenant}/did.json` per the did:web spec. The same pattern was applied in DEV (`sybol-did-resolver-dev`).

**Issue identified later:** The backoffice service already implemented this endpoint at `services/backoffice/src/app.js:47` → `didDocumentController.getPublicDidDocument()` (returns raw DID document, sets CORS, matches did:web spec). The dedicated Lambdas were unnecessary duplication.

**Fix (DEV only):**
- Updated API Gateway route `GET /tenants/{tenant}/did.json` on `13xxajdiae` to point to integration `i55hazm` (backoffice-api Lambda) instead of the standalone resolver
- Added Lambda permission `apigw-tenants-did-json-get` to `backoffice-api`
- Deleted Lambda `sybol-did-resolver-dev`
- Removed `lambdas/did-web-resolver/` directory from the repo

**⚠️ DISCLAIMER — ENVIRONMENT INCONSISTENCY**

This change was applied **only in DEV**. Staging **still runs the dedicated Lambda** `sybol-did-resolver-staging` with the old architecture:
- Staging API GW `gnholtnwob`: route `GET /tenants/{tenant}/did.json` → integration `yh91ir6` → `sybol-did-resolver-staging` Lambda
- DEV API GW `13xxajdiae`: route `GET /tenants/{tenant}/did.json` → integration `i55hazm` → `backoffice-api` Lambda

**TODO — either:**
- (a) **Align staging with DEV** — update staging API GW to route to backoffice-staging and delete `sybol-did-resolver-staging` Lambda, OR
- (b) **Revert DEV to match staging** — re-create the Lambda and repo source and point DEV route back

Both environments expose the endpoint correctly to external resolvers (raw DID document, CORS, unauthenticated), but the underlying implementation differs. This should be aligned before the next production deployment.

---

## Rollback Plan

- All new tables: `DROP TABLE IF EXISTS <table>` — no data loss risk since they are new.
- `catalog.form_sections` → restore `title`/`description` from backup taken before migration. The `translations` column is dropped.
- `catalog.form_fields` → restore `label_override`/`help_text` column names. Safe since data was empty.
- New columns on existing tables: `ALTER TABLE ... DROP COLUMN IF EXISTS <col>` — no data loss since they were added with defaults.

---

## Pre-flight Checklist

- [ ] Take a manual snapshot of `sybol-staging` before running the script
- [ ] Verify staging is not serving live traffic during migration window
- [ ] Run script in a transaction: if any statement fails, roll back
- [ ] Confirm 6 form_sections rows are preserved after migration (check translations column)
- [ ] Confirm 31 form_fields rows still present after column rename

---

## Tenants affected

| Environment | Tenants |
|---|---|
| staging | alsa, dataie, repsol, solred, sybol, tritemius |
