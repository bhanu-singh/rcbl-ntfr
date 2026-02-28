-- Immutable audit log for every sync run against an accounting integration.

CREATE TABLE sync_logs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id  UUID        NOT NULL REFERENCES accounting_integrations(id) ON DELETE CASCADE,
    sync_type       VARCHAR(20) NOT NULL CHECK (sync_type IN ('manual', 'automatic')),
    direction       VARCHAR(20) NOT NULL CHECK (direction IN ('import', 'export', 'bidirectional')),
    records_synced  INTEGER     NOT NULL DEFAULT 0,
    records_failed  INTEGER     NOT NULL DEFAULT 0,
    status          VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed', 'partial')),
    error_message   TEXT,
    started_at      TIMESTAMPTZ NOT NULL,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sync_logs_integration_id ON sync_logs(integration_id);
CREATE INDEX idx_sync_logs_started_at     ON sync_logs(started_at);
CREATE INDEX idx_sync_logs_status         ON sync_logs(status);
