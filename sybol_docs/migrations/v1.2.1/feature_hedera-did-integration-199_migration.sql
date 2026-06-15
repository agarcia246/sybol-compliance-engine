-- =============================================================================
-- Migration: feature/hedera-did-integration-199
-- Version:   v1.2.1
-- Branch:    feature/hedera-did-integration-199
-- Base:      develop
-- Date:      2026-04-21
-- Doc:       docs/migrations/v1.2.1/feature_hedera-did-integration-199_changeLog.md
--
-- Run order:
--   1. \c backoffice      -> paste SECTION 1
--   2. For each tenant DB -> paste SECTION 2
--
-- All statements are idempotent (IF NOT EXISTS / IF EXISTS / ON CONFLICT).
-- Always run inside a transaction. Take an RDS snapshot before executing.
-- =============================================================================


-- =============================================================================
-- SECTION 1 — database: backoffice
-- =============================================================================

\c backoffice

BEGIN;

-- ── entities: add default_did_method ────────────────────────────────────────
-- ADR-HED-007: Default DID method storage

ALTER TABLE entities
    ADD COLUMN IF NOT EXISTS default_did_method CHARACTER VARYING DEFAULT 'did:web';

COMMENT ON COLUMN entities.default_did_method IS
    'Default DID method for this tenant (did:web or did:hedera). Used when issuerKey is not explicitly provided in credential/presentation requests.';

COMMIT;


-- =============================================================================
-- SECTION 2 — per-tenant databases
-- Apply to each tenant DB (e.g. tenant_alsa, tenant_dataie, tenant_repsol,
--                          tenant_solred, tenant_sybol, tenant_tritemius)
--
-- Replace <TENANT_DB> with the actual database name before running.
-- =============================================================================

-- \c <TENANT_DB>

BEGIN;

-- ── hedera_credential_anchors ───────────────────────────────────────────────
-- ADR-HED-005: Topic per credential, SHA-256 hash anchoring
-- Stores the association between credentials and their HCS topic anchors

CREATE TABLE IF NOT EXISTS hedera_credential_anchors (
    credential_jti      UUID                     PRIMARY KEY,
    topic_id            TEXT                     NOT NULL,
    hash                TEXT                     NOT NULL,
    network             TEXT                     NOT NULL DEFAULT 'testnet',
    sequence_number     BIGINT,
    consensus_timestamp TIMESTAMP WITH TIME ZONE,
    published_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hedera_credential_anchors_topic
    ON hedera_credential_anchors (topic_id);

-- ── tenant_settings ─────────────────────────────────────────────────────────
-- Per-tenant key-value settings table.
-- Replaces the default_did_method column previously stored in the shared
-- backoffice entities table — tenant settings belong in the tenant DB so
-- that the tenant role has full read/write access without touching shared
-- platform tables.

CREATE TABLE IF NOT EXISTS tenant_settings (
    key        TEXT        PRIMARY KEY,
    value      TEXT        NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed with the default DID method (did:web) so GET /api/bl/settings
-- always returns a complete configuration even before the user changes it.
INSERT INTO tenant_settings (key, value)
VALUES ('default_did_method', 'did:web')
ON CONFLICT DO NOTHING;

COMMIT;
