-- Feature flag system for per-tenant capability gating.
-- target_companies is a UUID array; NULL means flag applies to all tenants
-- based on rollout_percentage alone.

CREATE TABLE feature_flags (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_name           VARCHAR(100) UNIQUE NOT NULL,
    description         TEXT,
    enabled             BOOLEAN     NOT NULL DEFAULT false,
    rollout_percentage  INTEGER     NOT NULL DEFAULT 0
                            CHECK (rollout_percentage >= 0 AND rollout_percentage <= 100),
    target_companies    UUID[],     -- Specific tenants to enable for; NULL = percentage-based rollout
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feature_flags_enabled ON feature_flags(enabled);

CREATE TRIGGER trg_feature_flags_updated_at
    BEFORE UPDATE ON feature_flags
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
