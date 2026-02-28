# rcbl-data-migration

Flyway database migrations for the RCBL Receivable Notification System.

## Structure

```
rcbl-data-migration/
├── flyway.toml          # Flyway configuration
├── .env.example         # Environment variable template
├── README.md
└── migrations/
    ├── V001__...        # MVP: Core schema (V001–V025)
    └── V100__...        # Post-MVP: AI / ML tables (V100–V108)
```

## Migration Phases

| Range    | Phase                   | Description                                          |
|----------|-------------------------|------------------------------------------------------|
| V001–V016 | Core Schema (MVP)       | All business entities, FKs, basic indexes            |
| V017–V018 | Security                | Audit logs, Row-Level Security (RLS) policies        |
| V019–V020 | Performance             | Composite indexes, JSONB indexes, triggers           |
| V021–V025 | Compliance & Monitoring | Soft deletes, optimistic locking, system tables, seeds |
| V100–V108 | AI / ML (Post-MVP)      | AI conversations, predictions, risk scores, materialized views |

## Prerequisites

- PostgreSQL 14+
- Flyway CLI 10+ OR the Flyway Docker image

### Install Flyway CLI (macOS)

```bash
brew install flyway
```

### Or use Docker

```bash
docker pull flyway/flyway:10
```

## Setup

### 1. Create the migration role and database

Connect as a superuser and run:

```sql
-- Create the migration admin role
CREATE ROLE rcbl_admin LOGIN PASSWORD 'changeme' CREATEDB;

-- Create the runtime application role (used by FastAPI, no login)
CREATE ROLE rcbl_app NOLOGIN;

-- Create the database
CREATE DATABASE rcbl OWNER rcbl_admin;
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Run migrations

```bash
# Using Flyway CLI
flyway migrate

# Using Docker
docker run --rm \
  --network host \
  -v $(pwd)/migrations:/flyway/sql \
  -e FLYWAY_URL=jdbc:postgresql://localhost:5432/rcbl \
  -e FLYWAY_USER=rcbl_admin \
  -e FLYWAY_PASSWORD=changeme \
  flyway/flyway:10 migrate
```

## Common Commands

```bash
# Check current state of applied migrations
flyway info

# Validate that applied checksums match local files
flyway validate

# Repair the schema history table (e.g., after a failed migration)
flyway repair

# Undo the last versioned migration (requires Flyway Teams)
flyway undo

# Clean the database (DANGER: drops all objects — dev/test only)
flyway clean
```

## Creating a New Migration

1. Determine the next version number (see current max in `migrations/`)
2. Create file: `migrations/V{NNN}__{description}.sql`
   - Version: 3-digit zero-padded number (e.g., `V026`)
   - Description: snake_case (e.g., `add_company_logo_url`)
   - Double underscore between version and description is required
3. Write idempotent SQL (use `IF NOT EXISTS`, `IF EXISTS` where possible)
4. Run `flyway info` to verify the new migration is detected
5. Run `flyway migrate` to apply

### Example

```bash
touch migrations/V026__add_company_logo_url.sql
```

```sql
-- migrations/V026__add_company_logo_url.sql
ALTER TABLE companies
    ADD COLUMN IF NOT EXISTS logo_url TEXT;
```

## Row-Level Security (RLS) Notes

RLS is enabled in `V018__enable_rls.sql`. The application must set the tenant
context on every database connection before running queries:

```sql
-- Set in every authenticated request (Python/SQLAlchemy):
SET LOCAL app.current_company_id = '<company-uuid>';
```

The `rcbl_app` role (runtime application role) is subject to RLS.
The `rcbl_admin` role (migration runner) uses `BYPASSRLS` to apply migrations
without being blocked by policies.

To grant the BYPASSRLS privilege to the migration role:
```sql
ALTER ROLE rcbl_admin BYPASSRLS;
```

## AI / Post-MVP Migrations (V100+)

Migrations V100 and above create AI-related tables. They are **not applied
automatically** in the MVP deployment — apply them only when rolling out
AI features:

```bash
# Apply only up to V025 (MVP)
flyway migrate -target=25

# Apply all including AI tables
flyway migrate
```

## CI/CD Integration

In your CI/CD pipeline, run migrations before starting the application:

```yaml
# Docker Compose (ci)
flyway:
  image: flyway/flyway:10
  command: migrate
  depends_on: [postgres]
  volumes:
    - ./rcbl-data-migration/migrations:/flyway/sql
  environment:
    FLYWAY_URL: jdbc:postgresql://postgres:5432/rcbl
    FLYWAY_USER: rcbl_admin
    FLYWAY_PASSWORD: ${DB_ADMIN_PASSWORD}
    FLYWAY_BASELINE_ON_MIGRATE: "true"
```
