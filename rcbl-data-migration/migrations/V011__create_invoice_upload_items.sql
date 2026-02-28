-- Individual files within an upload batch.
-- invoice_id is SET NULL if the linked invoice is later deleted.
-- The reverse FK (invoices.upload_item_id → this table) is added in V012
-- after both tables exist, breaking the circular dependency.

CREATE TABLE invoice_upload_items (
    id                     UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id               UUID         NOT NULL REFERENCES invoice_upload_batches(id) ON DELETE CASCADE,
    company_id             UUID         NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    file_name              VARCHAR(500) NOT NULL,
    file_url               TEXT         NOT NULL,    -- S3 / MinIO object path
    file_hash              VARCHAR(64),              -- SHA-256 for deduplication
    file_size_bytes        BIGINT,
    status                 VARCHAR(20)  NOT NULL
                               CHECK (status IN ('queued', 'processing', 'ready', 'review_pending', 'accepted', 'rejected', 'failed')),
    ocr_confidence_score   DECIMAL(3,2) CHECK (ocr_confidence_score >= 0 AND ocr_confidence_score <= 1),
    ocr_extracted_data     JSONB,
    ocr_processing_time_ms INTEGER,
    error_message          TEXT,
    invoice_id             UUID         REFERENCES invoices(id) ON DELETE SET NULL,  -- Set after acceptance
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at           TIMESTAMPTZ
);

CREATE INDEX idx_invoice_upload_items_batch_id    ON invoice_upload_items(batch_id);
CREATE INDEX idx_invoice_upload_items_status      ON invoice_upload_items(status);
CREATE INDEX idx_invoice_upload_items_file_hash   ON invoice_upload_items(file_hash);
CREATE INDEX idx_invoice_upload_items_company_id  ON invoice_upload_items(company_id);
