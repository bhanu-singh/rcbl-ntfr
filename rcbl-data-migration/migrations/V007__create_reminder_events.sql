-- Audit log of every reminder email dispatched for an invoice.

CREATE TABLE reminder_events (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id       UUID        NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    template_type    VARCHAR(20) NOT NULL CHECK (template_type IN ('friendly', 'firm')),
    sent_at          TIMESTAMPTZ NOT NULL,
    recipient_email  VARCHAR(255) NOT NULL,
    delivery_status  VARCHAR(20) NOT NULL CHECK (delivery_status IN ('sent', 'failed', 'bounced', 'delivered', 'opened', 'clicked')),
    opened_at        TIMESTAMPTZ,
    is_manual        BOOLEAN     NOT NULL DEFAULT false,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reminder_events_invoice_id       ON reminder_events(invoice_id);
CREATE INDEX idx_reminder_events_sent_at          ON reminder_events(sent_at);
CREATE INDEX idx_reminder_events_delivery_status  ON reminder_events(delivery_status);
