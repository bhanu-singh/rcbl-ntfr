-- Saved column-mapping profiles for recurring CSV imports.
-- Allows companies to store named profiles so they don't re-map columns each time.

CREATE TABLE csv_import_profiles (
    id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id     UUID         NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    profile_name   VARCHAR(255) NOT NULL,
    column_mapping JSONB        NOT NULL,   -- Maps CSV header → invoice field
    date_format    VARCHAR(50),             -- e.g. 'DD.MM.YYYY'
    number_format  VARCHAR(50),             -- e.g. '1.234,56' vs '1,234.56'
    delimiter      VARCHAR(10)  NOT NULL DEFAULT ',',
    encoding       VARCHAR(20)  NOT NULL DEFAULT 'utf-8',
    last_used_at   TIMESTAMPTZ,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_csv_import_profiles_company_id ON csv_import_profiles(company_id);
