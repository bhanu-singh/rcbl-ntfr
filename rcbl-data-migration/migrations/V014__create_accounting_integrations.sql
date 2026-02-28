-- Integration configuration for external accounting systems (SevDesk, Xero, etc.).
-- access_token and refresh_token are stored as TEXT but encrypted at the
-- application layer (AES-256-GCM via the Python cryptography library).
-- Do NOT store plain-text tokens here.

CREATE TABLE accounting_integrations (
    id                     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id             UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    provider               VARCHAR(50) NOT NULL
                               CHECK (provider IN ('sevdesk', 'xero', 'lexoffice', 'quickbooks', 'custom_webhook')),
    display_name           VARCHAR(255),
    access_token           TEXT        NOT NULL,     -- Encrypted at application layer
    refresh_token          TEXT,                     -- Encrypted at application layer
    token_expires_at       TIMESTAMPTZ,
    webhook_url            TEXT,                     -- For custom_webhook provider
    webhook_api_key        TEXT,                     -- Encrypted at application layer
    sync_direction         VARCHAR(20) NOT NULL CHECK (sync_direction IN ('import', 'export', 'bidirectional')),
    auto_sync_enabled      BOOLEAN     NOT NULL DEFAULT false,
    auto_sync_interval     VARCHAR(20) NOT NULL DEFAULT 'daily'
                               CHECK (auto_sync_interval IN ('hourly', 'daily', 'weekly')),
    auto_sync_time         TIME        NOT NULL DEFAULT '02:00:00',
    last_sync_at           TIMESTAMPTZ,
    last_sync_status       VARCHAR(20) CHECK (last_sync_status IN ('success', 'failed', 'partial')),
    last_sync_error        TEXT,
    sync_config            JSONB,                    -- Provider-specific configuration
    field_mapping_overrides JSONB,                   -- Custom field mapping per provider
    status                 VARCHAR(20) NOT NULL DEFAULT 'active'
                               CHECK (status IN ('active', 'disconnected', 'error')),
    created_at             TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_accounting_integrations_company_id ON accounting_integrations(company_id);
CREATE INDEX idx_accounting_integrations_provider   ON accounting_integrations(provider);
CREATE INDEX idx_accounting_integrations_status     ON accounting_integrations(status);
