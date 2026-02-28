-- Multi-tenant root entity. Every tenant-scoped table carries company_id
-- referencing this table. Deleting a company cascades to all owned data.

CREATE TABLE companies (
    id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name                  VARCHAR(255) NOT NULL,
    slug                  VARCHAR(100) UNIQUE NOT NULL,
    email                 VARCHAR(255) NOT NULL,
    default_payment_terms INTEGER      NOT NULL DEFAULT 30,
    default_currency      CHAR(3)      NOT NULL DEFAULT 'EUR',
    eu_regulation_enabled BOOLEAN      NOT NULL DEFAULT false,
    storage_quota_bytes   BIGINT       NOT NULL DEFAULT 10737418240, -- 10 GB
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_currency      CHECK (default_currency ~ '^[A-Z]{3}$'),
    CONSTRAINT valid_payment_terms CHECK (default_payment_terms > 0 AND default_payment_terms <= 365),
    CONSTRAINT valid_storage_quota CHECK (storage_quota_bytes > 0)
);

CREATE INDEX idx_companies_slug       ON companies(slug);
CREATE INDEX idx_companies_created_at ON companies(created_at);
