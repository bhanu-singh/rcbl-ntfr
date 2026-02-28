-- Learning signals captured for continuous model improvement.
-- Records outcomes of AI actions, human edits, and user overrides.
-- Processed by the nightly learning-event processor job.

CREATE TABLE ai_learning_events (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type       VARCHAR(30) NOT NULL
                         CHECK (event_type IN ('action_outcome', 'user_edit', 'user_override', 'customer_feedback')),
    conversation_id  UUID        REFERENCES ai_conversations(id) ON DELETE CASCADE,
    action_id        UUID        REFERENCES ai_actions(id) ON DELETE CASCADE,
    original_value   JSONB,
    outcome_value    JSONB,
    learning_signal  VARCHAR(20) NOT NULL CHECK (learning_signal IN ('positive', 'negative', 'neutral')),
    processed        BOOLEAN     NOT NULL DEFAULT false,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_learning_events_event_type       ON ai_learning_events(event_type);
CREATE INDEX idx_ai_learning_events_processed        ON ai_learning_events(processed, created_at);
CREATE INDEX idx_ai_learning_events_conversation_id  ON ai_learning_events(conversation_id);
