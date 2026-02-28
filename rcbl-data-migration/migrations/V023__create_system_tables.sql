-- System / operational tables:
--   • system_metrics        — time-series operational metrics
--   • backup_history        — track backup runs
--   • data_retention_policies — GDPR retention configuration
--   • personal_data_fields  — GDPR personal data inventory
--   • api_rate_limits       — per-company rate-limit tracking
--   • system_health view    — quick operational health check


-- ── system_metrics ───────────────────────────────────────────────────────────

CREATE TABLE system_metrics (
    id           UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name  VARCHAR(100)  NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    metric_unit  VARCHAR(50),
    company_id   UUID          REFERENCES companies(id) ON DELETE CASCADE,
    recorded_at  TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_metrics_name_date ON system_metrics(metric_name, recorded_at);
CREATE INDEX idx_system_metrics_company   ON system_metrics(company_id, recorded_at);


-- ── backup_history ───────────────────────────────────────────────────────────

CREATE TABLE backup_history (
    id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    backup_type        VARCHAR(20) CHECK (backup_type IN ('full', 'incremental', 'differential')),
    backup_location    TEXT        NOT NULL,
    backup_size_bytes  BIGINT,
    started_at         TIMESTAMPTZ NOT NULL,
    completed_at       TIMESTAMPTZ,
    status             VARCHAR(20) CHECK (status IN ('running', 'completed', 'failed')),
    error_message      TEXT
);


-- ── data_retention_policies (GDPR) ───────────────────────────────────────────

CREATE TABLE data_retention_policies (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name      VARCHAR(100) NOT NULL UNIQUE,
    retention_days  INTEGER     NOT NULL,
    deletion_logic  TEXT        NOT NULL,   -- SQL statement executed by the cleanup job
    last_cleanup_at TIMESTAMPTZ,
    enabled         BOOLEAN     NOT NULL DEFAULT true
);

-- Seed retention policies
INSERT INTO data_retention_policies (table_name, retention_days, deletion_logic) VALUES
    ('reminder_events',  730, 'DELETE FROM reminder_events WHERE sent_at < NOW() - INTERVAL ''730 days'''),
    ('sync_logs',        365, 'DELETE FROM sync_logs WHERE created_at < NOW() - INTERVAL ''365 days'''),
    ('webhook_events',   180, 'DELETE FROM webhook_events WHERE received_at < NOW() - INTERVAL ''180 days'''),
    ('audit_logs',      2190, 'DELETE FROM audit_logs WHERE changed_at < NOW() - INTERVAL ''2190 days'''),  -- 6 years
    ('system_metrics',   365, 'DELETE FROM system_metrics WHERE recorded_at < NOW() - INTERVAL ''365 days''');


-- ── personal_data_fields (GDPR inventory) ───────────────────────────────────

CREATE TABLE personal_data_fields (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name        VARCHAR(100) NOT NULL,
    column_name       VARCHAR(100) NOT NULL,
    data_category     VARCHAR(50) CHECK (data_category IN ('PII', 'Financial', 'Contact', 'Behavioral')),
    requires_consent  BOOLEAN     NOT NULL DEFAULT false,
    can_be_exported   BOOLEAN     NOT NULL DEFAULT true,
    can_be_deleted    BOOLEAN     NOT NULL DEFAULT true,

    CONSTRAINT unique_field UNIQUE (table_name, column_name)
);

-- Seed the PII inventory
INSERT INTO personal_data_fields (table_name, column_name, data_category, requires_consent, can_be_exported, can_be_deleted) VALUES
    ('users',      'email',          'PII',       false, true, true),
    ('users',      'name',           'PII',       false, true, true),
    ('customers',  'name',           'PII',       false, true, true),
    ('customers',  'email',          'PII',       false, true, true),
    ('customers',  'contact_person', 'PII',       false, true, true),
    ('invoices',   'amount',         'Financial', false, true, false),
    ('payments',   'amount',         'Financial', false, true, false);


-- ── api_rate_limits ───────────────────────────────────────────────────────────
-- Used as a fallback DB-level rate-limit store; Redis is the primary store.

CREATE TABLE api_rate_limits (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID         REFERENCES companies(id) ON DELETE CASCADE,
    endpoint        VARCHAR(200) NOT NULL,
    request_count   INTEGER      NOT NULL DEFAULT 0,
    window_start    TIMESTAMPTZ  NOT NULL,
    window_end      TIMESTAMPTZ  NOT NULL,
    limit_exceeded  BOOLEAN      NOT NULL DEFAULT false
);

CREATE INDEX idx_api_rate_limits_company_window ON api_rate_limits(company_id, window_start);


-- ── system_health view ────────────────────────────────────────────────────────

CREATE VIEW system_health AS
SELECT 'total_companies'   AS metric, COUNT(*)::BIGINT AS value FROM companies WHERE deleted_at IS NULL
UNION ALL
SELECT 'total_active_users',           COUNT(*) FROM users     WHERE deleted_at IS NULL
UNION ALL
SELECT 'active_invoices',              COUNT(*) FROM invoices  WHERE status != 'paid' AND deleted_at IS NULL
UNION ALL
SELECT 'invoices_overdue',             COUNT(*) FROM invoices  WHERE status = 'overdue' AND deleted_at IS NULL
UNION ALL
SELECT 'upload_batches_pending_review',COUNT(*) FROM invoice_upload_batches WHERE status = 'review_pending';


-- ── connection_stats view ─────────────────────────────────────────────────────

CREATE VIEW connection_stats AS
SELECT
    datname,
    usename,
    COUNT(*)   AS connections,
    MAX(state) AS state
FROM pg_stat_activity
GROUP BY datname, usename;
