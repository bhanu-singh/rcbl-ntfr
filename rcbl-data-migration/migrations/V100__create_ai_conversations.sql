-- AI collection conversation tracker (Post-MVP).
-- One conversation per invoice; manages the full lifecycle of AI-driven collection.
-- Also adds the FK from invoices.ai_conversation_id which was deferred until now.

CREATE TABLE ai_conversations (
    id                       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id               UUID        NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    customer_id              UUID        NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    status                   VARCHAR(20) NOT NULL CHECK (status IN ('active', 'paused', 'completed', 'escalated')),
    autonomy_level           VARCHAR(20) NOT NULL CHECK (autonomy_level IN ('full', 'supervised', 'assisted')),
    current_stage            VARCHAR(20) NOT NULL
                                 CHECK (current_stage IN ('initial_outreach', 'follow_up', 'negotiation', 'escalated', 'resolved')),
    total_messages_sent      INTEGER     NOT NULL DEFAULT 0,
    total_responses_received INTEGER     NOT NULL DEFAULT 0,
    last_action_at           TIMESTAMPTZ,
    next_action_at           TIMESTAMPTZ,
    escalation_reason        TEXT,
    outcome                  VARCHAR(20) CHECK (outcome IN ('paid', 'payment_plan', 'dispute', 'churned', 'written_off')),
    version                  INTEGER     NOT NULL DEFAULT 1,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_message_counts CHECK (total_messages_sent >= 0 AND total_responses_received >= 0)
);

CREATE INDEX idx_ai_conversations_invoice_id   ON ai_conversations(invoice_id);
CREATE INDEX idx_ai_conversations_customer_id  ON ai_conversations(customer_id);
CREATE INDEX idx_ai_conversations_status       ON ai_conversations(status);
CREATE INDEX idx_ai_conversations_next_action  ON ai_conversations(next_action_at) WHERE status = 'active';
CREATE INDEX idx_ai_conversations_outcome      ON ai_conversations(outcome);

CREATE TRIGGER trg_ai_conversations_updated_at
    BEFORE UPDATE ON ai_conversations
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_ai_conversations_version
    BEFORE UPDATE ON ai_conversations
    FOR EACH ROW EXECUTE FUNCTION increment_version();

-- Now that ai_conversations exists, add the FK from invoices
ALTER TABLE invoices
    ADD CONSTRAINT fk_invoices_ai_conversation
        FOREIGN KEY (ai_conversation_id)
        REFERENCES ai_conversations(id)
        ON DELETE SET NULL;
