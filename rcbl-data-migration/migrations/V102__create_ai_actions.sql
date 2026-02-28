-- Proposed AI actions that require (or have received) human approval.
-- human_reviewer_id is SET NULL on user deletion so the action audit is preserved.

CREATE TABLE ai_actions (
    id                  UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id     UUID         NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    action_type         VARCHAR(30)  NOT NULL
                            CHECK (action_type IN (
                                'send_message', 'schedule_follow_up', 'offer_payment_plan',
                                'escalate', 'pause', 'resume', 'mark_paid'
                            )),
    status              VARCHAR(30)  NOT NULL
                            CHECK (status IN ('pending_approval', 'approved', 'executed', 'rejected', 'cancelled')),
    ai_confidence       DECIMAL(3,2) NOT NULL CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    ai_reasoning        TEXT         NOT NULL,
    human_reviewer_id   UUID         REFERENCES users(id) ON DELETE SET NULL,
    human_decision_at   TIMESTAMPTZ,
    human_notes         TEXT,
    executed_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_actions_conversation_id ON ai_actions(conversation_id);
CREATE INDEX idx_ai_actions_status          ON ai_actions(status);
CREATE INDEX idx_ai_actions_created_at      ON ai_actions(created_at);
CREATE INDEX idx_ai_actions_pending         ON ai_actions(status, created_at) WHERE status = 'pending_approval';
