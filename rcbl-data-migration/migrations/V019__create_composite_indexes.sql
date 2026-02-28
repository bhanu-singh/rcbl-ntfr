-- Performance-critical composite and specialty indexes.
-- Separated from table creation migrations to keep each migration focused
-- and to make these indexes easy to tune independently.

-- ── Composite indexes for common query patterns ──────────────────────────────

-- Dashboard: all overdue invoices for a company ordered by due date
CREATE INDEX idx_invoices_company_status_due
    ON invoices(company_id, status, due_date);

-- Reminder scheduler: next invoices to act on per customer
CREATE INDEX idx_invoices_customer_status
    ON invoices(customer_id, status);

-- Payment lookup: all payments for an invoice ordered chronologically
CREATE INDEX idx_payments_invoice_date
    ON payments(invoice_id, payment_date);

-- ── Partial indexes (narrow hot paths) ──────────────────────────────────────

-- Only unpaid invoices need next_action scheduling
CREATE INDEX idx_invoices_next_action_unpaid
    ON invoices(next_action_date)
    WHERE status IN ('pending', 'due_soon', 'overdue');

-- Only active upload items are polled for OCR processing
CREATE INDEX idx_upload_items_queued
    ON invoice_upload_items(created_at)
    WHERE status IN ('queued', 'processing');

-- ── Full-text / trigram indexes for fuzzy search ─────────────────────────────

CREATE INDEX idx_customers_name_trgm
    ON customers USING gin(name gin_trgm_ops);

CREATE INDEX idx_invoices_number_trgm
    ON invoices USING gin(invoice_number gin_trgm_ops);

-- ── JSONB indexes ────────────────────────────────────────────────────────────

CREATE INDEX idx_email_notifications_jsonb
    ON users USING gin(email_notifications);

CREATE INDEX idx_ocr_data_jsonb
    ON invoices USING gin(ocr_extracted_data)
    WHERE ocr_extracted_data IS NOT NULL;

CREATE INDEX idx_anomaly_flags_jsonb
    ON invoices USING gin(anomaly_flags)
    WHERE anomaly_flags IS NOT NULL;
