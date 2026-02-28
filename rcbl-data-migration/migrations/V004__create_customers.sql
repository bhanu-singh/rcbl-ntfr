-- Customer entities per company. AI/risk columns are nullable;
-- they are populated by the AI module (Post-MVP) via background jobs.

CREATE TABLE customers (
    id                          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id                  UUID         NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name                        VARCHAR(255) NOT NULL,
    email                       VARCHAR(255) NOT NULL,
    contact_person              VARCHAR(255),
    default_payment_terms       INTEGER,
    notes                       TEXT,

    -- AI-populated risk fields (Post-MVP)
    risk_score                  INTEGER      CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_category               VARCHAR(20)  CHECK (risk_category IN ('low', 'medium', 'high', 'critical')),
    risk_updated_at             TIMESTAMPTZ,
    ai_customer_summary         TEXT,
    avg_days_to_pay             DECIMAL(5,2),
    payment_reliability_score   DECIMAL(3,2) CHECK (payment_reliability_score >= 0 AND payment_reliability_score <= 1),
    preferred_contact_channel   VARCHAR(20)  CHECK (preferred_contact_channel IN ('email', 'phone', 'linkedin')),
    preferred_contact_time      JSONB,
    relationship_value_score    DECIMAL(10,2),

    created_at                  TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                  TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_customer_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_customers_company_id    ON customers(company_id);
CREATE INDEX idx_customers_email         ON customers(company_id, email);
CREATE INDEX idx_customers_risk_category ON customers(risk_category);
CREATE INDEX idx_customers_created_at    ON customers(created_at);
