-- Enable required PostgreSQL extensions
-- gen_random_uuid() is built-in since PG 13; uuid-ossp is kept for compatibility
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;    -- Symmetric / asymmetric encryption (used for token storage)
CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- Trigram similarity for fuzzy name/invoice-number search
