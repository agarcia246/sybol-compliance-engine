-- =============================================================================
-- Migration: Staging → v1.2.0
-- Target:    sybol-staging (eu-west-1)
-- Date:      2026-04-13
-- Doc:       docs/migrations/milestone_v.1.2.0.md
--
-- Run order:
--   1. \c backoffice      → paste SECTION 1
--   2. \c catalog         → paste SECTION 2
--   3. For each tenant DB → paste SECTION 3
--
-- Always run inside a transaction. Take an RDS snapshot before executing.
-- =============================================================================


-- =============================================================================
-- SECTION 1 — database: backoffice
-- =============================================================================

\c backoffice

BEGIN;

-- ── bm_contracts ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bm_contracts (
    contract_ref TEXT        NOT NULL,
    chain_id     INTEGER     NOT NULL,
    address      TEXT        NOT NULL,
    abi          JSONB,
    version      INTEGER,
    PRIMARY KEY (contract_ref, chain_id)
);

-- ── entities ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS entities (
    tenant        TEXT                     NOT NULL PRIMARY KEY,
    business_name TEXT,
    cif           TEXT,
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── kyb_verifications ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS kyb_verifications (
    id            UUID                     PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email    CHARACTER VARYING,
    user_name     CHARACTER VARYING,
    tenant        CHARACTER VARYING,
    applicant_id  CHARACTER VARYING,
    status        CHARACTER VARYING,
    level_name    CHARACTER VARYING,
    sumsub_data   JSONB,
    created_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- ── referrals ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS referrals (
    id            UUID                     PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       CHARACTER VARYING        NOT NULL,
    referenced_by CHARACTER VARYING,
    created_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- ── smart_contracts ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS smart_contracts (
    id            UUID                     PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_ref  CHARACTER VARYING        NOT NULL,
    chain_id      INTEGER                  NOT NULL,
    address       CHARACTER VARYING        NOT NULL,
    abi           JSONB,
    created_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

COMMIT;


-- =============================================================================
-- SECTION 2 — database: catalog
-- =============================================================================

\c catalog

BEGIN;

-- ── documents: new columns ───────────────────────────────────────────────────
ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS standards              JSONB,
    ADD COLUMN IF NOT EXISTS version               CHARACTER VARYING,
    ADD COLUMN IF NOT EXISTS vc_type               JSONB,
    ADD COLUMN IF NOT EXISTS context               JSONB,
    ADD COLUMN IF NOT EXISTS schema_url            CHARACTER VARYING,
    ADD COLUMN IF NOT EXISTS compliance_regions    JSONB,
    ADD COLUMN IF NOT EXISTS issuer_requirements   JSONB,
    ADD COLUMN IF NOT EXISTS revocation            JSONB,
    ADD COLUMN IF NOT EXISTS expiry_policy         JSONB,
    ADD COLUMN IF NOT EXISTS selective_disclosure  BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS display               JSONB;

-- ── claims: new columns ──────────────────────────────────────────────────────
ALTER TABLE claims
    ADD COLUMN IF NOT EXISTS semantic_id                  CHARACTER VARYING,
    ADD COLUMN IF NOT EXISTS path                         CHARACTER VARYING,
    ADD COLUMN IF NOT EXISTS constraints                  JSONB,
    ADD COLUMN IF NOT EXISTS regex_flags                  CHARACTER VARYING,
    ADD COLUMN IF NOT EXISTS essential                    BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS selective_disclosure_policy  CHARACTER VARYING,
    ADD COLUMN IF NOT EXISTS source_type                  CHARACTER VARYING,
    ADD COLUMN IF NOT EXISTS display                      JSONB;

-- ── forms: new columns ───────────────────────────────────────────────────────
ALTER TABLE forms
    ADD COLUMN IF NOT EXISTS version                  CHARACTER VARYING,
    ADD COLUMN IF NOT EXISTS purpose                  TEXT,
    ADD COLUMN IF NOT EXISTS credential_requirements  JSONB,
    ADD COLUMN IF NOT EXISTS format_preferences       JSONB,
    ADD COLUMN IF NOT EXISTS response_expiry_seconds  INTEGER,
    ADD COLUMN IF NOT EXISTS compliance_regions       JSONB;

-- ── form_sections: data migration (title/description → translations jsonb) ───
--
-- Existing rows have real data in title and description (plain text, es locale).
-- We serialize them to {"es": "<value>", "en": "<value>"} using the Spanish
-- text as placeholder for English until manual translation is provided.
--
-- Steps:
--   1. Add translations column
--   2. Populate from existing title/description
--   3. Drop dependent views (forms_with_schema, form_documents_relation)
--   4. Drop old columns
--   5. Recreate views with v2 definitions (end of section)

ALTER TABLE form_sections
    ADD COLUMN IF NOT EXISTS translations JSONB;

UPDATE form_sections
SET translations = jsonb_build_object(
    'es', jsonb_build_object(
        'title',       COALESCE(title, ''),
        'description', COALESCE(description, '')
    ),
    'en', jsonb_build_object(
        'title',       COALESCE(title, ''),
        'description', COALESCE(description, '')
    )
)
WHERE translations IS NULL;

-- ── catalog views: drop before column removal ────────────────────────────────
--
-- forms_with_schema references fs.title, fs.description (form_sections) and
-- ff.label_override, ff.help_text (form_fields), all being dropped below.
-- form_documents_relation references new columns (c.semantic_id, d.vc_type,
-- d.compliance_regions) that don't exist yet.
-- Both are recreated after all schema changes using the exact schema.sql definition.

DROP VIEW IF EXISTS forms_with_schema;
DROP VIEW IF EXISTS form_documents_relation;

ALTER TABLE form_sections
    DROP COLUMN IF EXISTS title,
    DROP COLUMN IF EXISTS description;

-- ── form_fields: rename label_override/help_text → *_translations jsonb ──────
--
-- Current staging data: all 31 rows have NULL/empty in both columns → safe.
-- We drop the old varchar columns and add the jsonb equivalents,
-- then add the remaining new columns present in dev.

ALTER TABLE form_fields
    DROP COLUMN IF EXISTS label_override,
    DROP COLUMN IF EXISTS help_text;

ALTER TABLE form_fields
    ADD COLUMN IF NOT EXISTS label_override_translations  JSONB,
    ADD COLUMN IF NOT EXISTS help_text_translations       JSONB,
    ADD COLUMN IF NOT EXISTS or_group_index               INTEGER,
    ADD COLUMN IF NOT EXISTS origin_reference             CHARACTER VARYING,
    ADD COLUMN IF NOT EXISTS widget_ui                    CHARACTER VARYING,
    ADD COLUMN IF NOT EXISTS constraints_override         JSONB,
    ADD COLUMN IF NOT EXISTS sort_order                   INTEGER;

-- ── catalog views: recreate from exact schema.sql definitions ────────────────

CREATE OR REPLACE VIEW forms_with_schema AS
SELECT
    f.*,
    COALESCE(
        json_agg(
            json_build_object(
                'id',           fs.id,
                'translations', fs.translations,
                'sort_order',   fs.sort_order,
                'fields', (
                    SELECT json_agg(
                        json_build_object(
                            'id',                          ff.id,
                            'claim_id',                    ff.claim_id,
                            'claim_key',                   c.key,
                            'claim_translations',          c.translations,
                            'claim_default_lang_code',     c.default_lang_code,
                            'claim_semantic_id',           c.semantic_id,
                            'claim_data_type',             c.data_type,
                            'claim_constraints',           c.constraints,
                            'claim_display',               c.display,
                            'label_override_translations', ff.label_override_translations,
                            'help_text_translations',      ff.help_text_translations,
                            'required',                    ff.required,
                            'or_group_index',              ff.or_group_index,
                            'origin_reference',            ff.origin_reference,
                            'sort_order',                  ff.sort_order,
                            'regex_pattern',               c.regex_pattern,
                            'widget_ui',                   ff.widget_ui
                        ) ORDER BY ff.sort_order
                    )
                    FROM form_fields ff
                    LEFT JOIN claims c ON ff.claim_id = c.id
                    WHERE ff.section_id = fs.id
                )
            ) ORDER BY fs.sort_order
        ) FILTER (WHERE fs.id IS NOT NULL),
        '[]'::json
    ) AS sections
FROM forms f
LEFT JOIN form_sections fs ON f.id = fs.form_id
GROUP BY f.id;

CREATE OR REPLACE VIEW form_documents_relation AS
SELECT
    f.id                                AS form_id,
    f.code                              AS form_code,
    f.translations                      AS form_translations,
    f.default_lang_code                 AS form_default_lang_code,
    f.state                             AS form_state,
    d.id                                AS document_id,
    d.code                              AS document_code,
    d.vc_type                           AS document_vc_type,
    d.translations                      AS document_translations,
    d.default_lang_code                 AS document_default_lang_code,
    d.compliance_path,
    d.compliance_regions                AS document_compliance_regions,
    d.state                             AS document_state,
    COUNT(DISTINCT ff.id)               AS fields_count,
    COUNT(DISTINCT c.id)                AS claims_count,
    json_agg(DISTINCT jsonb_build_object(
        'key',              c.key,
        'semantic_id',      c.semantic_id,
        'translations',     c.translations,
        'default_lang_code',c.default_lang_code,
        'data_type',        c.data_type,
        'essential',        c.essential
    ) ORDER BY jsonb_build_object(
        'key',              c.key,
        'semantic_id',      c.semantic_id,
        'translations',     c.translations,
        'default_lang_code',c.default_lang_code,
        'data_type',        c.data_type,
        'essential',        c.essential
    )) AS claims
FROM forms f
JOIN form_fields ff ON f.id = ff.form_id
JOIN claims c ON ff.claim_id = c.id
JOIN documents d ON c.document_id = d.id
GROUP BY f.id, f.code, f.translations, f.default_lang_code, f.state,
         d.id, d.code, d.vc_type, d.translations, d.default_lang_code,
         d.compliance_path, d.compliance_regions, d.state;

COMMIT;


-- =============================================================================
-- SECTION 3 — per-tenant databases
-- Apply to each of: tenant_alsa, tenant_dataie, tenant_repsol,
--                   tenant_solred, tenant_sybol, tenant_tritemius
--
-- Replace <TENANT_DB> with the actual database name before running.
-- =============================================================================

-- \c <TENANT_DB>

BEGIN;

-- ── alerts: add updated_at ───────────────────────────────────────────────────
ALTER TABLE alerts
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- ── presentations: add delegations ───────────────────────────────────────────
ALTER TABLE presentations
    ADD COLUMN IF NOT EXISTS delegations JSONB;

-- ── credentials: add evidence_url ───────────────────────────────────────────
ALTER TABLE credentials
    ADD COLUMN IF NOT EXISTS evidence_url CHARACTER VARYING;

-- ── batch_processes ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS batch_processes (
    id                UUID                     PRIMARY KEY DEFAULT gen_random_uuid(),
    status            CHARACTER VARYING        NOT NULL DEFAULT 'pending',
    total_rows        INTEGER,
    processed_rows    INTEGER                  DEFAULT 0,
    failed_rows       INTEGER                  DEFAULT 0,
    s3_key            CHARACTER VARYING,
    issuer_key        CHARACTER VARYING,
    initiated_by      CHARACTER VARYING,
    original_filename TEXT,
    error_reason      TEXT,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── batch_credential_intents ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS batch_credential_intents (
    id               UUID                     PRIMARY KEY DEFAULT gen_random_uuid(),
    process_id       UUID                     NOT NULL REFERENCES batch_processes(id) ON DELETE CASCADE,
    row_index        INTEGER                  NOT NULL,
    document_id      CHARACTER VARYING,
    issuer_key       CHARACTER VARYING,
    recipient_did    CHARACTER VARYING,
    claims           JSONB,
    valid_from       TIMESTAMP WITH TIME ZONE,
    expiration_date  TIMESTAMP WITH TIME ZONE,
    status           CHARACTER VARYING        DEFAULT 'pending',
    credential_jti   UUID,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── batch_process_log ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS batch_process_log (
    id         SERIAL                   PRIMARY KEY,
    process_id UUID                     NOT NULL,
    row_index  INTEGER,
    status     CHARACTER VARYING,
    row_data   JSONB,
    error_msg  TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── bm_chains ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bm_chains (
    chain_id             INTEGER PRIMARY KEY,
    name                 TEXT    NOT NULL,
    native_currency      TEXT,
    block_time_ms        INTEGER,
    eip1559              BOOLEAN DEFAULT FALSE,
    confirmation_blocks  INTEGER DEFAULT 1,
    explorer_url         TEXT,
    rpc_primary          TEXT,
    rpc_fallback_ref     TEXT,
    critical             BOOLEAN DEFAULT FALSE
);

-- ── bm_signers ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bm_signers (
    signer_ref  TEXT    NOT NULL PRIMARY KEY,
    tenant_id   TEXT    NOT NULL,
    kms_key_id  TEXT,
    address     TEXT,
    chain_ids   TEXT[], -- stored as array of chain_id strings
    is_default  BOOLEAN DEFAULT FALSE
);

-- ── bm_nonces ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bm_nonces (
    chain_id    INTEGER NOT NULL,
    signer_ref  TEXT    NOT NULL,
    next_nonce  BIGINT  NOT NULL DEFAULT 0,
    PRIMARY KEY (chain_id, signer_ref)
);

-- ── bm_transactions ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bm_transactions (
    tx_hash       TEXT                     NOT NULL PRIMARY KEY,
    chain_id      INTEGER                  NOT NULL,
    nonce         BIGINT,
    signer_ref    TEXT,
    status        TEXT                     DEFAULT 'pending',
    gas_bump_count INTEGER                 DEFAULT 0,
    submitted_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confirmed_at  TIMESTAMP WITH TIME ZONE,
    receipt_json  TEXT
);

-- ── bm_event_subscriptions ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bm_event_subscriptions (
    subscription_id  UUID                     PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id        TEXT                     NOT NULL,
    chain_id         INTEGER                  NOT NULL,
    contract_ref     TEXT                     NOT NULL,
    event_name       TEXT                     NOT NULL,
    start_block      BIGINT,
    current_cursor   BIGINT,
    active           BOOLEAN                  DEFAULT TRUE,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ── hedera_identities ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hedera_identities (
    id         SERIAL  PRIMARY KEY,
    tenant_id  TEXT    NOT NULL,
    did        TEXT    NOT NULL UNIQUE,
    topic_id   TEXT    NOT NULL,
    kms_key_id TEXT,
    network    TEXT    NOT NULL DEFAULT 'testnet',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hedera_identities_tenant_id
    ON hedera_identities (tenant_id);

-- ── evidence_url_traces ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS evidence_url_traces (
    id              UUID                     PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_jti  UUID                     NOT NULL,
    evidence_url    CHARACTER VARYING,
    state           CHARACTER VARYING,
    updated_by      CHARACTER VARYING,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMIT;
