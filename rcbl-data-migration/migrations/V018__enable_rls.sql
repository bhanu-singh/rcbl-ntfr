-- Row-Level Security: enforces tenant isolation at the database layer.
--
-- IMPORTANT prerequisites (run once as superuser BEFORE applying migrations):
--   CREATE ROLE rcbl_app NOLOGIN;
--   GRANT CONNECT ON DATABASE rcbl TO rcbl_app;
--   GRANT USAGE ON SCHEMA public TO rcbl_app;
--   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO rcbl_app;
--   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO rcbl_app;
--   ALTER ROLE rcbl_admin BYPASSRLS;   -- migration runner bypasses RLS
--
-- The application must execute on every authenticated connection:
--   SET LOCAL app.current_company_id = '<company-uuid>';
-- ---------------------------------------------------------------------------

-- Enable RLS on all company-scoped tables
ALTER TABLE users                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers               ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices                ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments                ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminder_events         ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminder_sequences      ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_templates         ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_upload_batches  ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_upload_items    ENABLE ROW LEVEL SECURITY;
ALTER TABLE csv_import_profiles     ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounting_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_logs               ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_events          ENABLE ROW LEVEL SECURITY;

-- FORCE RLS so even the table owner is subject to policies
ALTER TABLE users                   FORCE ROW LEVEL SECURITY;
ALTER TABLE customers               FORCE ROW LEVEL SECURITY;
ALTER TABLE invoices                FORCE ROW LEVEL SECURITY;
ALTER TABLE payments                FORCE ROW LEVEL SECURITY;
ALTER TABLE reminder_events         FORCE ROW LEVEL SECURITY;
ALTER TABLE reminder_sequences      FORCE ROW LEVEL SECURITY;
ALTER TABLE email_templates         FORCE ROW LEVEL SECURITY;
ALTER TABLE invoice_upload_batches  FORCE ROW LEVEL SECURITY;
ALTER TABLE invoice_upload_items    FORCE ROW LEVEL SECURITY;
ALTER TABLE csv_import_profiles     FORCE ROW LEVEL SECURITY;
ALTER TABLE accounting_integrations FORCE ROW LEVEL SECURITY;
ALTER TABLE sync_logs               FORCE ROW LEVEL SECURITY;
ALTER TABLE webhook_events          FORCE ROW LEVEL SECURITY;

-- ── Direct company_id isolation ─────────────────────────────────────────────

CREATE POLICY users_tenant_isolation ON users
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY customers_tenant_isolation ON customers
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY invoices_tenant_isolation ON invoices
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY reminder_sequences_tenant_isolation ON reminder_sequences
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY email_templates_tenant_isolation ON email_templates
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY accounting_integrations_tenant_isolation ON accounting_integrations
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY invoice_upload_batches_tenant_isolation ON invoice_upload_batches
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY invoice_upload_items_tenant_isolation ON invoice_upload_items
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY csv_import_profiles_tenant_isolation ON csv_import_profiles
    USING (company_id = current_setting('app.current_company_id')::UUID);

-- ── Parent-joined isolation (no direct company_id column) ───────────────────

CREATE POLICY payments_tenant_isolation ON payments
    USING (invoice_id IN (
        SELECT id FROM invoices
        WHERE company_id = current_setting('app.current_company_id')::UUID
    ));

CREATE POLICY reminder_events_tenant_isolation ON reminder_events
    USING (invoice_id IN (
        SELECT id FROM invoices
        WHERE company_id = current_setting('app.current_company_id')::UUID
    ));

CREATE POLICY sync_logs_tenant_isolation ON sync_logs
    USING (integration_id IN (
        SELECT id FROM accounting_integrations
        WHERE company_id = current_setting('app.current_company_id')::UUID
    ));

CREATE POLICY webhook_events_tenant_isolation ON webhook_events
    USING (integration_id IN (
        SELECT id FROM accounting_integrations
        WHERE company_id = current_setting('app.current_company_id')::UUID
    ));
