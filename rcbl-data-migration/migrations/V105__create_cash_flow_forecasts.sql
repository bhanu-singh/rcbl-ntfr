-- Per-company weekly cash flow forecasts produced by the Monte Carlo simulation.
-- One forecast record per company per forecast_date per target_week_start.
-- actual_amount is backfilled at end-of-week for model accuracy tracking.

CREATE TABLE cash_flow_forecasts (
    id                   UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id           UUID          NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    forecast_date        DATE          NOT NULL,
    target_week_start    DATE          NOT NULL,
    expected_amount      DECIMAL(12,2) NOT NULL,
    lower_bound          DECIMAL(12,2) NOT NULL,
    upper_bound          DECIMAL(12,2) NOT NULL,
    confidence_level     DECIMAL(3,2)  NOT NULL CHECK (confidence_level >= 0 AND confidence_level <= 1),
    contributing_invoices JSONB        NOT NULL,  -- Array of {invoice_id, amount, probability}
    actual_amount        DECIMAL(12,2),            -- Backfilled for accuracy tracking
    model_version        VARCHAR(50)   NOT NULL,
    created_at           TIMESTAMPTZ   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_bounds CHECK (lower_bound <= expected_amount AND expected_amount <= upper_bound)
);

CREATE INDEX idx_cash_flow_forecasts_company_id   ON cash_flow_forecasts(company_id);
CREATE INDEX idx_cash_flow_forecasts_forecast_date ON cash_flow_forecasts(forecast_date);
CREATE INDEX idx_cash_flow_forecasts_target_week  ON cash_flow_forecasts(target_week_start);
CREATE UNIQUE INDEX idx_cash_flow_forecasts_unique
    ON cash_flow_forecasts(company_id, forecast_date, target_week_start);
