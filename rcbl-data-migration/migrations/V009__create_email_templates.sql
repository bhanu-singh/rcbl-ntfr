-- Per-company customisable email templates.
-- One template per type per company (enforced by unique constraint).

CREATE TABLE email_templates (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id    UUID         NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    template_type VARCHAR(20)  NOT NULL CHECK (template_type IN ('friendly', 'firm')),
    subject       VARCHAR(500) NOT NULL,
    body          TEXT         NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_template_per_company UNIQUE (company_id, template_type)
);

CREATE INDEX idx_email_templates_company_id ON email_templates(company_id);
