-- Extend Row-Level Security to AI tables.
-- AI tables don't have a direct company_id; isolation is inherited
-- through their parent invoice or customer (both already RLS-filtered).

ALTER TABLE ai_conversations   ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_messages        ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_actions         ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_risk_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE cash_flow_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_learning_events ENABLE ROW LEVEL SECURITY;

ALTER TABLE ai_conversations   FORCE ROW LEVEL SECURITY;
ALTER TABLE ai_messages        FORCE ROW LEVEL SECURITY;
ALTER TABLE ai_actions         FORCE ROW LEVEL SECURITY;
ALTER TABLE payment_predictions FORCE ROW LEVEL SECURITY;
ALTER TABLE customer_risk_scores FORCE ROW LEVEL SECURITY;
ALTER TABLE cash_flow_forecasts FORCE ROW LEVEL SECURITY;
ALTER TABLE ai_learning_events FORCE ROW LEVEL SECURITY;

-- Isolated via parent invoice (already company-scoped via V018)
CREATE POLICY ai_conversations_tenant_isolation ON ai_conversations
    USING (invoice_id IN (
        SELECT id FROM invoices
        WHERE company_id = current_setting('app.current_company_id')::UUID
    ));

CREATE POLICY ai_messages_tenant_isolation ON ai_messages
    USING (conversation_id IN (
        SELECT id FROM ai_conversations
        WHERE invoice_id IN (
            SELECT id FROM invoices
            WHERE company_id = current_setting('app.current_company_id')::UUID
        )
    ));

CREATE POLICY ai_actions_tenant_isolation ON ai_actions
    USING (conversation_id IN (
        SELECT id FROM ai_conversations
        WHERE invoice_id IN (
            SELECT id FROM invoices
            WHERE company_id = current_setting('app.current_company_id')::UUID
        )
    ));

CREATE POLICY payment_predictions_tenant_isolation ON payment_predictions
    USING (invoice_id IN (
        SELECT id FROM invoices
        WHERE company_id = current_setting('app.current_company_id')::UUID
    ));

CREATE POLICY customer_risk_scores_tenant_isolation ON customer_risk_scores
    USING (customer_id IN (
        SELECT id FROM customers
        WHERE company_id = current_setting('app.current_company_id')::UUID
    ));

-- cash_flow_forecasts has direct company_id
CREATE POLICY cash_flow_forecasts_tenant_isolation ON cash_flow_forecasts
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY ai_learning_events_tenant_isolation ON ai_learning_events
    USING (conversation_id IN (
        SELECT id FROM ai_conversations
        WHERE invoice_id IN (
            SELECT id FROM invoices
            WHERE company_id = current_setting('app.current_company_id')::UUID
        )
    ));
