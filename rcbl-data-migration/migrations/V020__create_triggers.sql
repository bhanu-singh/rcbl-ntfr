-- Database triggers for business rule enforcement and auto-maintenance.
--
-- 1. updated_at auto-update on all major tables
-- 2. Payment overpayment guard
-- 3. updated_at maintenance for companies


-- ── 1. Generic updated_at updater function ───────────────────────────────────

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables that have updated_at
CREATE TRIGGER trg_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_reminder_sequences_updated_at
    BEFORE UPDATE ON reminder_sequences
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_email_templates_updated_at
    BEFORE UPDATE ON email_templates
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_accounting_integrations_updated_at
    BEFORE UPDATE ON accounting_integrations
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_csv_import_profiles_updated_at
    BEFORE UPDATE ON csv_import_profiles
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ── 2. Payment overpayment guard ─────────────────────────────────────────────
-- Prevents the sum of all payments on an invoice from exceeding the invoice amount.
-- Uses a BEFORE INSERT trigger so the violation is caught immediately.

CREATE OR REPLACE FUNCTION validate_payment_amount()
RETURNS TRIGGER AS $$
DECLARE
    invoice_total     DECIMAL(10,2);
    already_paid      DECIMAL(10,2);
BEGIN
    SELECT amount INTO invoice_total
    FROM invoices
    WHERE id = NEW.invoice_id;

    SELECT COALESCE(SUM(amount), 0) INTO already_paid
    FROM payments
    WHERE invoice_id = NEW.invoice_id;

    IF (already_paid + NEW.amount) > invoice_total THEN
        RAISE EXCEPTION
            'Payment of % would exceed invoice total of % (already paid: %)',
            NEW.amount, invoice_total, already_paid
        USING ERRCODE = 'check_violation';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_payments_validate_amount
    BEFORE INSERT ON payments
    FOR EACH ROW EXECUTE FUNCTION validate_payment_amount();


-- ── 3. Autovacuum tuning for high-write tables ───────────────────────────────
-- Reduces bloat accumulation on tables with frequent updates/deletes.

ALTER TABLE invoices          SET (autovacuum_vacuum_scale_factor = 0.05);
ALTER TABLE payments          SET (autovacuum_vacuum_scale_factor = 0.10);
ALTER TABLE reminder_events   SET (autovacuum_vacuum_scale_factor = 0.05);
ALTER TABLE invoice_upload_items SET (autovacuum_vacuum_scale_factor = 0.05);
