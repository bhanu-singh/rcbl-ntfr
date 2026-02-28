-- ML-based payment probability predictions per invoice.
-- One prediction record per invoice per day (unique constraint enforced).
-- actual_payment_date is backfilled when payment is received (for model training).

CREATE TABLE payment_predictions (
    id                   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id           UUID         NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    prediction_date      DATE         NOT NULL,
    prob_7_days          DECIMAL(3,2) NOT NULL CHECK (prob_7_days >= 0 AND prob_7_days <= 1),
    prob_14_days         DECIMAL(3,2) NOT NULL CHECK (prob_14_days >= 0 AND prob_14_days <= 1),
    prob_30_days         DECIMAL(3,2) NOT NULL CHECK (prob_30_days >= 0 AND prob_30_days <= 1),
    prob_by_due_date     DECIMAL(3,2) NOT NULL CHECK (prob_by_due_date >= 0 AND prob_by_due_date <= 1),
    expected_payment_date DATE        NOT NULL,
    confidence_score     DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    model_version        VARCHAR(50)  NOT NULL,
    feature_importance   JSONB,
    actual_payment_date  DATE,        -- Backfilled for model training
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payment_predictions_invoice_id     ON payment_predictions(invoice_id);
CREATE INDEX idx_payment_predictions_prediction_date ON payment_predictions(prediction_date);
CREATE INDEX idx_payment_predictions_model_version  ON payment_predictions(model_version);
CREATE UNIQUE INDEX idx_payment_predictions_unique  ON payment_predictions(invoice_id, prediction_date);

CREATE INDEX idx_feature_importance_jsonb
    ON payment_predictions USING gin(feature_importance)
    WHERE feature_importance IS NOT NULL;
