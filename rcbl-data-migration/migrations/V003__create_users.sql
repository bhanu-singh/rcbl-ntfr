-- User accounts scoped to a company. Deleting the company cascades here.

CREATE TABLE users (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id           UUID        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    email                VARCHAR(255) UNIQUE NOT NULL,
    password_hash        VARCHAR(255) NOT NULL,
    name                 VARCHAR(255) NOT NULL,
    timezone             VARCHAR(50)  NOT NULL DEFAULT 'UTC',
    email_notifications  JSONB        NOT NULL DEFAULT '{}',
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at        TIMESTAMPTZ,

    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_company_id  ON users(company_id);
CREATE INDEX idx_users_email       ON users(email);
CREATE INDEX idx_users_last_login  ON users(last_login_at);
