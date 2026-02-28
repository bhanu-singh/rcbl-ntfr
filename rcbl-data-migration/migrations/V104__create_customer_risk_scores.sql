-- Customer credit risk assessment scores produced by the XGBoost risk model.
-- One score per customer per day (unique constraint enforced).

CREATE TABLE customer_risk_scores (
    id                       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id              UUID        NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    score_date               DATE        NOT NULL,
    risk_score               INTEGER     NOT NULL CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_category            VARCHAR(20) NOT NULL CHECK (risk_category IN ('low', 'medium', 'high', 'critical')),
    payment_history_score    INTEGER     NOT NULL CHECK (payment_history_score >= 0 AND payment_history_score <= 100),
    outstanding_balance_score INTEGER    NOT NULL CHECK (outstanding_balance_score >= 0 AND outstanding_balance_score <= 100),
    trend_score              INTEGER     NOT NULL CHECK (trend_score >= 0 AND trend_score <= 100),
    external_signal_score    INTEGER     NOT NULL CHECK (external_signal_score >= 0 AND external_signal_score <= 100),
    contributing_factors     JSONB,
    model_version            VARCHAR(50) NOT NULL,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer_risk_scores_customer_id   ON customer_risk_scores(customer_id);
CREATE INDEX idx_customer_risk_scores_score_date    ON customer_risk_scores(score_date);
CREATE INDEX idx_customer_risk_scores_risk_category ON customer_risk_scores(risk_category);
CREATE UNIQUE INDEX idx_customer_risk_scores_unique ON customer_risk_scores(customer_id, score_date);
