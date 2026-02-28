-- Inbound webhook events received from external accounting systems.
-- Stored for idempotency checking (duplicate event_type + payload hash).

CREATE TABLE webhook_events (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id    UUID        REFERENCES accounting_integrations(id) ON DELETE CASCADE,
    event_type        VARCHAR(50) NOT NULL
                          CHECK (event_type IN ('invoice_created', 'invoice_updated', 'payment_received', 'contact_updated')),
    payload           JSONB       NOT NULL,
    processing_status VARCHAR(20) NOT NULL
                          CHECK (processing_status IN ('received', 'processing', 'processed', 'failed')),
    error_message     TEXT,
    received_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at      TIMESTAMPTZ
);

CREATE INDEX idx_webhook_events_integration_id ON webhook_events(integration_id);
CREATE INDEX idx_webhook_events_status         ON webhook_events(processing_status);
CREATE INDEX idx_webhook_events_received_at    ON webhook_events(received_at);
