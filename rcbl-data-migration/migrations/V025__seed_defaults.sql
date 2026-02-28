-- Default seed data applied once during initial deployment.
-- All AI feature flags start disabled; enable per-tenant as the AI module rolls out.
-- Default email templates and reminder sequences are created per-company by the
-- application on first login, NOT here (they need company_id context).

-- ── Feature flags (all disabled at MVP launch) ───────────────────────────────

INSERT INTO feature_flags (flag_name, description, enabled, rollout_percentage) VALUES
    ('ai_collection_agent',   'Autonomous collection agent via LangGraph',       false, 0),
    ('ai_payment_prediction', 'ML-based payment probability predictions',         false, 0),
    ('ai_risk_scoring',       'Customer credit risk scoring via XGBoost',         false, 0),
    ('ai_cash_flow_forecast', 'Monte Carlo cash flow forecasting',                false, 0),
    ('ai_message_generation', 'LLM-powered reminder message generation',          false, 0),
    ('ai_reply_classifier',   'Automatic classification of incoming customer replies', false, 0),
    ('bulk_upload',           'Bulk PDF invoice upload and OCR processing',       true,  100),
    ('csv_import',            'CSV invoice import with column mapping',           true,  100),
    ('accounting_integrations','Third-party accounting system sync (SevDesk etc)',true,  100)
ON CONFLICT (flag_name) DO NOTHING;
