-- Soft-delete support: adds deleted_at to core tables.
-- Records are never physically removed; application queries filter WHERE deleted_at IS NULL.
-- Hard-delete via GDPR erasure requests is handled separately by a scheduled job.

ALTER TABLE companies  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE users      ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE customers  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE invoices   ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

-- Partial indexes that exclude soft-deleted rows — used by all list queries
CREATE INDEX idx_companies_active  ON companies(id)                WHERE deleted_at IS NULL;
CREATE INDEX idx_users_active      ON users(company_id)            WHERE deleted_at IS NULL;
CREATE INDEX idx_customers_active  ON customers(company_id)        WHERE deleted_at IS NULL;
CREATE INDEX idx_invoices_active   ON invoices(company_id, status) WHERE deleted_at IS NULL;

-- Update the health check view to exclude soft-deleted rows (recreate after soft-delete columns exist)
-- Note: The view is created in V023 after this migration runs.
