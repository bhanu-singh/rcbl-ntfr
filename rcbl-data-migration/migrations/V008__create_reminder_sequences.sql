-- One reminder cadence configuration per company.
-- The JSONB `steps` column stores the ordered list of reminder steps
-- e.g. [{"day_offset": 1, "template": "friendly"}, {"day_offset": 7, "template": "firm"}]

CREATE TABLE reminder_sequences (
    id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    steps      JSONB       NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT one_sequence_per_company UNIQUE (company_id)
);

CREATE INDEX idx_reminder_sequences_company_id ON reminder_sequences(company_id);
