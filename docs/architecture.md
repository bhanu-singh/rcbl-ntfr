# System Architecture Document
## Receivable Notification System (RCBL)

**Document Version:** 3.0  
**Last Updated:** February 15, 2026  
**Architecture Style:** Multi-Tenant SaaS, Service-Oriented (Backend + AI Agent Service)  
**Reference:** Based on `ai-functional-spec.md` v2.0

---

## Table of Contents

1. [Architecture Principles](#1-architecture-principles)
2. [C1: System Context](#2-c1-system-context)
3. [C2: Container Diagram](#3-c2-container-diagram)
4. [C3: Component Diagrams](#4-c3-component-diagrams)
5. [Multi-Tenancy Strategy](#5-multi-tenancy-strategy)
6. [Backend Architecture](#6-backend-architecture)
7. [Frontend Architecture](#7-frontend-architecture)
8. [Cron & Background Jobs](#8-cron--background-jobs)
9. [AI Agent Architecture (LangGraph Platform -- Separate Repo)](#9-ai-agent-architecture-langgraph-platform----separate-repo)
10. [Data Layer](#10-data-layer)
11. [Infrastructure & Deployment](#11-infrastructure--deployment)
12. [Security Architecture](#12-security-architecture)
13. [Scalability Playbook](#13-scalability-playbook)
14. [MVP vs Post-MVP Boundary](#14-mvp-vs-post-mvp-boundary)

---

## 1. Architecture Principles

| Principle | Rationale |
|-----------|-----------|
| **Tenant isolation at the data layer** | Every table carries `company_id`; Row-Level Security enforces isolation at the DB level |
| **Two-repo separation** | Backend (`rcbl-backend`) and AI agents (`receivable-agents`) are independent repos, independently deployable and scalable |
| **Async by default** | All heavy work (OCR, sync, emails, AI) goes through a Redis job queue; API calls return immediately |
| **AI as a separate service** | LangGraph agents run on LangGraph Platform in the `receivable-agents` repo; the backend calls them via the `langgraph-sdk` Python client over HTTP |
| **Cron as external trigger** | Hetzner Cron Jobs calls protected HTTP endpoints on the backend; no in-process scheduler needed |
| **Feature-flag everything post-MVP** | AI capabilities are gated behind feature flags per tenant so they can be rolled out progressively |
| **Zero-trust multi-tenancy** | Never rely only on application logic for tenant isolation; RLS is the last line of defense |
| **Cost-aware AI** | LLM/OCR calls are metered per tenant with hard limits; caching and model tiering reduce spend |

---

## 2. C1: System Context

The outermost view -- who uses the system and what external systems does it talk to.

```mermaid
C4Context
    title System Context Diagram (C1) - RCBL Receivable Notification System

    Person(sme, "SME Owner / Finance Manager", "Uses web app to manage accounts receivable")
    Person(customer, "Customer (Invoice Recipient)", "Receives reminder emails, replies to collection messages, views payment plan proposals")

    System(rcbl, "RCBL - Receivable Notification System", "SaaS platform for invoice tracking, automated reminders, AI-powered collections, and cash flow prediction")

    System_Ext(accounting, "Accounting Systems", "SevDesk, Xero, LexOffice, Custom Webhook")
    System_Ext(email, "Email Services", "AWS SES, SendGrid, SMTP/IMAP")
    System_Ext(ocr_llm, "OCR / LLM Providers", "OpenAI Vision, AWS Textract, Anthropic, PaddleOCR")
    System_Ext(payment, "Payment Sources", "Bank CSV, Manual entry, API sync")
    System_Ext(hetzner, "Hetzner Cron Jobs", "External cron scheduler, triggers HTTP endpoints")

    Rel(sme, rcbl, "Uses", "HTTPS / Web App")
    Rel(rcbl, sme, "Sends notifications", "Email")
    Rel(rcbl, accounting, "Syncs invoices & payments", "REST API + OAuth 2.0")
    Rel(rcbl, email, "Sends reminder & notification emails", "SMTP / REST API")
    Rel(rcbl, ocr_llm, "Extracts invoice data, generates AI messages", "REST API")
    Rel(rcbl, payment, "Imports payment data", "CSV / API")
    Rel(rcbl, customer, "Sends reminders & collection messages", "Email")
    Rel(customer, rcbl, "Replies to messages", "Email")
    Rel(hetzner, rcbl, "Triggers scheduled jobs", "HTTPS + Secret Header")
```

### External Systems Summary

| External System | Interaction | Protocol | MVP? |
|----------------|-------------|----------|------|
| **SevDesk** | Bidirectional invoice + payment sync | REST API + OAuth 2.0 | Yes |
| **Xero** | One-way invoice import | REST API + OAuth 2.0 | V1 |
| **LexOffice** | One-way invoice import | REST API + API Key | V1 |
| **Custom Webhook** | Inbound invoice data | HTTPS POST + API Key | V2 |
| **AWS SES / SendGrid** | Send reminder & notification emails | SMTP / REST API | Yes |
| **SMTP/IMAP** | Receive forwarded invoices, customer replies | IMAP polling | Yes |
| **OpenAI Vision** | OCR invoice extraction | REST API + API Key | Yes |
| **AWS Textract** | OCR fallback | REST API + IAM | Yes (fallback) |
| **OpenAI GPT-4 / Anthropic Claude** | AI message generation, classification | REST API + API Key | Post-MVP |
| **S3 / MinIO** | File storage for invoices | S3-compatible API | Yes |
| **Redis** | Job queue, cache, pub/sub | Redis protocol | Yes |
| **Hetzner Cron Jobs** | Trigger scheduled jobs (status update, reminders, sync, digest) | HTTPS POST + shared secret | Yes |

---

## 3. C2: Container Diagram

The runtime containers -- what processes run and how they communicate.

```mermaid
C4Container
    title Container Diagram (C2) - RCBL System

    Person(user, "SME User", "Uses web browser")

    Container_Boundary(rcbl, "RCBL Platform (rcbl-backend repo)") {
        Container(spa, "Frontend SPA", "React 18, TypeScript, TailwindCSS, Vite", "User interface for all screens")
        Container(proxy, "Reverse Proxy", "Caddy / Nginx / Fly Proxy", "TLS termination, routing, rate limiting")
        Container(api, "Backend API", "Python 3.12, FastAPI, SQLAlchemy, Pydantic", "REST API, Auth (JWT), SSE, Webhook receiver, Cron endpoints. Calls agents via langgraph-sdk.")
        Container(worker, "Queue Worker", "Python 3.12, arq, same backend codebase", "Consumes Redis queues: OCR, CSV, email, sync, webhook, AI job dispatch")
        ContainerDb(pg, "PostgreSQL", "PostgreSQL 16", "Primary data store with RLS for tenancy. Core tables, AI tables, Audit logs")
        ContainerDb(redis, "Redis", "Redis 7", "Job Queue (arq), Cache, Pub/Sub, Rate Limits")
        Container(s3, "Object Storage", "S3 / MinIO", "Invoice PDFs, OCR results, CSV uploads, Export files")
    }

    Container_Boundary(agents, "AI Agent Service (receivable-agents repo)") {
        Container(lg_platform, "LangGraph Platform", "Python 3.12, LangGraph, langgraph-api", "Hosts LangGraph agent graphs: Collection Agent, Reply Classifier. Stateful, checkpointed.")
    }

    System_Ext(llm, "LLM / OCR APIs", "OpenAI Vision, GPT-4, Anthropic Claude")
    System_Ext(hetzner, "Hetzner Cron Jobs", "Calls /internal/cron/* endpoints on schedule")

    Rel(user, proxy, "HTTPS")
    Rel(proxy, spa, "Serves static assets", "CDN / S3")
    Rel(proxy, api, "Routes API calls", "HTTP")
    Rel(api, pg, "Reads/Writes", "SQLAlchemy + asyncpg + RLS")
    Rel(api, redis, "Publishes jobs, caches", "Redis protocol")
    Rel(api, s3, "Stores/retrieves files", "S3 API")
    Rel(api, llm, "OCR calls", "REST API")
    Rel(api, lg_platform, "Invokes agent runs", "langgraph-sdk (HTTP)")
    Rel(worker, pg, "Reads/Writes", "SQLAlchemy + asyncpg + RLS")
    Rel(worker, redis, "Consumes jobs", "Redis protocol")
    Rel(worker, s3, "Reads files", "S3 API")
    Rel(worker, lg_platform, "Dispatches AI jobs", "langgraph-sdk (HTTP)")
    Rel(lg_platform, llm, "LLM + embedding calls", "REST API")
    Rel(lg_platform, pg, "Reads context data", "asyncpg (read-only)")
    Rel(hetzner, api, "Triggers cron endpoints", "HTTPS + secret")
```

### Container Summary

| Container | Technology | Repo | Role | MVP? | Scales How |
|-----------|------------|------|------|------|------------|
| **Frontend SPA** | React 18 + TypeScript + TailwindCSS + Vite | `rcbl-frontend` | User interface, all screens | Yes | CDN-served, stateless |
| **Backend API** | Python 3.12 + FastAPI + SQLAlchemy + Pydantic | `rcbl-backend` | REST API, auth, business logic, webhook receiver, cron endpoints | Yes | Horizontal (stateless) |
| **Queue Worker** | Python 3.12 + arq (same backend codebase) | `rcbl-backend` | Async job consumers: OCR, CSV, email, sync, webhook, AI dispatch | Yes | Horizontal (competing consumers) |
| **LangGraph Platform** | Python 3.12 + LangGraph + langgraph-api | `receivable-agents` | AI agent graphs (Collection, Reply Classifier), stateful agents | Post-MVP | Horizontal (independent) |
| **Hetzner Cron** | Hetzner Cron Jobs (external, managed) | N/A | Triggers scheduled HTTP endpoints at configured intervals | Yes | Managed |
| **PostgreSQL** | PostgreSQL 16 | N/A | Primary data store, RLS for tenancy | Yes | Vertical → read replicas |
| **Redis** | Redis 7 (or Valkey) | N/A | Job queue (arq), cache, pub/sub, rate limits | Yes | Vertical → cluster |
| **Object Storage** | MinIO (self-hosted) / AWS S3 | N/A | File storage (invoices, CSVs) | Yes | Managed, unlimited |
| **Reverse Proxy** | Caddy or Fly Proxy | N/A | TLS termination, routing, rate limiting | Yes | Managed |

> **Key architecture decision:** The AI agents live in a **separate repository** (`receivable-agents`) and are deployed as a **LangGraph Platform** service. The backend calls agents via the **`langgraph-sdk`** Python client over HTTP. This allows independent development, deployment, and scaling of the AI and backend components.

---

## 4. C3: Component Diagrams

### 4.1 C3: Backend API (Python / FastAPI)

```mermaid
graph TB
    subgraph HTTP_LAYER["HTTP Layer (FastAPI + Middleware)"]
        AUTH_MW["Auth Middleware<br/>(JWT validation)"]
        RATE_LIM["Rate Limiter<br/>(slowapi + Redis)"]
        TENANT_RES["Tenant Resolver<br/>(company_id from JWT)"]
        REQ_LOG["Request Logger<br/>(structlog)"]
    end

    subgraph ROUTE_HANDLERS["Route Handlers (FastAPI Routers)"]
        INV_ROUTES["Invoice Router<br/>/api/invoices/.."]
        CUST_ROUTES["Customer Router<br/>/api/customers/.."]
        DASH_ROUTES["Dashboard Router<br/>/api/dashboard/.."]
        UPLOAD_ROUTES["Upload Router<br/>/api/invoices/upload"]
        INTEG_ROUTES["Integration Router<br/>/api/integrations/.."]
        SETTINGS_ROUTES["Settings Router<br/>/api/settings/.."]
        AUTH_ROUTES["Auth Router<br/>/api/auth/.."]
        CRON_ROUTES["Cron Router<br/>/internal/cron/..<br/>(Hetzner calls these)"]
        AI_ROUTES["AI Router<br/>/api/ai/.. (Post-MVP)"]
        WH_ROUTES["Webhook Receiver<br/>/api/webhooks/:slug/.."]
    end

    subgraph SERVICE_LAYER["Service Layer"]
        INV_SVC["InvoiceService<br/>create, update,<br/>mark_paid, bulk_ops"]
        CUST_SVC["CustomerService<br/>CRUD, fuzzy_match,<br/>merge"]
        REM_SVC["ReminderService<br/>evaluate_sequence,<br/>send_reminder,<br/>schedule_next"]
        UPLOAD_SVC["UploadService<br/>single, batch,<br/>process_ocr, review"]
        CSV_SVC["CSVImportService<br/>parse, map_cols,<br/>validate, import"]
        INTEG_SVC["IntegrationService<br/>oauth_flow, sync,<br/>refresh_token,<br/>handle_webhook"]
        PAY_SVC["PaymentService<br/>record, csv_import,<br/>match"]
        DASH_SVC["DashboardService<br/>stats, overdue,<br/>dso_calc"]
        NOTIF_SVC["NotificationService<br/>email, in_app,<br/>daily_digest"]
    end

    subgraph INFRA_LAYER["Infrastructure Layer"]
        DB_POOL["DB Session<br/>(SQLAlchemy async +<br/>asyncpg pool)"]
        REDIS_CLI["Redis Client<br/>(redis-py / arq)"]
        S3_CLI["S3 Client<br/>(boto3 / aioboto3)"]
        EMAIL_CLI["Email Client<br/>(aiosmtplib /<br/>SES SDK)"]
        OCR_CLI["OCR Client<br/>(httpx →<br/>OpenAI / AWS)"]
        JOB_PUB["Job Publisher<br/>(arq enqueue)"]
        CRYPTO["Crypto<br/>(cryptography /<br/>python-jose)"]
        TENANT_CTX["Tenant Context<br/>(Sets company_id<br/>for RLS from JWT)"]
    end

    HTTP_LAYER --> ROUTE_HANDLERS
    ROUTE_HANDLERS --> SERVICE_LAYER
    SERVICE_LAYER --> INFRA_LAYER
```

### 4.2 C3: Queue Worker + Hetzner Cron

```mermaid
graph TB
    subgraph HETZNER["Hetzner Cron Jobs (External)<br/>Calls protected HTTP endpoints on the Backend API"]
        STATUS_UPD["Invoice Status Updater<br/>POST /internal/cron/update-statuses<br/>Every 6h: */6 * * * *"]
        REM_SEND["Reminder Sender<br/>POST /internal/cron/send-reminders<br/>Every 4h: 0 */4 * * *"]
        DIGEST["Daily Digest Mailer<br/>POST /internal/cron/daily-digest<br/>Daily 8AM: 0 8 * * *"]
        SYNC_SCHED["Integration Sync<br/>POST /internal/cron/run-syncs<br/>Daily 2AM: 0 2 * * *"]
        CLEANUP["Orphan File Cleaner<br/>POST /internal/cron/cleanup-files<br/>Weekly Sun 3AM: 0 3 * * 0"]
    end

    subgraph BACKEND_CRON["Backend API - Cron Endpoints<br/>/internal/cron/* secured with CRON_SECRET header"]
        CRON_EP["Each endpoint runs the job inline<br/>OR enqueues work to Redis for the Worker"]
    end

    subgraph QUEUE_WORKERS["Queue Worker (Python, same codebase)<br/>Consumes jobs from Redis via arq.<br/>Multiple instances compete (at-least-once)."]
        OCR_PROC["OCR Processor<br/>queue:ocr:process<br/>Concurrency: 5"]
        CSV_IMP["CSV Importer<br/>queue:csv:import<br/>Concurrency: 1"]
        EMAIL_SEND["Email Sender<br/>queue:email:send<br/>Concurrency: 10"]
        WH_PROC["Webhook Processor<br/>queue:webhook:process<br/>Concurrency: 3"]
        ACCT_SYNC["Accounting Syncer<br/>queue:sync:execute<br/>Concurrency: 1/tenant"]
    end

    subgraph AI_TRIGGERS["Post-MVP: AI Cron Triggers<br/>(Additional Hetzner Cron entries)"]
        AGENT_LOOP["Agent Decision Loop<br/>Every 1h"]
        REPLY_CHK["Reply Check<br/>Every 15m"]
        PRED_REF["Prediction Refresh<br/>Daily 3AM"]
        RISK_REF["Risk Score Refresh<br/>Daily 4AM"]
    end

    HETZNER -->|"HTTPS + CRON_SECRET"| BACKEND_CRON
    BACKEND_CRON -->|"enqueue jobs"| QUEUE_WORKERS
    AI_TRIGGERS -.->|"HTTPS + CRON_SECRET"| BACKEND_CRON
```

### 4.3 C3: Frontend (React SPA)

```mermaid
graph TB
    subgraph APP_SHELL["App Shell"]
        AUTH_PROV["Auth Provider<br/>(JWT)"]
        ROUTER["Router<br/>(React Router)"]
        TENANT_CTX["Tenant Context"]
        GLOBAL_STATE["Global State<br/>(Zustand /<br/>TanStack Query)"]
    end

    subgraph MODULES["Page Modules"]
        DASH_MOD["Dashboard Module<br/>- Stats<br/>- Overdue<br/>- Upcoming<br/>- Charts"]
        INV_MOD["Invoice Module<br/>- List / Detail<br/>- Upload / Bulk<br/>- CSV Import<br/>- Review"]
        CUST_MOD["Customer Module<br/>- List / Detail<br/>- Risk Profile"]
        SET_MOD["Settings Module<br/>- Company / SMTP<br/>- Integrations<br/>- Reminders<br/>- CSV Profiles"]
        AI_MOD["AI Hub Module<br/>(Post-MVP)<br/>- Agent Control<br/>- Insights<br/>- Forecast<br/>- Risk Overview"]
    end

    subgraph SHARED["Shared Layer"]
        API_CLI["API Client<br/>(fetch +<br/>TanStack Query)"]
        UI_LIB["UI Component<br/>Library<br/>(Shadcn / Radix)"]
        UPLOAD_COMP["Upload Component<br/>(drag-drop,<br/>progress)"]
        NOTIF_SYS["Notification System<br/>(toast, SSE<br/>listener)"]
    end

    APP_SHELL --> MODULES
    MODULES --> SHARED
```

### 4.4 C3: AI Agent Service (receivable-agents repo -- LangGraph Platform)

```mermaid
graph TB
    subgraph AGENT_SERVICE["receivable-agents repo<br/>Deployed as LangGraph Platform"]
        subgraph AGENTS["LangGraph Agents"]
            subgraph COLLECTION["Collection Agent (StateGraph)"]
                OBS["observe"] --> ANA["analyze"] --> DEC["decide"]
                DEC -->|confidence > threshold| ACT_AUTO["act_autonomously"]
                DEC -->|confidence < threshold| ESCALATE["escalate"]
                DEC -->|needs approval| ACT_HUMAN["request_approval"]
                ACT_AUTO --> LEARN["learn"]
            end

            subgraph REPLY_CLASS["Reply Classifier Agent (StateGraph)"]
                PARSE["parse_email"] --> CLASSIFY["classify_intent"] --> ROUTE["route_action"]
                ROUTE -->|payment_confirmed| H_PAY["handle_payment"]
                ROUTE -->|dispute| H_DISP["handle_dispute"]
                ROUTE -->|negotiation| H_NEG["handle_negotiation"]
                ROUTE -->|out_of_office| H_OOO["handle_ooo"]
            end
        end

        subgraph TOOLS["Tool / Skill Layer"]
            LLM_GEN["llm_generate_message"]
            LLM_CLASS["llm_classify_intent"]
            PRED_PAY["predict_payment<br/>(XGBoost)"]
            SCORE_RISK["score_risk<br/>(XGBoost)"]
            FORECAST["forecast_cashflow<br/>(Monte Carlo)"]
            DB_READ["db_read_context<br/>(read-only DB)"]
        end

        subgraph LLM_INFRA["LLM Infrastructure"]
            LLM_GW["LLM Gateway<br/>(litellm)<br/>OpenAI, Anthropic,<br/>Fallbacks"]
            MODEL_STORE["Model Store<br/>(MLflow / local pkl)"]
            PROMPT_REG["Prompt Registry<br/>(YAML / DB versioned)"]
        end
    end

    subgraph BACKEND["rcbl-backend"]
        SDK_CLIENT["langgraph-sdk Client<br/>calls agent runs via HTTP"]
    end

    SDK_CLIENT -->|"HTTP (langgraph-sdk)"| AGENT_SERVICE
    AGENTS --> TOOLS
    TOOLS --> LLM_INFRA
```

> **Key difference from v2:** The AI module is now a **separate repository** (`receivable-agents`) deployed as a **LangGraph Platform** service. The backend communicates with it exclusively via the `langgraph-sdk` Python client. The agent service has its own DB connection (read-only to the shared PostgreSQL) and its own LLM credentials.

---

## 5. Multi-Tenancy Strategy

### 5.1 Approach: Shared Database, Shared Schema, Row-Level Security

```mermaid
graph LR
    subgraph OPTIONS["Multi-Tenancy Options"]
        A["Option A:<br/>DB-per-tenant"] -->|Too expensive at scale| X["Rejected"]
        B["Option B:<br/>Schema-per-tenant"] -->|Migration headaches| X
        C["Option C:<br/>Shared + RLS"] -->|Chosen| Y["Selected"]
    end

    subgraph CHOSEN["Chosen Approach"]
        Y --> D["Every table has company_id"]
        Y --> E["PostgreSQL RLS enforces isolation"]
        Y --> F["Application sets tenant context per request"]
    end
```

### 5.2 Tenant Resolution Flow

```mermaid
sequenceDiagram
    participant Browser
    participant AuthMW as Auth Middleware
    participant TenantMW as Tenant Resolver
    participant DB as PostgreSQL (RLS)

    Browser->>AuthMW: API Request with JWT
    AuthMW->>AuthMW: Validate JWT
    AuthMW->>TenantMW: Extract company_id from claims
    TenantMW->>DB: SET LOCAL app.current_company_id = 'uuid'
    DB->>DB: RLS Policy filters rows by company_id
    DB-->>TenantMW: Query results (tenant-scoped only)
    TenantMW-->>Browser: JSON Response
    Note over DB: Connection returned to pool, setting reset
```

### 5.3 RLS Policy Pattern

```sql
-- Applied to EVERY tenant-scoped table
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON invoices
    USING (company_id = current_setting('app.current_company_id')::UUID);

CREATE POLICY tenant_insert ON invoices
    FOR INSERT
    WITH CHECK (company_id = current_setting('app.current_company_id')::UUID);
```

### 5.4 Tables with `company_id` (Direct Tenant Scope)

| Table | Tenant Column | Notes |
|-------|--------------|-------|
| `companies` | `id` (IS the tenant) | RLS not needed, accessed by ID |
| `users` | `company_id` | |
| `customers` | `company_id` | |
| `invoices` | `company_id` | |
| `reminder_sequences` | `company_id` | |
| `email_templates` | `company_id` | |
| `integration_providers` | `company_id` | |
| `invoice_upload_batches` | `company_id` | |
| `csv_import_profiles` | `company_id` | |
| `cash_flow_forecasts` | `company_id` | |

### 5.5 Tables without `company_id` (Joined via Parent)

These tables don't have their own `company_id` -- access is controlled through their parent's RLS:

| Table | Parent | Access Path |
|-------|--------|-------------|
| `payments` | `invoices.id` | Invoice already RLS-filtered |
| `reminder_events` | `invoices.id` | Invoice already RLS-filtered |
| `invoice_upload_items` | `invoice_upload_batches.id` | Batch already RLS-filtered |
| `sync_logs` | `integration_providers.id` | Integration already RLS-filtered |
| `webhook_events` | `integration_providers.id` | Integration already RLS-filtered |
| `ai_conversations` | `invoices.id` + `customers.id` | Both parents RLS-filtered |
| `ai_messages` | `ai_conversations.id` | Conversation already filtered |
| `ai_actions` | `ai_conversations.id` | Conversation already filtered |
| `payment_predictions` | `invoices.id` | Invoice already filtered |
| `customer_risk_scores` | `customers.id` | Customer already filtered |
| `ai_learning_events` | `ai_conversations.id` | Conversation already filtered |

### 5.6 Tenant Isolation Verification

```sql
-- Periodic verification query (run in CI or nightly)
-- Ensures no cross-tenant data leaks exist
SELECT
    'invoices' as table_name,
    COUNT(*) FILTER (WHERE company_id != i.company_id) as cross_tenant_violations
FROM invoices i
JOIN customers c ON c.id = i.customer_id
WHERE c.company_id != i.company_id;
-- Expected: 0 violations
```

---

## 6. Backend Architecture

### 6.1 Project Structure (Python)

```
rcbl-backend/
├── pyproject.toml                     # uv / poetry managed dependencies
├── Dockerfile
├── flyway.toml                        # Flyway config (DB URL, locations)
├── migrations/                        # Flyway SQL migrations (V{version}__{desc}.sql)
│   ├── V001__create_companies.sql
│   ├── V002__create_users.sql
│   ├── V003__create_customers.sql
│   ├── V004__create_invoices.sql
│   ├── V005__create_payments.sql
│   ├── V006__create_reminder_tables.sql
│   ├── V007__create_email_templates.sql
│   ├── V008__create_upload_tables.sql
│   ├── V009__create_integration_tables.sql
│   ├── V010__create_audit_logs.sql
│   ├── V011__enable_rls_policies.sql
│   ├── V012__create_indexes.sql
│   ├── V013__seed_defaults.sql
│   └── ...                            # Post-MVP: V100+ for AI tables
│
├── src/
│   ├── main.py                        # FastAPI app entrypoint
│   ├── worker.py                      # arq worker entrypoint
│   ├── config.py                      # Pydantic Settings (env-based)
│   │
│   ├── api/                           # HTTP layer (FastAPI routers)
│   │   ├── __init__.py
│   │   ├── deps.py                    # Dependency injection (DB session, current user, tenant)
│   │   ├── middleware/
│   │   │   ├── auth.py                # JWT validation middleware
│   │   │   ├── tenant.py              # Tenant context injection
│   │   │   ├── rate_limit.py          # slowapi + Redis rate limiting
│   │   │   └── logging.py            # structlog request logging
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── invoices.py
│   │   │   ├── customers.py
│   │   │   ├── uploads.py             # Single + bulk upload
│   │   │   ├── csv_import.py          # CSV import
│   │   │   ├── integrations.py        # Third-party sync
│   │   │   ├── webhooks.py            # Webhook receiver
│   │   │   ├── payments.py
│   │   │   ├── dashboard.py
│   │   │   ├── settings.py
│   │   │   ├── cron.py                # /internal/cron/* endpoints (Hetzner calls these)
│   │   │   └── ai_router.py           # /api/ai/* routes (Post-MVP, calls agents via SDK)
│   │   └── schemas/                   # Pydantic request/response models
│   │       ├── invoice.py
│   │       ├── customer.py
│   │       ├── upload.py
│   │       └── ...
│   │
│   ├── services/                      # Business logic
│   │   ├── __init__.py
│   │   ├── invoice_service.py
│   │   ├── customer_service.py
│   │   ├── upload_service.py          # OCR orchestration, batch mgmt
│   │   ├── csv_import_service.py      # CSV parsing, mapping, import
│   │   ├── integration_service.py     # OAuth, sync engine
│   │   ├── reminder_service.py
│   │   ├── payment_service.py
│   │   ├── notification_service.py    # Email sending
│   │   ├── dashboard_service.py
│   │   └── ai_service.py             # Post-MVP: orchestrates calls to LangGraph Platform via SDK
│   │
│   ├── integrations/                  # Third-party adapters
│   │   ├── __init__.py
│   │   ├── base.py                    # AccountingProvider ABC
│   │   ├── sevdesk.py
│   │   ├── xero.py
│   │   ├── lexoffice.py
│   │   └── webhook.py
│   │
│   ├── jobs/                          # arq job handlers (consumed by worker)
│   │   ├── __init__.py
│   │   ├── ocr_processor.py
│   │   ├── csv_importer.py
│   │   ├── email_sender.py
│   │   ├── sync_executor.py
│   │   ├── webhook_processor.py
│   │   └── ai_jobs.py                 # Post-MVP: dispatches agent runs via langgraph-sdk
│   │
│   ├── db/                            # Database layer
│   │   ├── __init__.py
│   │   ├── session.py                 # AsyncSession factory + tenant context
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── base.py               # DeclarativeBase + common mixins
│   │   │   ├── company.py
│   │   │   ├── user.py
│   │   │   ├── customer.py
│   │   │   ├── invoice.py
│   │   │   ├── payment.py
│   │   │   ├── reminder.py
│   │   │   ├── upload.py
│   │   │   ├── integration.py
│   │   │   └── ai_models.py          # Post-MVP: AI conversation, prediction tables
│   │   └── repositories/             # Query layer (thin wrapper around ORM)
│   │       ├── invoice_repo.py
│   │       ├── customer_repo.py
│   │       └── ...
│   │
│   ├── clients/                       # External service clients
│   │   ├── __init__.py
│   │   ├── ocr_client.py             # httpx → OpenAI Vision / Textract
│   │   ├── email_client.py           # aiosmtplib / SES SDK
│   │   ├── s3_client.py              # aioboto3 / boto3
│   │   └── langgraph_client.py       # langgraph-sdk client (Post-MVP, calls agent service)
│   │
│   ├── core/                          # Cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── security.py               # JWT encode/decode, password hashing
│   │   ├── crypto.py                 # AES-256-GCM for token encryption
│   │   ├── tenant.py                 # Tenant context manager
│   │   └── feature_flags.py          # Feature flag checker
│   │
│   └── # NOTE: No src/ai/ directory -- all AI agent code lives in receivable-agents repo
│
├── tests/
│   ├── conftest.py
│   ├── test_invoices.py
│   ├── test_uploads.py
│   └── ...
```

### 6.2 Request Lifecycle

```mermaid
graph TD
    A["HTTP Request"] --> B["TLS Termination<br/>(Caddy / Fly Proxy)"]
    B --> C["Rate Limiter<br/>(slowapi + Redis)<br/>per IP + per tenant<br/>→ 429 if exceeded"]
    C --> D["Auth Middleware<br/>Validate JWT (python-jose)<br/>Extract user_id + company_id<br/>→ 401 if invalid"]
    D --> E["Tenant Resolver<br/>Sets company_id in request state<br/>DB session executes<br/>SET LOCAL app.current_company_id"]
    E --> F["FastAPI Route Handler<br/>Calls service layer"]
    F --> G["Service Layer<br/>Business logic, Pydantic validation<br/>Enqueues jobs to arq/Redis if async"]
    G --> H["DB Query (with RLS)<br/>SQLAlchemy async query<br/>Tenant can ONLY touch their own data"]
    H --> I["JSON Response<br/>Pydantic model serialization"]
```

### 6.3 Key Python Packages

| Package | Purpose |
|---------|---------|
| `fastapi` | HTTP framework (ASGI) |
| `uvicorn` | ASGI server |
| `pydantic` + `pydantic-settings` | Validation, config, schemas |
| `sqlalchemy[asyncio]` + `asyncpg` | Async ORM + PostgreSQL driver |
| `python-jose[cryptography]` | JWT encode/decode |
| `passlib[bcrypt]` | Password hashing |
| `redis` + `arq` | Redis client + async job queue |
| `httpx` | Async HTTP client for external APIs |
| `aiosmtplib` | Async email sending |
| `aioboto3` | Async S3/MinIO client |
| `slowapi` | Rate limiting middleware |
| `structlog` | Structured logging |
| `cryptography` | AES-256-GCM for token encryption |
| `python-multipart` | File upload handling |
| `openpyxl` | XLSX parsing |
| `langgraph` | AI agent framework (Post-MVP) |
| `langgraph-sdk` | LangGraph Platform Python client (Post-MVP) |
| `scikit-learn` / `xgboost` | ML models -- used in `receivable-agents` repo (Post-MVP) |
| `pytest` + `pytest-asyncio` | Testing |
| `ruff` | Linting + formatting |

---

## 7. Frontend Architecture

### 7.1 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Framework** | React 18 + TypeScript | Mature ecosystem, hire-able talent |
| **Build** | Vite | Fast dev server, optimized builds |
| **Styling** | TailwindCSS + Shadcn/ui | Consistent design, rapid prototyping |
| **State** | TanStack Query (server state) + Zustand (client state) | Cache-first data fetching, minimal boilerplate |
| **Routing** | React Router v6 | Standard, file-based-ready |
| **Forms** | React Hook Form + Zod | Validation-first forms |
| **Charts** | Recharts | Simple, React-native charting |
| **File Upload** | react-dropzone | Drag-and-drop, progress tracking |
| **Real-time** | EventSource (SSE) | Simpler than WebSocket for progress updates |
| **Testing** | Vitest + React Testing Library | Fast, Vite-native |

### 7.2 Project Structure

```
rcbl-frontend/
├── package.json
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── index.html
├── public/
│   └── favicon.svg
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/
│   │   ├── client.ts
│   │   ├── invoices.ts
│   │   ├── customers.ts
│   │   ├── uploads.ts
│   │   ├── csv-import.ts
│   │   ├── integrations.ts
│   │   ├── payments.ts
│   │   ├── dashboard.ts
│   │   ├── settings.ts
│   │   └── ai.ts                   # Post-MVP
│   ├── hooks/
│   │   ├── useInvoices.ts
│   │   ├── useUpload.ts
│   │   ├── useSSE.ts
│   │   └── ...
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── InvoiceList.tsx
│   │   ├── InvoiceDetail.tsx
│   │   ├── InvoiceUpload.tsx
│   │   ├── InvoiceCSVImport.tsx
│   │   ├── BatchReviewQueue.tsx
│   │   ├── CustomerList.tsx
│   │   ├── CustomerDetail.tsx
│   │   ├── Settings.tsx
│   │   ├── Integrations.tsx
│   │   ├── SyncHistory.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── ai/                     # Post-MVP
│   │   │   ├── AgentDashboard.tsx
│   │   │   ├── ConversationDetail.tsx
│   │   │   ├── InsightsHub.tsx
│   │   │   └── CashFlowForecast.tsx
│   │   └── NotFound.tsx
│   ├── components/
│   │   ├── ui/
│   │   ├── layout/
│   │   ├── invoice/
│   │   ├── upload/
│   │   └── charts/
│   ├── stores/
│   ├── lib/
│   └── types/
└── tests/
```

---

## 8. Cron & Background Jobs

### 8.1 Architecture: Hetzner Cron Jobs + arq Workers

There are **two kinds** of background work:

1. **Scheduled jobs (cron)** -- triggered by Hetzner Cron Jobs calling HTTP endpoints on the backend
2. **Queue jobs (async)** -- enqueued by API handlers, consumed by arq worker processes

```mermaid
graph LR
    subgraph HETZNER["Hetzner Cron Jobs"]
        H1["0 */6 * * *<br/>update-statuses"]
        H2["0 */4 * * *<br/>send-reminders"]
        H3["0 8 * * *<br/>daily-digest"]
        H4["0 2 * * *<br/>run-syncs"]
        H5["0 3 * * 0<br/>cleanup-files"]
    end

    subgraph BACKEND["Backend API<br/>/internal/cron/* endpoints"]
        CE["Cron endpoint handler<br/>Validates CRON_SECRET<br/>Runs job or enqueues to Redis"]
    end

    subgraph REDIS["Redis (arq queues)"]
        Q1["queue:ocr:process"]
        Q2["queue:csv:import"]
        Q3["queue:email:send"]
        Q4["queue:sync:execute"]
        Q5["queue:webhook:process"]
    end

    subgraph WORKER["arq Worker Process(es)"]
        W1["ocr_processor"]
        W2["csv_importer"]
        W3["email_sender"]
        W4["sync_executor"]
        W5["webhook_processor"]
    end

    HETZNER -->|"HTTPS POST<br/>+ CRON_SECRET header"| BACKEND
    BACKEND -->|"enqueue"| REDIS
    REDIS --> WORKER
```

### 8.2 Hetzner Cron Endpoint Security

Every `/internal/cron/*` endpoint is protected:

```python
# src/api/routers/cron.py
from fastapi import APIRouter, Header, HTTPException
from src.config import settings

router = APIRouter(prefix="/internal/cron", tags=["cron"])

async def verify_cron_secret(x_cron_secret: str = Header(...)):
    if x_cron_secret != settings.CRON_SECRET:
        raise HTTPException(status_code=403, detail="Invalid cron secret")

@router.post("/update-statuses", dependencies=[Depends(verify_cron_secret)])
async def update_statuses(db: AsyncSession = Depends(get_db)):
    """Called by Hetzner every 6 hours."""
    await invoice_service.update_all_statuses(db)
    return {"status": "ok", "job": "update-statuses"}

@router.post("/send-reminders", dependencies=[Depends(verify_cron_secret)])
async def send_reminders(db: AsyncSession = Depends(get_db)):
    """Called by Hetzner every 4 hours. Enqueues individual emails to arq."""
    count = await reminder_service.enqueue_pending_reminders(db)
    return {"status": "ok", "enqueued": count}
```

### 8.3 Hetzner Cron Configuration

Each cron entry in Hetzner dashboard:

| Job Name | Schedule | HTTP Method | URL | Header |
|----------|----------|-------------|-----|--------|
| update-statuses | `0 */6 * * *` | POST | `https://api.rcbl.app/internal/cron/update-statuses` | `X-Cron-Secret: <secret>` |
| send-reminders | `0 */4 * * *` | POST | `https://api.rcbl.app/internal/cron/send-reminders` | `X-Cron-Secret: <secret>` |
| daily-digest | `0 8 * * *` | POST | `https://api.rcbl.app/internal/cron/daily-digest` | `X-Cron-Secret: <secret>` |
| run-syncs | `0 2 * * *` | POST | `https://api.rcbl.app/internal/cron/run-syncs` | `X-Cron-Secret: <secret>` |
| cleanup-files | `0 3 * * 0` | POST | `https://api.rcbl.app/internal/cron/cleanup-files` | `X-Cron-Secret: <secret>` |

**Post-MVP additions:**

| Job Name | Schedule | URL |
|----------|----------|-----|
| agent-decision-loop | `0 * * * *` | `/internal/cron/agent-decision-loop` |
| reply-check | `*/15 * * * *` | `/internal/cron/reply-check` |
| prediction-refresh | `0 3 * * *` | `/internal/cron/prediction-refresh` |
| risk-score-refresh | `0 4 * * *` | `/internal/cron/risk-score-refresh` |
| cashflow-forecast | `0 5 * * *` | `/internal/cron/cashflow-forecast` |
| learning-processor | `0 6 * * *` | `/internal/cron/learning-processor` |
| model-retrain | `0 2 * * 0` | `/internal/cron/model-retrain` |

### 8.4 arq Worker Configuration

```python
# src/worker.py
from arq import create_pool
from arq.connections import RedisSettings
from src.jobs.ocr_processor import process_ocr
from src.jobs.csv_importer import import_csv
from src.jobs.email_sender import send_email
from src.jobs.sync_executor import execute_sync
from src.jobs.webhook_processor import process_webhook
from src.config import settings

class WorkerSettings:
    functions = [
        process_ocr,
        import_csv,
        send_email,
        execute_sync,
        process_webhook,
    ]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 10
    job_timeout = 300  # 5 minutes default
```

Start the worker:
```bash
# Start arq worker (separate process from API)
arq src.worker.WorkerSettings
```

### 8.5 Job Schedule (MVP)

| Job | Type | Trigger | Concurrency | Timeout |
|-----|------|---------|-------------|---------|
| **OCR Processor** | arq queue | API enqueue | 5 per worker | 30s |
| **CSV Importer** | arq queue | API enqueue | 1 per worker | 5min |
| **Email Sender** | arq queue | API/cron enqueue | 10 per worker | 10s |
| **Webhook Processor** | arq queue | API enqueue | 3 per worker | 10s |
| **Accounting Sync** | arq queue | Cron enqueue | 1 per tenant | 5min |
| **Invoice Status Updater** | Hetzner cron | Every 6h | 1 (HTTP call) | 2min |
| **Reminder Scheduler** | Hetzner cron | Every 4h | 1 (HTTP call) | 5min |
| **Daily Digest** | Hetzner cron | Daily 8AM | 1 (HTTP call) | 10min |
| **Orphan File Cleaner** | Hetzner cron | Weekly Sun 3AM | 1 (HTTP call) | 30min |

> **No leader election needed.** Hetzner calls the endpoint exactly once. If the API is behind a load balancer, only one instance handles the request. Idempotency guards in each handler prevent double processing.

---

## 9. AI Agent Architecture (LangGraph Platform -- Separate Repo)

### 9.1 Why LangGraph Platform (Separate Service)

| Concern | LangGraph Platform Advantage |
|---------|-------------------|
| **Stateful agents** | StateGraph persists conversation state across runs via built-in checkpointing |
| **Human-in-the-loop** | Built-in interrupt/resume for approval workflows |
| **Branching logic** | Conditional edges for escalation/autonomous paths |
| **Tool calling** | Native tool integration for DB queries, email, etc. |
| **Checkpointing** | State saved/loaded from PostgreSQL (managed by LangGraph Platform) |
| **Observability** | LangSmith integration for tracing and debugging |
| **Independent deployment** | Agent code evolves on its own release cycle |
| **Independent scaling** | Scale AI workloads without touching the backend |
| **SDK communication** | Backend calls agents via `langgraph-sdk` (Python HTTP client) |

### 9.2 Architecture: AI as a Separate Service

```mermaid
graph LR
    subgraph BACKEND_REPO["rcbl-backend repo"]
        direction TB
        API["Backend API (FastAPI)<br/>- All CRUD<br/>- Auth + Tenancy<br/>- File storage<br/>- Email sending<br/>- Cron endpoints"]
        SDK["langgraph-sdk Client<br/>(src/clients/langgraph_client.py)<br/>- create_run()<br/>- wait_for_result()<br/>- stream_events()"]
        WORKER["arq Worker<br/>- OCR, CSV, Email<br/>- AI job dispatch via SDK"]
    end

    subgraph AGENT_REPO["receivable-agents repo"]
        direction TB
        PLATFORM["LangGraph Platform<br/>(langgraph-api server)"]
        AGENTS["Agent Graphs<br/>- Collection Agent<br/>- Reply Classifier"]
        TOOLS["Tools + Models<br/>- LLM, Prediction<br/>- DB read-only"]
    end

    API --> SDK
    WORKER --> SDK
    SDK -->|"HTTP (langgraph-sdk)"| PLATFORM
    PLATFORM --> AGENTS
    AGENTS --> TOOLS

    style AGENT_REPO fill:#f0f9ff,stroke:#3b82f6,stroke-width:2px
```

The backend and agents are **two separate Python codebases** in **two separate repositories**:
- **`rcbl-backend`** -- owns all business logic, auth, tenancy, CRUD, jobs. Calls agents via `langgraph-sdk`.
- **`receivable-agents`** -- owns all LangGraph agent graphs, ML models, LLM gateway, prompt templates. Deployed as a LangGraph Platform service.

### 9.3 receivable-agents Repository Structure

```
receivable-agents/
├── pyproject.toml                     # uv / poetry managed dependencies
├── Dockerfile
├── langgraph.json                     # LangGraph Platform config (graphs, env)
│
├── src/
│   ├── agents/
│   │   ├── collection_agent.py        # LangGraph Collection StateGraph
│   │   ├── reply_classifier.py        # LangGraph Reply Classifier StateGraph
│   │   └── nodes/                     # Individual graph nodes
│   │       ├── observe.py
│   │       ├── analyze.py
│   │       ├── decide.py
│   │       ├── act.py
│   │       ├── escalate.py
│   │       └── learn.py
│   ├── tools/                         # LangGraph tools (DB read, LLM, predictions)
│   │   ├── db_tools.py                # Read-only DB queries for context
│   │   ├── llm_tools.py
│   │   └── prediction_tools.py
│   ├── models/                        # ML models
│   │   ├── payment_predictor.py
│   │   ├── risk_scorer.py
│   │   ├── cash_flow_forecaster.py
│   │   └── model_store.py
│   ├── prompts/                       # Prompt templates (YAML)
│   │   ├── collection_friendly.yaml
│   │   ├── collection_firm.yaml
│   │   └── reply_classification.yaml
│   └── llm/
│       ├── gateway.py                 # litellm LLM gateway
│       ├── prompt_registry.py
│       └── cost_tracker.py
│
├── trained_models/                    # Serialized ML model files
│   ├── payment_predictor_v1.pkl
│   └── risk_scorer_v1.pkl
│
└── tests/
    ├── test_collection_agent.py
    └── test_reply_classifier.py
```

### 9.4 Backend → Agent Communication via langgraph-sdk

The backend calls the LangGraph Platform using the official `langgraph-sdk` Python client:

```python
# rcbl-backend/src/clients/langgraph_client.py

from langgraph_sdk import get_client
from src.config import settings

class AgentClient:
    def __init__(self):
        self.client = get_client(url=settings.LANGGRAPH_API_URL)

    async def run_collection_agent(self, invoice_context: dict) -> dict:
        """Invoke the collection agent graph and wait for result."""
        thread = await self.client.threads.create()
        run = await self.client.runs.create(
            thread_id=thread["thread_id"],
            assistant_id="collection_agent",
            input=invoice_context,
        )
        # Wait for the run to complete
        result = await self.client.runs.join(
            thread_id=thread["thread_id"],
            run_id=run["run_id"],
        )
        return result

    async def run_reply_classifier(self, email_data: dict) -> dict:
        """Invoke the reply classifier graph and wait for result."""
        thread = await self.client.threads.create()
        run = await self.client.runs.create(
            thread_id=thread["thread_id"],
            assistant_id="reply_classifier",
            input=email_data,
        )
        result = await self.client.runs.join(
            thread_id=thread["thread_id"],
            run_id=run["run_id"],
        )
        return result

    async def stream_agent_events(self, thread_id: str, run_id: str):
        """Stream events from an agent run (for SSE to frontend)."""
        async for event in self.client.runs.stream(
            thread_id=thread_id,
            run_id=run_id,
        ):
            yield event
```

### 9.5 Collection Agent Graph (in receivable-agents repo)

```python
# receivable-agents/src/agents/collection_agent.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver

class CollectionState(TypedDict):
    invoice_id: str
    company_id: str
    customer_id: str
    conversation_id: str
    invoice_context: dict
    payment_probability: float
    customer_risk_score: int
    ai_confidence: float
    recommended_action: str
    generated_message: str | None
    requires_approval: bool
    human_decision: str | None

graph = StateGraph(CollectionState)

graph.add_node("observe",          observe_context)
graph.add_node("analyze",          analyze_situation)
graph.add_node("decide",           decide_action)
graph.add_node("act_autonomous",   act_autonomously)
graph.add_node("request_approval", request_human_approval)
graph.add_node("escalate",         escalate_to_human)
graph.add_node("learn",            record_learning_signal)

graph.set_entry_point("observe")
graph.add_edge("observe", "analyze")
graph.add_edge("analyze", "decide")

graph.add_conditional_edges("decide", route_decision, {
    "autonomous": "act_autonomous",
    "approval":   "request_approval",
    "escalate":   "escalate",
})

graph.add_edge("act_autonomous", "learn")
graph.add_edge("request_approval", END)
graph.add_edge("escalate", END)
graph.add_edge("learn", END)

checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)
collection_agent = graph.compile(checkpointer=checkpointer)
```

### 9.6 Reply Classifier Graph (in receivable-agents repo)

```python
# receivable-agents/src/agents/reply_classifier.py

graph = StateGraph(ReplyClassificationState)

graph.add_node("parse_email",      parse_incoming_email)
graph.add_node("classify_intent",  classify_with_llm)
graph.add_node("extract_entities", extract_dates_amounts)
graph.add_node("route_action",     determine_next_action)

graph.set_entry_point("parse_email")
graph.add_edge("parse_email", "classify_intent")
graph.add_edge("classify_intent", "extract_entities")
graph.add_edge("extract_entities", "route_action")

graph.add_conditional_edges("route_action", route_by_intent, {
    "payment_confirmed": "handle_payment_confirmation",
    "payment_promise":   "handle_payment_promise",
    "dispute":           "handle_dispute",
    "info_request":      "handle_info_request",
    "negotiation":       "handle_negotiation",
    "out_of_office":     "handle_ooo",
    "unrelated":         "handle_unrelated",
})
```

### 9.7 LLM Gateway Pattern (in receivable-agents repo)

```python
# receivable-agents/src/llm/gateway.py
from litellm import completion

class LLMGateway:
    def __init__(self, config: LLMConfig):
        self.primary = config.primary_model      # "gpt-4o"
        self.fallback = config.fallback_model    # "claude-3-5-sonnet"
        self.cache = RedisCache(config.redis_url)

    async def generate(self, prompt: str, **kwargs) -> str:
        cache_key = hash(prompt + str(kwargs))
        if cached := await self.cache.get(cache_key):
            return cached

        try:
            response = await completion(
                model=self.primary,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
        except Exception:
            response = await completion(
                model=self.fallback,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

        result = response.choices[0].message.content
        await self.cache.set(cache_key, result, ttl=3600)
        return result
```

---

## 10. Data Layer

### 10.1 Database Architecture

```mermaid
graph TB
    subgraph PG_TOPOLOGY["PostgreSQL Topology"]
        PRIMARY["PRIMARY (Read/Write)<br/><br/>- All writes go here<br/>- Backend API connects<br/>- arq Worker connects<br/>- RLS enforced"]
        REPLICA["READ REPLICA (Post-MVP)<br/><br/>- Heavy dashboard queries<br/>- Analytics queries<br/>- ML feature extraction"]

        PRIMARY -->|"Streaming<br/>Replication"| REPLICA
    end

    subgraph POOLING["Connection Pooling"]
        API_POOL["Backend API: asyncpg pool<br/>(max 20 conns per instance)"]
        WORKER_POOL["Worker: asyncpg pool<br/>(max 10 conns per instance)"]
        AGENT_POOL["Agent Service: asyncpg pool<br/>(max 5 conns, read-only)"]
        PGBOUNCER["Consider PgBouncer at<br/>50+ concurrent connections"]
    end

    API_POOL --> PRIMARY
    WORKER_POOL --> PRIMARY
    AGENT_POOL --> PRIMARY
```

### 10.2 Schema Organization

All tables live in the `public` schema. Logical grouping:

| Group | Tables | Phase |
|-------|--------|-------|
| **Tenant** | `companies`, `users` | MVP |
| **Core AR** | `customers`, `invoices`, `payments`, `reminder_events`, `reminder_sequences`, `email_templates` | MVP |
| **Ingestion** | `invoice_upload_batches`, `invoice_upload_items`, `csv_import_profiles` | MVP |
| **Integration** | `integration_providers`, `sync_logs`, `webhook_events` | MVP |
| **AI Conversation** | `ai_conversations`, `ai_messages`, `ai_actions` | Post-MVP |
| **AI Prediction** | `payment_predictions`, `customer_risk_scores`, `cash_flow_forecasts` | Post-MVP |
| **AI Learning** | `ai_learning_events` | Post-MVP |
| **System** | `audit_logs`, `feature_flags`, `system_metrics` | MVP (audit), Post-MVP (flags) |

### 10.3 Migration Strategy

Use **Flyway** (language-agnostic, plain SQL migrations):

```bash
# Run all pending migrations
flyway migrate

# Check current migration status
flyway info

# Validate applied migrations against local files
flyway validate

# Repair metadata table (fix failed migrations)
flyway repair
```

**Migration naming convention:** `V{version}__{description}.sql` (double underscore required)

```
migrations/
├── V001__create_companies.sql
├── V002__create_users.sql
├── V003__create_customers.sql
├── V004__create_invoices.sql
├── V005__create_payments.sql
├── V006__create_reminder_tables.sql
├── V007__create_email_templates.sql
├── V008__create_upload_tables.sql
├── V009__create_integration_tables.sql
├── V010__create_audit_logs.sql
├── V011__enable_rls_policies.sql
├── V012__create_indexes.sql
├── V013__seed_defaults.sql
│
│   ── Post-MVP migrations (V100+ reserved for AI) ──
├── V100__create_ai_conversations.sql
├── V101__create_ai_messages.sql
├── V102__create_ai_actions.sql
├── V103__create_prediction_tables.sql
├── V104__create_learning_tables.sql
├── V105__add_ai_columns_to_invoices.sql
├── V106__add_ai_columns_to_customers.sql
└── V107__create_feature_flags.sql
```

**Flyway config (`flyway.toml`):**
```toml
[flyway]
url = "jdbc:postgresql://localhost:5432/rcbl"
user = "rcbl"
locations = ["filesystem:./migrations"]
schemas = ["public"]
baselineOnMigrate = true
```

> **Why Flyway over Alembic:** Migrations are pure SQL -- no Python dependency, reviewable by anyone, and can be run independently of the application. Flyway also tracks migration history in a `flyway_schema_history` table for auditability.

### 10.4 Caching Strategy (Redis)

| Cache Key Pattern | TTL | Purpose |
|-------------------|-----|---------|
| `cache:dashboard:{company_id}` | 5 min | Dashboard stats |
| `cache:invoice_list:{company_id}:{filters_hash}` | 2 min | Invoice list queries |
| `cache:customer:{customer_id}` | 10 min | Customer profile |
| `cache:ocr:{file_hash}` | 24h | OCR results for duplicate files |
| `cache:llm:{prompt_hash}` | 1h | LLM response cache |
| `ratelimit:{company_id}:{endpoint}` | Sliding window | API rate limiting |
| `ratelimit:ocr:{company_id}` | Monthly window | OCR usage limits |

---

## 11. Infrastructure & Deployment

### 11.1 MVP Deployment (Single Region)

```mermaid
graph TB
    subgraph DEPLOY["Deployment Topology (MVP + Post-MVP)"]
        API["Python Backend API<br/>(2 instances, uvicorn)<br/>rcbl-backend repo"]
        WORKER["Python arq Worker<br/>(1 instance)<br/>rcbl-backend repo"]
        AGENT["LangGraph Platform<br/>(1 instance, Post-MVP)<br/>receivable-agents repo"]

        PG["Managed PostgreSQL<br/>(Neon / Supabase / Fly Postgres)"]
        REDIS["Managed Redis<br/>(Upstash / Fly Redis)"]
        OBJ["Object Storage<br/>(Tigris / S3 / MinIO)"]
    end

    HETZNER["Hetzner Cron Jobs<br/>(external, managed)"]

    API --> PG
    API --> REDIS
    API --> OBJ
    API -->|"langgraph-sdk"| AGENT
    WORKER --> PG
    WORKER --> REDIS
    WORKER --> OBJ
    WORKER -->|"langgraph-sdk"| AGENT
    AGENT -->|"read-only"| PG
    HETZNER -->|"HTTPS + secret"| API
```

### 11.2 Docker Compose (Local Development)

```yaml
# docker-compose.yml
services:
  api:
    build: ./rcbl-backend
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    ports: ["8000:8000"]
    depends_on: [postgres, redis, minio]
    environment:
      DATABASE_URL: postgresql+asyncpg://rcbl:rcbl@postgres:5432/rcbl
      REDIS_URL: redis://redis:6379
      S3_ENDPOINT: http://minio:9000
      CRON_SECRET: dev-secret-change-me
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      LANGGRAPH_API_URL: http://agent:8123  # Post-MVP: connect to agent service

  worker:
    build: ./rcbl-backend
    command: arq src.worker.WorkerSettings
    depends_on: [postgres, redis, minio]
    environment:  # same as api
      DATABASE_URL: postgresql+asyncpg://rcbl:rcbl@postgres:5432/rcbl
      REDIS_URL: redis://redis:6379
      S3_ENDPOINT: http://minio:9000
      LANGGRAPH_API_URL: http://agent:8123

  # Post-MVP: LangGraph Platform agent service (receivable-agents repo)
  agent:
    build: ./receivable-agents
    command: langgraph up --host 0.0.0.0 --port 8123
    ports: ["8123:8123"]
    depends_on: [postgres]
    environment:
      DATABASE_URL: postgresql+asyncpg://rcbl:rcbl@postgres:5432/rcbl  # read-only access
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}

  frontend:
    build: ./rcbl-frontend
    ports: ["3000:3000"]

  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: rcbl
      POSTGRES_PASSWORD: rcbl
      POSTGRES_DB: rcbl
    volumes: [pgdata:/var/lib/postgresql/data]
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    volumes: [minio-data:/data]
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin

  flyway:
    image: flyway/flyway:10
    command: migrate
    depends_on: [postgres]
    volumes:
      - ./migrations:/flyway/sql
    environment:
      FLYWAY_URL: jdbc:postgresql://postgres:5432/rcbl
      FLYWAY_USER: rcbl
      FLYWAY_PASSWORD: rcbl
      FLYWAY_BASELINE_ON_MIGRATE: "true"

volumes:
  pgdata:
  minio-data:
```

> **Local cron testing:** Use `curl` or a simple script to hit cron endpoints locally:
> ```bash
> curl -X POST http://localhost:8000/internal/cron/update-statuses \
>   -H "X-Cron-Secret: dev-secret-change-me"
> ```

### 11.3 CI/CD Pipeline

```mermaid
graph TD
    A["PR Opened / Push to main"] --> B["Lint + Format<br/>ruff check, ruff format --check (backend)<br/>eslint, prettier (frontend)<br/>ruff check (agents)"]
    B --> C["Unit Tests<br/>pytest (backend + agents)<br/>vitest (frontend)"]
    C --> D["Integration Tests<br/>Docker Compose + test DB<br/>API endpoint tests<br/>Agent graph tests"]
    D --> E["Build<br/>Docker images (backend, agents, frontend)<br/>Frontend static build"]
    E --> F["Deploy<br/>Fly deploy / Railway deploy<br/>Run flyway migrate<br/>Deploy agent service<br/>Health check"]
```

---

## 12. Security Architecture

### 12.1 Authentication Flow

```mermaid
sequenceDiagram
    participant User as Browser
    participant API as Python Backend
    participant DB as PostgreSQL

    User->>API: POST /api/auth/login (email + password)
    API->>DB: Verify password (bcrypt via passlib)
    DB-->>API: User record
    API->>API: Issue JWT (python-jose, HS256 or Ed25519)
    Note right of API: JWT contains: sub (user-uuid),<br/>company_id (tenant-uuid),<br/>email, iat, exp (24h)
    API-->>User: Set httpOnly cookie with JWT
    User->>API: Subsequent API request (cookie included)
    API->>API: Middleware validates JWT
    API->>DB: SET LOCAL app.current_company_id
    DB-->>API: RLS-filtered query results
    API-->>User: JSON response

    Note over User,API: Refresh: Issue new JWT before<br/>expiry via /api/auth/refresh
```

### 12.2 Security Layers

| Layer | Mechanism | What It Protects |
|-------|-----------|-----------------|
| **Transport** | TLS 1.3 (Caddy auto-cert) | Data in transit |
| **Authentication** | JWT (python-jose) + httpOnly cookies | Identity verification |
| **Authorization** | Tenant context from JWT → RLS | Cross-tenant access |
| **Rate Limiting** | slowapi + Redis sliding window (per tenant + per IP) | Abuse / DoS |
| **Input Validation** | Zod (frontend) + Pydantic (backend) | Injection attacks |
| **SQL Injection** | SQLAlchemy parameterized queries | DB attacks |
| **XSS** | React auto-escaping + CSP headers | Script injection |
| **CSRF** | SameSite cookies + custom header check | Cross-site requests |
| **File Upload** | Type validation, size limits, virus scan (ClamAV optional) | Malicious uploads |
| **Secret Storage** | cryptography (AES-256-GCM) for OAuth tokens, env vars for API keys | Credential leaks |
| **Cron Security** | CRON_SECRET header on /internal/cron/* endpoints | Unauthorized job triggers |
| **Audit** | Every mutation logged with user_id + timestamp | Compliance |

### 12.3 Webhook Security

```
Inbound webhooks (from accounting systems):
  1. Verify signature header (HMAC-SHA256)
  2. Check timestamp (reject if > 5 min old)
  3. Validate API key from header
  4. Rate limit: 100 req/min per company
  5. Idempotency: check event ID for duplicates

Outbound webhooks (future):
  1. Sign payload with company's webhook secret
  2. Include timestamp in signature
  3. Retry with exponential backoff (3 attempts)
```

---

## 13. Scalability Playbook

### 13.1 Scaling Triggers and Actions

| Metric | Threshold | Action |
|--------|-----------|--------|
| API p99 latency > 500ms | Sustained 5 min | Add API instance |
| Worker queue depth > 100 | Sustained 10 min | Add Worker instance |
| Agent p99 latency > 2s | Sustained 5 min | Add Agent instance |
| PostgreSQL CPU > 70% | Sustained 15 min | Add read replica OR upgrade instance |
| Redis memory > 80% | Sustained | Increase instance size OR add eviction policy |
| OCR queue wait > 30s | Sustained | Increase OCR concurrency OR add Worker |

### 13.2 Phase-by-Phase Scaling

**Phase 1: MVP (0-100 tenants, 0-50K invoices)**
```
- 2x Python API instances (512MB-1GB each, uvicorn)
- 1x Python arq Worker instance (512MB)
- 1x PostgreSQL (2GB RAM, 20GB storage)
- 1x Redis (256MB)
- 1x MinIO or Tigris bucket
- Hetzner Cron Jobs (free / minimal cost)
- Total: ~$50-100/month
```

**Phase 2: Growth (100-1,000 tenants, 50K-500K invoices)**
```
- 3-4x Python API instances (1GB each)
- 2x Python arq Worker instances (1GB each)
- 1x LangGraph Platform (agent service, 1GB, receivable-agents repo)
- 1x PostgreSQL (4GB RAM, 100GB) + 1x read replica
- 1x Redis (512MB)
- PgBouncer for connection pooling
- Total: ~$200-400/month
```

**Phase 3: Scale (1,000-10,000 tenants, 500K-5M invoices)**
```
- 4-8x Python API (2GB each, behind load balancer)
- 3-4x Python Workers (2GB each)
- 2-4x LangGraph Platform instances (independently scaled)
- PostgreSQL: Primary (8GB) + 2x read replicas
- Redis Cluster (3 nodes)
- CDN for frontend assets
- Table partitioning for reminder_events, ai_messages, sync_logs
- Total: ~$800-1,500/month
```

### 13.3 What Does NOT Need to Scale (MVP)

- **Frontend:** Static files on CDN, scales infinitely
- **File Storage:** S3/MinIO is effectively unlimited
- **Cron:** Hetzner handles scheduling; just one HTTP call per trigger
- **Agent Service:** Not deployed in MVP; only added Post-MVP
- **Database Writes:** PostgreSQL handles 10K+ writes/sec on modest hardware; not a concern until Phase 3

---

## 14. MVP vs Post-MVP Boundary

### 14.1 Clear Deployment Separation

```mermaid
graph TB
    subgraph MVP["MVP Deployment (Weeks 1-8)"]
        direction LR
        M1["Frontend<br/>(React)"]
        M2["Python API<br/>(FastAPI)<br/>rcbl-backend"]
        M3["Python Worker<br/>(arq)<br/>rcbl-backend"]
        M4["PostgreSQL"]
        M5["Redis"]
        M6["Hetzner Cron"]
    end

    subgraph POSTMVP["Post-MVP Deployment (Weeks 13+)"]
        direction LR
        P1["Frontend<br/>(React)"]
        P2["Python API<br/>(FastAPI + SDK client)<br/>rcbl-backend"]
        P3["Python Worker<br/>(arq + AI dispatch)<br/>rcbl-backend"]
        P4["LangGraph Platform<br/>(Agent Service)<br/>receivable-agents"]
        P5["PostgreSQL<br/>+ Replica"]
        P6["Redis"]
        P7["Hetzner Cron<br/>(+ AI cron entries)"]
    end
```

> **MVP:** Backend and agents are separate repos, but only the backend is deployed for MVP. No LLM API keys needed. No agent service. Just FastAPI + React + PostgreSQL + Redis + S3 + Hetzner Cron.

> **Post-MVP:** Deploy the `receivable-agents` service alongside the backend. Enable feature flags, add LLM API keys, configure `LANGGRAPH_API_URL` in backend env. The backend now calls agents via SDK.

### 14.2 Feature Flag Gating

All AI features are behind feature flags, enabled per tenant:

```sql
INSERT INTO feature_flags (flag_name, enabled, rollout_percentage) VALUES
('ai_collection_agent',  false, 0),
('ai_payment_prediction', false, 0),
('ai_risk_scoring',      false, 0),
('ai_cash_flow_forecast', false, 0),
('ai_message_generation', false, 0);
```

The backend checks flags before calling the agent service:

```python
# rcbl-backend/src/core/feature_flags.py
async def is_enabled(flag_name: str, company_id: UUID, db: AsyncSession) -> bool:
    flag = await db.get(FeatureFlag, flag_name)
    if not flag or not flag.enabled:
        return False
    if flag.target_companies and company_id not in flag.target_companies:
        return False
    return random.randint(1, 100) <= flag.rollout_percentage

# Usage in router -- calls agent via langgraph-sdk
@router.post("/api/ai/conversations/{id}/generate")
async def generate_message(id: UUID, agent_client: AgentClient = Depends(get_agent_client), ...):
    if not await is_enabled("ai_message_generation", current_user.company_id, db):
        raise HTTPException(404, "Feature not available")
    result = await agent_client.run_collection_agent(invoice_context)
    return result
```

### 14.3 Code Organization for the Boundary

```
# rcbl-backend repo (Backend)
src/
├── clients/langgraph_client.py    # SDK client to call agent service (Post-MVP)
├── services/ai_service.py         # Orchestrates agent calls (Post-MVP)
├── api/routers/ai_router.py       # AI endpoints, all gated by feature flags (Post-MVP)
├── jobs/ai_jobs.py                # AI job dispatch via SDK (Post-MVP)
└── ...                            # Everything else is MVP

# receivable-agents repo (Agent Service -- entirely Post-MVP)
src/
├── agents/                        # LangGraph graphs
├── tools/                         # Agent tools
├── models/                        # ML models
├── prompts/                       # Prompt templates
└── llm/                           # LLM gateway
```

The MVP deployment does not start the agent service at all. Post-MVP, enable the agent service and configure `LANGGRAPH_API_URL` in the backend.

---

## Appendix A: Technology Decision Records

### ADR-001: Python (FastAPI) for Backend

**Decision:** Python 3.12 + FastAPI for backend API and worker.

**Rationale:**
- **Unified language with AI:** LangGraph, scikit-learn, XGBoost, litellm are all Python. Same language for backend and agent repos = shared skill set
- **FastAPI performance:** Async-native, on par with Node.js for I/O-bound workloads (which this system is)
- **Development speed:** Faster iteration than compiled languages; critical for MVP timeline
- **Ecosystem depth:** Best-in-class libraries for OCR (OpenAI SDK), email (aiosmtplib), CSV (pandas), S3 (aioboto3)
- **Hire-able talent:** Large Python developer pool in Europe
- **Type safety:** Pydantic v2 + mypy provide strong runtime + static typing

**Trade-off:** Higher memory per instance (100-300MB) vs Rust (10-50MB). Mitigated by horizontal scaling and the fact that this is an I/O-bound app, not CPU-bound.

### ADR-002: Hetzner Cron Jobs for Scheduling

**Decision:** Use Hetzner Cron Jobs (external managed cron) instead of an in-process scheduler.

**Rationale:**
- **No cron library to maintain:** No APScheduler, no Celery Beat, no leader election
- **Naturally idempotent:** One HTTP call per schedule = no duplicate execution risk
- **Observable:** Each call is logged with HTTP status; easy to monitor in Hetzner dashboard
- **Decoupled from app lifecycle:** App restarts don't lose cron state; Hetzner retries on failure
- **Free/cheap:** Hetzner includes cron jobs with their hosting; minimal additional cost
- **Easy to add/remove:** Change schedule in Hetzner dashboard, no code deploy needed

**Trade-off:** External dependency on Hetzner. Mitigated by: cron endpoints are standard HTTP -- easily portable to any cron service (AWS EventBridge, Google Cloud Scheduler, cron-job.org, or even a simple crontab on a VPS).

### ADR-003: Shared Schema Multi-Tenancy with RLS

**Decision:** Single PostgreSQL database, single schema, RLS for isolation.

**Rationale:**
- Simplest migration story: one schema to manage
- Lowest infrastructure cost for first 1,000 tenants
- RLS provides database-level enforcement (not just application-level)
- Easy to query across tenants for admin operations
- Can upgrade to schema-per-tenant or DB-per-tenant later if needed

**Trade-off:** Noisy neighbor risk on shared DB; mitigated by per-tenant query limits and monitoring.

### ADR-004: arq for Job Queue (not Celery)

**Decision:** arq (async Redis queue) instead of Celery.

**Rationale:**
- Async-native: works natively with FastAPI's async ecosystem
- Lightweight: ~500 lines of code vs Celery's complexity
- Redis-only: no separate broker needed (Celery supports Redis but also needs result backend config)
- Type-safe: integrates well with Pydantic and type hints
- Simple: one worker file, one config object, done

**Trade-off:** Less feature-rich than Celery (no task chains, no canvas). Mitigated by: we don't need those features; our jobs are simple enqueue → process → done.

### ADR-005: Separate Agent and Backend Repositories

**Decision:** AI agents (`receivable-agents`) and backend (`rcbl-backend`) are separate repositories, communicating via `langgraph-sdk`.

**Rationale:**
- **Independent deployment:** Agent code can be deployed, rolled back, and versioned independently of the backend
- **Independent scaling:** LangGraph Platform can be scaled based on AI workload without affecting the backend
- **Team independence:** AI and backend teams can work on separate repos with separate CI/CD pipelines
- **Clean separation of concerns:** Backend owns business logic, auth, tenancy; agents own AI graphs, prompts, ML models
- **LangGraph Platform compatibility:** Deploying agents as a LangGraph Platform service gives built-in checkpointing, observability (LangSmith), and standard SDK communication
- **Technology flexibility:** Agent repo can adopt different ML libraries, model versions, and LLM providers without touching backend

**Trade-off:** Network hop between backend and agents adds latency (~10-50ms per call). Mitigated by: agent calls are inherently slow (LLM calls take 1-10s), so HTTP overhead is negligible. Also, the `langgraph-sdk` handles retries, timeouts, and streaming natively.

---

## Appendix B: Monitoring & Observability

### Metrics to Track

| Category | Metric | Tool |
|----------|--------|------|
| **API** | Request latency (p50, p95, p99) | Prometheus + Grafana |
| **API** | Error rate by endpoint | Prometheus |
| **API** | Active connections per tenant | Prometheus |
| **Worker** | Queue depth per queue | Redis metrics → Grafana |
| **Worker** | Job processing time | Prometheus |
| **Worker** | Job failure rate | Prometheus |
| **Database** | Active connections | pg_stat_activity |
| **Database** | Query latency (slow query log) | pganalyze / custom |
| **Database** | Table sizes and growth | pg_stat_user_tables |
| **Cron** | Hetzner job success/failure | Hetzner dashboard + alerts |
| **Cron** | Endpoint response time | API metrics |
| **AI Service** | LLM latency per model | LangSmith + Prometheus |
| **AI Service** | LLM cost per tenant | Custom meter |
| **AI Service** | Agent decision success rate | LangSmith |
| **AI Service** | Agent run duration (p50, p95) | Prometheus |
| **AI Service** | langgraph-sdk call failures | Prometheus |
| **Business** | OCR accuracy per tenant | Custom |
| **Business** | Emails sent / delivered / opened | Custom |
| **Business** | Sync success rate per provider | Custom |

### Alerting Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| API p99 > 2s | Sustained 5 min | Warning |
| API error rate > 5% | Sustained 5 min | Critical |
| Queue depth > 500 | Sustained 10 min | Warning |
| Database connections > 80% | Sustained 5 min | Critical |
| OCR job failure rate > 20% | Sustained 15 min | Warning |
| Email delivery failure > 10% | Sustained 30 min | Critical |
| Hetzner cron job failed | Any occurrence | Warning |
| Disk usage > 85% | Any occurrence | Critical |

---

## Document Control

**Approval Required From:**
- [ ] Engineering Lead
- [ ] Senior Backend Engineer
- [ ] DevOps / Infrastructure Lead
- [ ] Product Manager
- [ ] CEO / CTO

**Change Log:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-08 | Architecture Team | Initial architecture document (Rust backend) |
| 1.1 | 2026-02-08 | Architecture Team | Converted all ASCII diagrams to Mermaid |
| 2.0 | 2026-02-08 | Architecture Team | Switched backend from Rust to Python/FastAPI, replaced in-process cron with Hetzner Cron Jobs, merged AI service into same codebase as backend module, replaced Celery with arq, updated all diagrams/structures/ADRs |
| 2.1 | 2026-02-08 | Architecture Team | Replaced Alembic with Flyway for database migrations (pure SQL, language-agnostic) |
| 3.0 | 2026-02-15 | Architecture Team | Separated AI agents into independent `receivable-agents` repo, backend connects via `langgraph-sdk`. Agents deployed as LangGraph Platform service. Updated all diagrams, project structures, Docker Compose, deployment topology, scalability playbook, ADRs. Added ADR-005 for repo separation. |

---

**Next Steps:**
1. Review and approve architecture decisions (ADRs)
2. Set up local development environment (Docker Compose)
3. Create `rcbl-backend` project scaffold with FastAPI + SQLAlchemy + arq
4. Create `receivable-agents` project scaffold with LangGraph Platform
5. Create React project scaffold with Vite + TailwindCSS
6. Write initial Flyway SQL migrations (core tables + RLS)
7. Implement auth flow (register/login/JWT)
8. Configure Hetzner Cron Jobs for status updater + reminder sender
9. Begin Sprint 1: Invoice upload + OCR integration
10. Post-MVP: Deploy agent service, integrate `langgraph-sdk` in backend
