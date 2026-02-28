-- Tracks a single upload session (single file, bulk PDFs, or CSV import).
-- created_by is SET NULL on user deletion so batch history is preserved.

CREATE TABLE invoice_upload_batches (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id       UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    upload_type      VARCHAR(20) NOT NULL CHECK (upload_type IN ('single', 'bulk', 'csv_import')),
    total_files      INTEGER     NOT NULL DEFAULT 0,
    processed_files  INTEGER     NOT NULL DEFAULT 0,
    successful_files INTEGER     NOT NULL DEFAULT 0,
    failed_files     INTEGER     NOT NULL DEFAULT 0,
    status           VARCHAR(20) NOT NULL CHECK (status IN ('uploading', 'processing', 'review_pending', 'completed', 'failed')),
    metadata         JSONB,      -- Column mappings for CSV imports, etc.
    created_by       UUID        REFERENCES users(id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at     TIMESTAMPTZ
);

CREATE INDEX idx_invoice_upload_batches_company_id  ON invoice_upload_batches(company_id);
CREATE INDEX idx_invoice_upload_batches_status      ON invoice_upload_batches(status);
CREATE INDEX idx_invoice_upload_batches_created_at  ON invoice_upload_batches(created_at);
