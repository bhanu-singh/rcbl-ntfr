-- Individual messages within an AI collection conversation.
-- Covers both outbound AI-generated messages and inbound customer replies.

CREATE TABLE ai_messages (
    id                    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id       UUID         NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    direction             VARCHAR(20)  NOT NULL CHECK (direction IN ('outbound', 'inbound')),
    channel               VARCHAR(20)  NOT NULL CHECK (channel IN ('email', 'phone_script', 'linkedin')),
    message_type          VARCHAR(30)  NOT NULL
                              CHECK (message_type IN ('ai_generated', 'human_approved', 'human_written', 'customer_reply')),
    content               TEXT         NOT NULL,
    subject               TEXT,
    sentiment_score       DECIMAL(4,3) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    intent_classification VARCHAR(100),
    confidence_score      DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    ai_reasoning          TEXT,
    delivery_status       VARCHAR(20)  NOT NULL
                              CHECK (delivery_status IN ('draft', 'approved', 'sent', 'delivered', 'failed', 'opened', 'clicked')),
    sent_at               TIMESTAMPTZ,
    opened_at             TIMESTAMPTZ,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_messages_conversation_id  ON ai_messages(conversation_id);
CREATE INDEX idx_ai_messages_direction        ON ai_messages(direction);
CREATE INDEX idx_ai_messages_sent_at          ON ai_messages(sent_at);
CREATE INDEX idx_ai_messages_delivery_status  ON ai_messages(delivery_status);

-- High-volume table — lower autovacuum threshold
ALTER TABLE ai_messages SET (autovacuum_vacuum_scale_factor = 0.05);
