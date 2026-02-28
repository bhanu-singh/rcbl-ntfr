-- Optimistic locking via version columns.
-- On every UPDATE the application must include WHERE id = ? AND version = ?
-- and then increment version = version + 1 in the SET clause.
-- A mismatch means another process updated the row first → retry.

ALTER TABLE invoices          ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;
ALTER TABLE customers         ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;
ALTER TABLE accounting_integrations ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;

-- Trigger: automatically increment version on every UPDATE so the application
-- never needs to manually set it (just check it in the WHERE clause).

CREATE OR REPLACE FUNCTION increment_version()
RETURNS TRIGGER AS $$
BEGIN
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_invoices_version
    BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION increment_version();

CREATE TRIGGER trg_customers_version
    BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION increment_version();

CREATE TRIGGER trg_accounting_integrations_version
    BEFORE UPDATE ON accounting_integrations
    FOR EACH ROW EXECUTE FUNCTION increment_version();
