-- Core invoice table. Two intentional FK gaps exist at this point:
--   • upload_item_id  → invoice_upload_items.id  (added in V012 to break circular dependency)
--   • ai_conversation_id → ai_conversations.id   (Post-MVP, not a FK — stored as plain UUID)
-- All other FKs are set here.

CREATE TABLE invoices (
    id                      UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id              UUID         NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    customer_id             UUID         NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    invoice_number          VARCHAR(100) NOT NULL,
    amount                  DECIMAL(10,2) NOT NULL,
    currency                CHAR(3)      NOT NULL DEFAULT 'EUR',
    invoice_date            DATE         NOT NULL,
    payment_terms_days      INTEGER      NOT NULL DEFAULT 30,
    due_date                DATE         NOT NULL,
    status                  VARCHAR(20)  NOT NULL CHECK (status IN ('pending', 'due_soon', 'overdue', 'paid', 'written_off')),
    file_url                TEXT,
    last_reminder_date      TIMESTAMPTZ,
    next_action_date        TIMESTAMPTZ,
    reminder_sequence_step  INTEGER      NOT NULL DEFAULT 0,

    -- Ingestion source
    source                  VARCHAR(30)  NOT NULL DEFAULT 'manual'
                                CHECK (source IN ('manual', 'upload', 'bulk_upload', 'csv_import', 'api_sync', 'email_forward', 'webhook')),

    -- OCR fields (populated after upload processing)
    ocr_processed           BOOLEAN      NOT NULL DEFAULT false,
    ocr_confidence_score    DECIMAL(3,2) CHECK (ocr_confidence_score >= 0 AND ocr_confidence_score <= 1),
    ocr_extracted_data      JSONB,
    upload_item_id          UUID,        -- FK to invoice_upload_items added in V012

    -- External integration fields
    external_id             VARCHAR(100),
    external_provider       VARCHAR(50),
    external_synced_at      TIMESTAMPTZ,
    external_sync_status    VARCHAR(20)  NOT NULL DEFAULT 'not_synced'
                                CHECK (external_sync_status IN ('not_synced', 'synced', 'sync_failed')),

    -- SevDesk legacy fields (backward compatibility)
    sevdesk_invoice_id      VARCHAR(100),
    sevdesk_synced_at       TIMESTAMPTZ,
    sevdesk_sync_status     VARCHAR(20)  NOT NULL DEFAULT 'not_synced'
                                CHECK (sevdesk_sync_status IN ('not_synced', 'synced', 'sync_failed')),

    -- AI prediction fields (Post-MVP, populated by AI module)
    ai_conversation_id      UUID,        -- Plain UUID; FK added when AI tables are created (V100)
    payment_probability_7d  DECIMAL(3,2) CHECK (payment_probability_7d >= 0 AND payment_probability_7d <= 1),
    payment_probability_30d DECIMAL(3,2) CHECK (payment_probability_30d >= 0 AND payment_probability_30d <= 1),
    expected_payment_date   DATE,
    prediction_updated_at   TIMESTAMPTZ,
    anomaly_flags           JSONB,

    created_at              TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_amount        CHECK (amount > 0),
    CONSTRAINT valid_currency      CHECK (currency ~ '^[A-Z]{3}$'),
    CONSTRAINT valid_payment_terms CHECK (payment_terms_days > 0 AND payment_terms_days <= 365),
    CONSTRAINT due_after_invoice   CHECK (due_date >= invoice_date),
    CONSTRAINT unique_invoice_per_company UNIQUE (company_id, invoice_number)
);

CREATE INDEX idx_invoices_company_id      ON invoices(company_id);
CREATE INDEX idx_invoices_customer_id     ON invoices(customer_id);
CREATE INDEX idx_invoices_status          ON invoices(status);
CREATE INDEX idx_invoices_due_date        ON invoices(due_date);
CREATE INDEX idx_invoices_external_id     ON invoices(external_provider, external_id);
CREATE INDEX idx_invoices_source          ON invoices(source);
CREATE INDEX idx_invoices_next_action     ON invoices(next_action_date) WHERE status != 'paid';
CREATE INDEX idx_invoices_payment_prob    ON invoices(payment_probability_7d, payment_probability_30d);
CREATE INDEX idx_invoices_ai_conversation ON invoices(ai_conversation_id);
CREATE INDEX idx_invoices_upload_item     ON invoices(upload_item_id);
