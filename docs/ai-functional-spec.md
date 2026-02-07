# AI-Native Functional Specification
## Receivable Notification System - Enhanced Platform

**Document Version:** 2.0  
**Last Updated:** February 7, 2026  
**Product Stage:** MVP + AI Enhancement Layer  
**Dependencies:** Extends core MVP functionality as defined in `functional-spec.md`

---

## 1. Executive Summary

### 1.1 Vision
Build an **AI-native accounts receivable platform** that covers the entire lifecycle -- from invoice ingestion through intelligent collection to cash flow prediction. The system starts with a **lean MVP** (invoice upload, tracking, reminders) and progressively layers AI capabilities (autonomous collection, predictive analytics) to deliver compounding value.

### 1.2 Platform Scope

| Layer | What It Covers | MVP? |
|-------|---------------|------|
| **Invoice Ingestion Hub** | Single upload, bulk upload, CSV import, third-party accounting sync | Yes (P0) |
| **Core AR Management** | Due date engine, status tracking, payment matching, dashboard | Yes (P0) |
| **Automated Reminders** | Rule-based email sequences, templates | Yes (P0) |
| **Autonomous Collection Agent** | AI-driven conversations, adaptive cadence, negotiation | Post-MVP (P1) |
| **Predictive Cash Flow Intelligence** | Payment prediction, risk scoring, cash flow forecasting | Post-MVP (P1) |

### 1.3 Success Criteria

**MVP Targets (Week 1-8):**
- User sees value on **Day 1** -- immediate visibility into overdue invoices
- **10-30% DSO reduction** through automated reminders
- **<2 min** to upload and track a new invoice (single or bulk)
- **70% activation rate** -- users who upload first invoice within 24 hours
- **10 paying customers** within 8 weeks of launch

**AI Layer Targets (Post-MVP):**
- **40-50% DSO reduction** (vs 10-30% with base MVP)
- **80% autonomous handling rate** -- collection conversations without human intervention
- **>85% accuracy** on 7-day payment probability
- **±10% accuracy** on weekly cash flow forecasts
- Maintain or improve customer NPS despite automated collections

### 1.4 Key Differentiators
- **Invoice ingestion flexibility** -- Upload single, bulk, CSV, or auto-sync from accounting software
- **From static reminders to adaptive conversations** -- AI learns what works for each customer
- **From reactive tracking to predictive intelligence** -- Know which invoices will be paid before due date
- **From transactional to relationship-aware** -- AI balances getting paid with preserving valuable customers
- **European SME focus** -- EU Late Payment Regulation built in, GDPR compliant, multi-currency ready

---

## 2. Architecture Overview

### 2.1 Platform Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Dashboard   │  │ Invoice Hub  │  │ AI Insights  │  │ Agent Control │  │
│  │              │  │ (Upload/     │  │ Hub          │  │ Center        │  │
│  │              │  │  Import)     │  │              │  │               │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      INVOICE INGESTION LAYER (MVP)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ Single       │  │ Bulk Upload  │  │ CSV Import   │  │ Third-Party   │  │
│  │ Upload +     │  │ (Multi-file  │  │ Engine       │  │ Accounting    │  │
│  │ OCR          │  │  Pipeline)   │  │              │  │ Sync Engine   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AI ORCHESTRATION LAYER (Post-MVP)                      │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │  Collection Agent Engine    │  │  Prediction & Analytics Engine      │  │
│  │  - Conversation Manager     │  │  - Payment Probability Model        │  │
│  │  - Response Generator       │  │  - Cash Flow Forecaster             │  │
│  │  - Escalation Handler       │  │  - Risk Scoring Engine              │  │
│  │  - Channel Optimizer        │  │  - Customer Behavior Analyzer       │  │
│  └─────────────────────────────┘  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DATA & ML INFRASTRUCTURE                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ LLM Gateway │  │ ML Models   │  │ Vector DB   │  │ Event Stream    │  │
│  │ (OpenAI/    │  │ (Payment    │  │ (Embeddings │  │ (Customer       │  │
│  │  Anthropic) │  │  Prediction)│  │  & Context) │  │  Interactions)  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CORE MVP LAYER                                         │
│  (Due Date Engine, Status Tracking, Reminder System, Payment Matching)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Integration Points

| Component | MVP Scope | AI Enhancement (Post-MVP) |
|-----------|-----------|--------------------------|
| **Invoice Ingestion** | Upload, bulk, CSV, OCR, third-party sync | AI extracts context, identifies contract type, flags anomalies |
| **Due Date Engine** | Rule-based calculation | AI predicts actual payment date vs contractual due date |
| **Reminder System** | Template-based sequences | Replaced by Autonomous Collection Agent |
| **Dashboard** | AR health metrics | Enhanced with AI Insights Hub |
| **Customer Management** | Basic profiles, payment terms | Enriched with AI-generated customer intelligence |
| **Accounting Integrations** | SevDesk (MVP), extensible framework | Auto-reconciliation, anomaly detection on synced data |

---

## 3. Feature 1: Invoice Ingestion Hub (MVP)

### 3.1 Overview

The Invoice Ingestion Hub is the **primary entry point** for all invoice data into the system. It supports four ingestion methods, each designed for a different user workflow. This is a **P0 MVP feature** -- without frictionless invoice ingestion, the rest of the system has no data to work with.

### 3.2 Ingestion Methods Summary

| Method | Use Case | Automation Level | MVP Priority |
|--------|----------|-----------------|--------------|
| **Single Upload** | One-off invoice from email/desktop | OCR auto-extract, user reviews | P0 |
| **Bulk Upload** | Monthly batch from folder/archive | Parallel OCR, batch review queue | P0 |
| **CSV Import** | Export from spreadsheet or legacy system | Column mapping, auto-match customers | P0 |
| **Third-Party Accounting Sync** | Connected accounting software (SevDesk, Xero, etc.) | API sync, field mapping, conflict resolution | P0 (SevDesk), P1 (others) |

### 3.3 Single Invoice Upload

#### 3.3.1 Functional Requirements (Priority: P0)

**User Story:** As a user, I want to upload a single invoice PDF and have the system automatically extract its data so I can start tracking it in under 2 minutes.

**Acceptance Criteria:**
- Drag-and-drop or click-to-upload interface
- Supported formats: PDF, PNG, JPG, JPEG
- File size limit: 10MB
- On upload, system immediately queues file for OCR processing
- OCR extracts:
  - Invoice number
  - Invoice date
  - Due date (if present)
  - Customer name and email
  - Total amount and currency
  - Payment terms (Net 15/30/60)
  - IBAN/bank details (if present)
  - Line items (stored for future use)
- After OCR, user sees pre-filled review form with:
  - Side-by-side PDF preview and extracted fields
  - Confidence indicators per field (green/yellow/red)
  - Customer dropdown (auto-matched or create new)
  - Editable fields for correction
- "Accept All" for high-confidence extractions
- System calculates due date automatically on save
- Invoice immediately appears on dashboard

**OCR Processing Flow:**
```
User uploads file
       │
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ File stored  │────▶│ OCR queued   │────▶│ OCR extracts │
│ in S3/MinIO  │     │ (async job)  │     │ fields       │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │ Customer     │
                                          │ auto-match   │
                                          └──────┬───────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │ User reviews │
                                          │ & confirms   │
                                          └──────┬───────┘
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │ Invoice      │
                                          │ created &    │
                                          │ tracked      │
                                          └──────────────┘
```

**Edge Cases:**
- Duplicate invoice number for same company → Show warning, allow override
- Poor quality scan → Show warning, fall back to manual entry
- Non-English invoice → Attempt extraction, flag low-confidence fields
- OCR timeout (>15 seconds) → Show error, allow manual entry with retry option
- Multi-page invoice → Process all pages, extract from first page primarily

**Technical Requirements:**
- Primary OCR: OpenAI Vision API (GPT-4 Vision) for structured extraction
- Fallback OCR: AWS Textract or Google Cloud Vision API
- Processing target: <10 seconds for typical single-page invoice
- Store OCR results with confidence scores in `ocr_extracted_data` JSONB
- Cache OCR results for duplicate files (SHA-256 hash-based dedup)

**UI Requirements:**
- Progress indicator with estimated time during OCR
- Review screen: PDF on left, form on right
- Confidence badges: Green checkmark (high), Yellow warning (medium), Red alert (low)
- Inline field editing with instant validation
- "Re-run OCR" button if extraction seems wrong

### 3.4 Bulk Invoice Upload

#### 3.4.1 Functional Requirements (Priority: P0)

**User Story:** As a user, I want to upload multiple invoices at once (e.g., a month's worth) and review them in a batch queue so I can onboard quickly or handle monthly processing efficiently.

**Acceptance Criteria:**
- Drag-and-drop zone accepts multiple files simultaneously
- Upload limit: **up to 50 files per batch** (MVP)
- Supported formats: PDF, PNG, JPG, JPEG (same as single upload)
- File size limit: 10MB per file, 200MB per batch
- On batch upload:
  1. System shows upload progress bar per file
  2. All files queued for parallel OCR processing
  3. User sees **Batch Review Queue** with processing status per file
- Batch Review Queue shows:
  - File name, processing status (queued/processing/ready/failed)
  - Extracted customer name, invoice number, amount (preview)
  - Confidence score (overall per invoice)
  - Quick actions: Review, Skip, Delete
- User reviews invoices one at a time (same review UI as single upload)
- "Accept All High-Confidence" button for batch approval of invoices with all fields above 80% confidence
- Batch summary after review:
  - X invoices created
  - Y invoices skipped
  - Z invoices need manual review (low confidence)
- Failed OCR files moved to "Needs Manual Entry" queue

**Batch Processing Flow:**
```
User drops 20 PDFs
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                BATCH UPLOAD PROGRESS                       │
│                                                            │
│  invoice_jan_001.pdf  ████████████████████ 100% ✓ Ready   │
│  invoice_jan_002.pdf  ████████████████░░░░  80% ⟳ OCR     │
│  invoice_jan_003.pdf  ████████████░░░░░░░░  60% ⟳ OCR     │
│  invoice_jan_004.pdf  ░░░░░░░░░░░░░░░░░░░░   0% ⏳ Queued │
│  ...                                                       │
│                                                            │
│  [Cancel Remaining]  [View Ready Invoices]                 │
└──────────────────────────────────────────────────────────┘

                    │ (all processed)
                    ▼

┌──────────────────────────────────────────────────────────┐
│                BATCH REVIEW QUEUE                          │
│                                                            │
│  ✅ High Confidence (14)  ⚠️ Needs Review (4)  ❌ Failed (2) │
│                                                            │
│  [Accept All High-Confidence]  [Review One-by-One]        │
│                                                            │
│  Customer       │ Invoice # │ Amount  │ Conf. │ Action     │
│  ───────────────┼───────────┼─────────┼───────┼──────────  │
│  Acme Corp      │ INV-001   │ €4,500  │ 95%   │ [Accept]   │
│  Beta Inc       │ INV-002   │ €8,200  │ 92%   │ [Accept]   │
│  Unknown        │ INV-003   │ €2,100  │ 45%   │ [Review]   │
│  (OCR Failed)   │ —         │ —       │ 0%    │ [Manual]   │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

**Performance Requirements:**
- Parallel OCR processing: up to 5 files concurrently
- Batch of 20 invoices fully processed in < 3 minutes
- Batch of 50 invoices fully processed in < 8 minutes
- UI remains responsive during batch processing (async updates via WebSocket or polling)

**Edge Cases:**
- Mixed file types in batch → Process each based on format, skip unsupported
- Duplicate invoices within batch → Flag duplicates, let user decide
- Duplicate against existing invoices → Warn per invoice during review
- Partial batch failure → Continue processing remaining files, report failures
- Browser tab closed during processing → Jobs continue server-side, user resumes on next login

**Technical Requirements:**
- Job queue (Redis + Bull/BullMQ) for parallel OCR processing
- WebSocket or SSE for real-time progress updates to UI
- Atomic batch operations: all-or-nothing per user confirmation
- Temporary storage for batch state (expires after 24 hours if not reviewed)

### 3.5 CSV Invoice Import

#### 3.5.1 Functional Requirements (Priority: P0)

**User Story:** As a user, I want to import invoices from a CSV file (exported from a spreadsheet, legacy system, or accounting tool) so I can migrate existing data or handle structured invoice data efficiently.

**Acceptance Criteria:**
- Upload CSV/XLSX file (max 10MB, max 5,000 rows)
- **Smart Column Mapping** screen:
  - System auto-detects columns based on header names
  - User can manually map columns if auto-detection fails
  - Required mappings: Invoice Number, Customer Name, Amount, Invoice Date
  - Optional mappings: Due Date, Currency, Payment Terms, Customer Email, Status, Notes
  - Preview first 5 rows with mapped data
  - Date format auto-detection (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, DD.MM.YYYY)
  - Number format auto-detection (1,234.56 vs 1.234,56)

**Column Mapping UI:**
```
┌──────────────────────────────────────────────────────────┐
│              CSV IMPORT - COLUMN MAPPING                   │
│                                                            │
│  File: invoices_january_2026.csv (142 rows detected)      │
│                                                            │
│  Map your CSV columns to system fields:                    │
│                                                            │
│  System Field      │ Your CSV Column          │ Required   │
│  ──────────────────┼──────────────────────────┼──────────  │
│  Invoice Number    │ [invoice_no ▼]           │ ✓          │
│  Customer Name     │ [client_name ▼]          │ ✓          │
│  Amount            │ [total_gross ▼]          │ ✓          │
│  Currency          │ [currency ▼]             │            │
│  Invoice Date      │ [date_issued ▼]          │ ✓          │
│  Due Date          │ [payment_due ▼]          │            │
│  Payment Terms     │ [— Not Mapped — ▼]       │            │
│  Customer Email    │ [email ▼]                │            │
│  Status            │ [status ▼]               │            │
│                                                            │
│  ┌─ PREVIEW (first 5 rows) ─────────────────────────────┐ │
│  │ Invoice # │ Customer    │ Amount  │ Date       │ Due  │ │
│  │ INV-001   │ Acme Corp   │ €4,500  │ 2026-01-05 │ ...  │ │
│  │ INV-002   │ Beta Inc    │ €8,200  │ 2026-01-08 │ ...  │ │
│  │ INV-003   │ Gamma LLC   │ €2,100  │ 2026-01-12 │ ...  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                            │
│  [Back]  [Import 142 Invoices]                             │
└──────────────────────────────────────────────────────────┘
```

**Import Validation Rules:**
- Skip rows with empty required fields (log as errors)
- Validate amounts are positive numbers
- Validate dates are reasonable (not before 2020, not more than 1 year in future)
- Validate currency codes (ISO 4217)
- Detect and flag duplicate invoice numbers (against existing + within CSV)
- Auto-match customers by name (fuzzy match) or email (exact match)
- Create new customer records for unmatched customers

**Import Results Screen:**
```
┌──────────────────────────────────────────────────────────┐
│              CSV IMPORT RESULTS                            │
│                                                            │
│  ✅ Successfully imported: 135 invoices                    │
│  ⚠️ Skipped (validation errors): 5 rows                   │
│  🔄 Duplicate (already exists): 2 rows                    │
│                                                            │
│  New customers created: 8                                  │
│  Matched to existing customers: 127                        │
│                                                            │
│  ┌─ ERRORS (5) ──────────────────────────────────────────┐ │
│  │ Row 23: Missing invoice number                         │ │
│  │ Row 45: Invalid amount "-500"                          │ │
│  │ Row 67: Date format not recognized "13/13/2026"        │ │
│  │ Row 89: Amount is zero                                 │ │
│  │ Row 102: Missing customer name                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                            │
│  [Download Error Report (CSV)]  [View Imported Invoices]   │
└──────────────────────────────────────────────────────────┘
```

**CSV Templates & Format Support:**
- Provide downloadable CSV template with example data
- Support common accounting export formats:
  - SevDesk export format
  - Xero export format
  - QuickBooks export format
  - LexOffice export format
  - Generic/custom CSV
- Save column mappings per company for repeat imports

**Status Mapping (from CSV):**

| CSV Status Value | System Status |
|-----------------|---------------|
| `open`, `unpaid`, `pending`, `sent` | pending |
| `overdue`, `past_due`, `late` | overdue |
| `paid`, `closed`, `settled` | paid |
| Empty or unrecognized | pending (default) |

**Edge Cases:**
- Encoding issues (UTF-8, Latin-1, Windows-1252) → Auto-detect encoding, fall back to UTF-8
- Large files (>5,000 rows) → Show warning, process in chunks of 500
- Mixed currencies in single CSV → Accept, store per-invoice currency
- CSV with extra columns → Ignore unmapped columns
- Semicolon-separated files → Auto-detect delimiter (comma, semicolon, tab)

**Technical Requirements:**
- Streaming CSV parser (handle large files without memory issues)
- Background job for imports >100 rows
- Store original CSV for audit trail
- Idempotent import: re-importing same CSV skips existing invoices
- Column mapping persistence per company in `import_config` JSONB

#### 3.5.2 Recurring CSV Import (Priority: P1)

**User Story:** As a user who regularly exports invoices from another system, I want to save my CSV column mapping and re-use it for future imports.

**Acceptance Criteria:**
- After first successful import, system saves column mapping as a "profile"
- User can name the profile (e.g., "SevDesk Export", "Monthly Spreadsheet")
- On next CSV import, user selects saved profile → columns auto-mapped
- User can edit/delete saved profiles
- System remembers date format and number format preferences

### 3.6 Third-Party Accounting Integration

#### 3.6.1 Overview

Third-party accounting integration enables **bidirectional sync** between the receivable system and external accounting software. This eliminates double-entry and ensures invoice data stays consistent across systems.

**Integration Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                 INTEGRATION ADAPTER LAYER                     │
│                                                               │
│  ┌───────────────┐  ┌──────────────┐  ┌───────────────────┐ │
│  │ SevDesk       │  │ Xero         │  │ LexOffice         │ │
│  │ Adapter       │  │ Adapter      │  │ Adapter           │ │
│  │ (MVP - P0)    │  │ (V1 - P1)    │  │ (V1 - P1)        │ │
│  └───────┬───────┘  └──────┬───────┘  └────────┬──────────┘ │
│          │                 │                    │             │
│          ▼                 ▼                    ▼             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Unified Sync Engine                         │ │
│  │  - Field Mapping        - Conflict Resolution            │ │
│  │  - Deduplication        - Error Recovery                 │ │
│  │  - Rate Limiting        - Audit Logging                  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                          │                                    │
│                          ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Provider Interface (Trait/Interface)        │ │
│  │  - fetchInvoices()     - fetchContacts()                │ │
│  │  - createInvoice()     - updateInvoiceStatus()          │ │
│  │  - fetchPayments()     - authenticate()                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  Future Adapters:                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────────┐ │
│  │QuickBooks│ │ Billomat │ │ Zoho     │ │ Custom API      │ │
│  │(V2)     │ │ (V2)     │ │ (V2)     │ │ (Webhook-based) │ │
│  └──────────┘ └──────────┘ └──────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 3.6.2 Provider Interface Contract

Every accounting integration adapter must implement the following interface:

```
AccountingProvider {
    // Authentication
    authenticate(credentials) → AuthToken
    refreshToken(token) → AuthToken
    revokeAccess(token) → void
    
    // Invoice Operations
    fetchInvoices(since: Date, page: int) → InvoiceList
    fetchInvoiceById(externalId: string) → Invoice
    createInvoice(invoice: Invoice) → ExternalId
    updateInvoiceStatus(externalId: string, status: Status) → void
    
    // Customer/Contact Operations
    fetchContacts(since: Date, page: int) → ContactList
    fetchContactById(externalId: string) → Contact
    
    // Payment Operations
    fetchPayments(since: Date, page: int) → PaymentList
    
    // Metadata
    getProviderName() → string
    getSupportedFeatures() → FeatureSet
    getRateLimits() → RateLimitConfig
}
```

#### 3.6.3 SevDesk Integration (Priority: P0 - MVP)

**User Story:** As a user of SevDesk accounting software, I want to sync invoices and payments between SevDesk and the receivable system so I don't manage data in two places.

**Connection Flow:**
1. User clicks "Connect SevDesk" in Settings → Integrations
2. System initiates OAuth 2.0 flow
3. User authorizes access in SevDesk
4. System stores encrypted tokens
5. Connection status shown: "Connected since [date]"
6. User configures sync preferences

**Sync Capabilities:**

| Capability | Direction | Automation | Priority |
|-----------|-----------|------------|----------|
| Import invoices | SevDesk → System | Manual + Auto (daily) | P0 |
| Export invoices | System → SevDesk | Manual trigger | P0 |
| Payment status sync | Bidirectional | Auto on payment event | P0 |
| Customer/contact sync | SevDesk → System | On invoice import | P0 |
| Real-time webhook sync | SevDesk → System | Event-driven | P1 |

**Field Mapping (SevDesk → System):**

| SevDesk Field | System Field | Notes |
|--------------|-------------|-------|
| `invoiceNumber` | invoice_number | |
| `invoiceDate` | invoice_date | |
| `dueDate` | due_date | Calculated if missing |
| `totalGross` | amount | |
| `currency` | currency | Default EUR |
| `contact.name` | customer.name | |
| `contact.email` | customer.email | |
| Status 100 (Draft) | pending | |
| Status 200 (Sent) | pending | |
| Status 1000 (Paid) | paid | |
| Status 1001 (Overdue) | overdue | |

**Sync Configuration (User Settings):**
- **Sync Direction:** Import only / Export only / Bidirectional (default)
- **Auto-sync:** Enable/disable, frequency (daily at configurable time)
- **Conflict Resolution:** Last write wins / Prefer SevDesk / Prefer System / Ask user
- **Filter:** Sync all invoices or only invoices from specific date range

**Error Handling:**
- Invalid/expired credentials → Prompt user to reconnect
- Rate limit exceeded (100 req/min) → Queue and retry with exponential backoff
- Network failure → Retry 3 times, then notify user
- Field mapping failure → Skip field, log warning, include in sync report
- Duplicate detection → Match by invoice number + company, skip if exists

#### 3.6.4 Xero Integration (Priority: P1 - V1)

**User Story:** As a Xero user, I want to import invoices from Xero so I can manage collections in one place.

**MVP Scope for Xero:**
- OAuth 2.0 authentication
- One-way import: Xero → System
- Invoice and contact sync
- Payment status sync
- Manual sync trigger only (auto-sync in V2)

**Field Mapping (Xero → System):**

| Xero Field | System Field |
|-----------|-------------|
| `InvoiceNumber` | invoice_number |
| `Date` | invoice_date |
| `DueDate` | due_date |
| `Total` | amount |
| `CurrencyCode` | currency |
| `Contact.Name` | customer.name |
| `Contact.EmailAddress` | customer.email |
| Status: AUTHORISED | pending |
| Status: PAID | paid |
| Status: OVERDUE | overdue |

#### 3.6.5 LexOffice Integration (Priority: P1 - V1)

**User Story:** As a LexOffice user (popular in Germany), I want to import invoices from LexOffice.

**MVP Scope for LexOffice:**
- API key authentication
- One-way import: LexOffice → System
- Invoice and contact sync
- Manual sync trigger

#### 3.6.6 Generic Webhook Integration (Priority: P2 - V2)

**User Story:** As a user with a custom or unsupported accounting system, I want to send invoices to the system via a webhook/API.

**Acceptance Criteria:**
- Company gets a unique webhook URL: `POST /api/webhooks/{company-slug}/invoices`
- Accepts JSON payload with standard invoice fields
- API key authentication
- Rate limit: 100 requests/minute
- Returns created invoice ID or validation errors
- Webhook event log in settings

**Webhook Payload Example:**
```json
{
  "invoice_number": "INV-2026-001",
  "customer_name": "Acme Corp",
  "customer_email": "ap@acme.com",
  "amount": 4500.00,
  "currency": "EUR",
  "invoice_date": "2026-01-15",
  "due_date": "2026-02-14",
  "payment_terms_days": 30,
  "status": "open",
  "external_id": "ext-12345",
  "metadata": {}
}
```

#### 3.6.7 Integration Settings UI

```
┌─────────────────────────────────────────────────────────────┐
│  SETTINGS > INTEGRATIONS                                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  CONNECTED                                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  [SevDesk Logo] SevDesk                                │  │
│  │  Status: ✅ Connected since Jan 15, 2026                │  │
│  │  Last sync: 2 hours ago (142 invoices synced)          │  │
│  │  Auto-sync: Daily at 2:00 AM                           │  │
│  │                                                         │  │
│  │  [Sync Now]  [Configure]  [View Logs]  [Disconnect]    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  AVAILABLE                                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  [Xero Logo] Xero              [Connect]               │  │
│  │  Import invoices from Xero accounting                   │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  [LexOffice Logo] LexOffice    [Connect]               │  │
│  │  Import invoices from LexOffice                         │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  [API Icon] Custom Webhook      [Set Up]               │  │
│  │  Send invoices via API from any system                  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  CSV IMPORT PROFILES                                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  "Monthly Spreadsheet" - Last used: Feb 1, 2026        │  │
│  │  "SevDesk CSV Export" - Last used: Jan 28, 2026        │  │
│  │                                                         │  │
│  │  [Import CSV]  [Manage Profiles]                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### 3.6.8 Sync Dashboard

**User Story:** As a user, I want to see the history and health of my integration syncs.

```
┌─────────────────────────────────────────────────────────────┐
│  SYNC HISTORY - SevDesk                                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Last Sync   │  │ Total       │  │ Success Rate        │  │
│  │ 2 hrs ago   │  │ 1,247       │  │ 98.2%               │  │
│  │             │  │ invoices    │  │ last 30 days        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                               │
│  RECENT SYNCS                                                 │
│  Date/Time       │ Type     │ Direction │ Records │ Status    │
│  ─────────────────┼──────────┼───────────┼─────────┼─────────│
│  Feb 7, 02:00 AM │ Auto     │ Import    │ 12      │ ✅ OK    │
│  Feb 6, 02:00 AM │ Auto     │ Import    │ 8       │ ✅ OK    │
│  Feb 5, 11:30 AM │ Manual   │ Import    │ 45      │ ⚠️ 2 err │
│  Feb 5, 02:00 AM │ Auto     │ Import    │ 3       │ ✅ OK    │
│                                                               │
│  [View Error Details]  [Retry Failed]  [Export Log]           │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Feature 2: Autonomous Collection Agent (Post-MVP)

### 4.1 Overview

The Autonomous Collection Agent (ACA) is an AI-powered system that manages the entire collection lifecycle for each invoice, from initial reminder through payment resolution or human escalation. This replaces the rule-based reminder system from MVP with an intelligent, adaptive agent.

**Prerequisite:** Core MVP must be live with at least 6 months of payment data for model training.

### 4.2 Agent Capabilities

#### 4.2.1 Core Agent Functions

| Function | Description | Autonomy Level |
|----------|-------------|----------------|
| **Initial Outreach** | Generates personalized reminder based on customer history | Fully Autonomous |
| **Follow-up Cadence** | Determines optimal timing and frequency | Fully Autonomous |
| **Tone Adaptation** | Adjusts communication style based on context | Fully Autonomous |
| **Response Handling** | Processes and responds to customer replies | Semi-Autonomous (may escalate) |
| **Negotiation** | Proposes payment plans, discusses disputes | Semi-Autonomous |
| **Escalation** | Hands off to human when needed | Human-in-the-loop |

#### 4.2.2 Agent Decision Framework

```
┌─────────────────────────────────────────────────────────────┐
│                     AGENT DECISION LOOP                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. OBSERVE                                                   │
│     ├── Invoice status & history                              │
│     ├── Customer behavior patterns                            │
│     ├── Previous communication outcomes                       │
│     ├── External signals (company news, seasonality)          │
│     └── Current communication context                         │
│                                                               │
│  2. ANALYZE                                                   │
│     ├── Payment probability score                             │
│     ├── Customer relationship value                           │
│     ├── Risk of churn vs cost of delay                        │
│     ├── Optimal action recommendation                         │
│     └── Confidence level                                      │
│                                                               │
│  3. DECIDE                                                    │
│     ├── If confidence > threshold → Act autonomously          │
│     ├── If confidence < threshold → Request human review      │
│     └── If high-risk action → Require human approval          │
│                                                               │
│  4. ACT                                                       │
│     ├── Generate communication                                │
│     ├── Select channel (email, phone script)                  │
│     ├── Execute action                                        │
│     └── Schedule follow-up                                    │
│                                                               │
│  5. LEARN                                                     │
│     ├── Track outcome                                         │
│     ├── Update customer model                                 │
│     └── Improve future predictions                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Functional Requirements

#### 4.3.1 Intelligent Outreach Generation (Priority: P0)

**User Story:** As a user, I want the AI to generate personalized, context-aware collection messages that feel human and professional.

**Acceptance Criteria:**
- AI generates unique message for each customer/invoice combination
- Message incorporates:
  - Customer name and relationship history
  - Invoice details (amount, number, due date)
  - Previous payment patterns for this customer
  - Appropriate tone based on overdue severity
  - Relevant context (e.g., "We noticed you typically pay on the 15th...")
- User can preview AI-generated message before first send
- User can edit and approve message templates
- AI learns from user edits to improve future generations

**Example Generated Messages:**

*Early Reminder (customer with good history):*
```
Hi Sarah,

Just a quick heads-up that invoice #INV-2024-089 for €4,500 is coming 
up for payment on February 5th.

Given our great working relationship over the past 2 years, I wanted 
to make sure this doesn't slip through the cracks during what I know 
is a busy month-end period.

Payment details are attached. Let me know if you have any questions!

Best,
[Company Name]
```

*Firm Reminder (customer with payment delays):*
```
Hi Michael,

I'm following up on invoice #INV-2024-067 for €12,300, which is now 
21 days overdue.

I understand that payment delays can happen, and I noticed this is 
similar to the timing on your last few invoices. If there's a cash 
flow timing issue, I'd be happy to discuss a payment arrangement 
that works for both of us.

Could you please let me know your expected payment date, or if you'd 
like to set up a brief call to discuss options?

Best regards,
[Company Name]
```

**Technical Requirements:**
- LLM integration (OpenAI GPT-4 or Anthropic Claude)
- Prompt engineering for consistent brand voice
- Context injection from customer history
- Template guardrails to prevent off-brand messaging
- A/B testing framework for message variants

#### 4.3.2 Adaptive Communication Cadence (Priority: P0)

**User Story:** As a user, I want the AI to determine the optimal timing for each follow-up based on customer behavior, not fixed schedules.

**Acceptance Criteria:**
- AI replaces static reminder sequences with dynamic cadence
- Cadence factors include:
  - Customer's historical response time
  - Day of week/time of day responsiveness
  - Current invoice aging
  - Recent communication history
  - Payment probability score
- AI can accelerate or delay follow-ups based on signals
- User can set minimum/maximum bounds for follow-up frequency
- System logs rationale for each timing decision

**Cadence Intelligence Examples:**

| Customer Signal | AI Action |
|-----------------|-----------|
| Customer opened email but didn't respond | Wait 2 days, then follow up |
| Customer historically pays on 15th of month | Schedule reminder for 12th |
| Customer is 3 weeks overdue, no response | Escalate frequency, suggest phone call |
| Customer responded "paying next week" | Wait 8 days before next outreach |
| High-value customer, first overdue invoice | Use gentle approach, longer intervals |

**Data Required:**
- Email open/click tracking (via pixel or link tracking)
- Historical payment dates per customer
- Response times to previous communications
- Customer lifetime value score

#### 4.3.3 Customer Reply Processing (Priority: P0)

**User Story:** As a user, I want the AI to understand and appropriately respond to customer replies without my intervention for routine cases.

**Acceptance Criteria:**
- AI monitors incoming emails to company inbox
- AI classifies customer replies into categories:
  - **Payment Confirmation** -- "Payment sent today"
  - **Payment Promise** -- "Will pay by Friday"
  - **Dispute** -- "We have concerns about the invoice"
  - **Request for Info** -- "Can you resend the invoice?"
  - **Negotiation Request** -- "Can we pay in installments?"
  - **Out of Office** -- Auto-reply detection
  - **Unrelated** -- Not about this invoice
- For each category, AI takes appropriate action:

| Category | AI Action | Autonomy |
|----------|-----------|----------|
| Payment Confirmation | Log expected payment, pause reminders, verify in 3 days | Autonomous |
| Payment Promise | Log promise date, schedule follow-up, update prediction | Autonomous |
| Dispute | Flag for human review, pause reminders, draft response options | Human-in-loop |
| Request for Info | Auto-respond with invoice PDF, update tracking | Autonomous |
| Negotiation Request | Generate payment plan options, present to user for approval | Human-in-loop |
| Out of Office | Extract return date, reschedule outreach | Autonomous |

**Natural Language Understanding Requirements:**
- Sentiment analysis to detect frustration/satisfaction
- Entity extraction (dates, amounts, invoice numbers)
- Intent classification with confidence scores
- Multi-language support (EN, DE, FR for V1)

#### 4.3.4 Automated Payment Plan Negotiation (Priority: P1)

**User Story:** As a user, I want the AI to offer payment plan options when customers request them, within my pre-approved parameters.

**Acceptance Criteria:**
- User defines payment plan rules in settings:
  - Minimum down payment percentage (e.g., 20%)
  - Maximum installment count (e.g., 3 payments)
  - Maximum total duration (e.g., 60 days)
  - Interest/fees (if applicable)
  - Invoice amount thresholds (e.g., only for invoices > €1,000)
- When customer requests payment plan, AI:
  - Checks if invoice qualifies based on rules
  - Generates 2-3 plan options within parameters
  - Presents options to customer
  - Tracks agreement and payment schedule
- User notified of any payment plan offered
- User can approve/reject before sending (optional setting)

**Payment Plan Example:**

*Customer email:* "We're having cash flow issues. Can we pay over time?"

*AI-generated response:*
```
Hi Marcus,

I understand -- cash flow timing can be challenging. I'd be happy to 
offer a payment arrangement for invoice #INV-2024-089 (€4,500).

Here are a few options that work for us:

Option A: 50% now (€2,250) + 50% in 30 days
Option B: 3 payments of €1,500 each over 60 days
Option C: 25% now + 3 monthly payments of €1,125

Please let me know which option works best for you, or if you'd 
like to discuss a different arrangement.

Best regards,
[Company Name]
```

#### 4.3.5 Multi-Channel Orchestration (Priority: P1)

**User Story:** As a user, I want the AI to recommend and execute outreach across multiple channels based on what works best for each customer.

**Acceptance Criteria:**
- Supported channels:
  - Email (fully automated)
  - Phone call scripts (AI generates script, human executes)
  - LinkedIn InMail (AI draft, user approval required)
- AI recommends channel based on:
  - Customer's responsiveness to previous channels
  - Urgency of collection
  - Customer relationship value
  - Channel availability (e.g., do we have phone number?)
- Channel escalation path:
  - Day 1-14: Email only
  - Day 15-30: Email + Phone script recommendation
  - Day 30+: Email + Phone + LinkedIn + Human escalation
- Track effectiveness by channel per customer segment

**Phone Script Generation:**

When AI recommends phone outreach, it generates a call script:
```
CALL SCRIPT: Invoice #INV-2024-089

Customer: Acme Corp (Sarah Johnson - CFO)
Amount Due: €4,500 (21 days overdue)
Relationship: 2-year customer, €45,000 annual spend

OPENING:
"Hi Sarah, this is [Name] from [Company]. Do you have a quick moment 
to discuss an outstanding invoice?"

KEY POINTS:
- Invoice #INV-2024-089 for €4,500 is now 21 days overdue
- We sent 3 email reminders (no response)
- They usually pay within 15 days

SUGGESTED APPROACH:
- Friendly but direct -- this is unusual for them
- Ask if there's an issue with the invoice or service
- Offer payment plan if cash flow issue

IF THEY CAN PAY:
"That's great. When can we expect the payment?"
[Log date and schedule follow-up]

IF THEY DISPUTE:
"I understand. Let me make a note and have our team look into this."
[Flag for human review]

IF PAYMENT PLAN NEEDED:
"We can certainly discuss options. Would [X] work for you?"
```

#### 4.3.6 Escalation Management (Priority: P0)

**User Story:** As a user, I want the AI to know when to escalate to human intervention and provide context for quick resolution.

**Escalation Triggers:**

| Trigger | Threshold | Escalation Type |
|---------|-----------|-----------------|
| High-value invoice | Amount > company-defined threshold (e.g., €10,000) | Approval required before outreach |
| Customer dispute | AI detects dispute language | Human review required |
| Legal threat | AI detects legal language | Immediate human escalation |
| VIP customer | Customer marked as VIP | All outreach requires approval |
| Low confidence | AI confidence < 60% | Human review before action |
| Extended overdue | > 45 days overdue | Recommend legal/collection agency |
| No response | 4+ outreach attempts, no response | Recommend phone/alternative channel |

**Escalation Workflow:**
1. AI triggers escalation with reason
2. Human receives notification with:
   - Invoice details
   - Customer context
   - Communication history
   - AI's recommended action
   - AI's confidence level
3. Human can:
   - Approve AI recommendation
   - Modify and approve
   - Take over conversation
   - Mark as resolved
4. AI learns from human decisions

**Acceptance Criteria:**
- Escalation dashboard shows all pending items
- Priority sorting (highest value + oldest first)
- One-click approve/reject
- Bulk actions for similar cases
- SLA tracking (escalations should be resolved within 24 hours)

#### 4.3.7 Learning & Optimization (Priority: P1)

**User Story:** As a user, I want the AI to continuously improve based on outcomes.

**Learning Signals:**
- **Positive outcomes:**
  - Payment received after outreach
  - Customer responded positively
  - Shorter collection cycle than predicted
- **Negative outcomes:**
  - Customer complained about tone
  - Customer churned after aggressive collection
  - No response after multiple attempts
  - User modified AI draft before sending

**Optimization Areas:**
- Message tone and phrasing
- Optimal send times per customer
- Channel effectiveness by segment
- Escalation thresholds
- Payment plan terms acceptance rates

**Feedback Loop:**
```
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING LOOP                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ACTION → OUTCOME → ANALYSIS → MODEL UPDATE → ACTION         │
│                                                               │
│  Example:                                                     │
│  - Sent friendly reminder to Customer X                       │
│  - No response after 5 days                                   │
│  - Analysis: Customer X responds better to firm tone          │
│  - Update: Increase firmness for Customer X                   │
│  - Next action: Use firmer tone                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Technical Requirements:**
- Outcome tracking for every AI action
- A/B testing framework
- Model retraining pipeline (weekly)
- Explainability dashboard (why did AI do X?)

### 4.4 Agent Control Center UI

#### 4.4.1 Agent Dashboard

**Components:**
1. **Active Conversations** -- List of invoices AI is currently managing
2. **Pending Approvals** -- Actions requiring human approval
3. **Recent Activity** -- Timeline of AI actions
4. **Performance Metrics** -- Success rates, response times
5. **Escalation Queue** -- Items needing human intervention

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  Collection Agent Control Center                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐      │
│ │ Active: 47       │ │ Pending: 5       │ │ Success Rate: 78%│      │
│ │ conversations    │ │ approvals        │ │ this month       │      │
│ └──────────────────┘ └──────────────────┘ └──────────────────┘      │
│                                                                      │
│  PENDING APPROVALS                                                   │
│ ┌───────────────────────────────────────────────────────────────┐   │
│ │  Acme Corp - €12,300 - AI wants to offer payment plan         │   │
│ │   [Approve] [Modify] [Reject]                                  │   │
│ │  TechStart - €5,000 - Customer dispute detected                │   │
│ │   [View Details] [Take Over] [Let AI Continue]                 │   │
│ └───────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ACTIVE CONVERSATIONS                                                │
│ ┌───────────────────────────────────────────────────────────────┐   │
│ │ Customer        │ Amount   │ Status    │ Next Action │ When   │   │
│ ├─────────────────┼──────────┼───────────┼─────────────┼────────┤   │
│ │ Acme Corp       │ €4,500   │ Awaiting  │ Follow-up   │ 2 days │   │
│ │ Beta Inc        │ €8,200   │ Promised  │ Verify pay  │ 5 days │   │
│ │ Gamma LLC       │ €2,100   │ Overdue   │ Firm remind │ Today  │   │
│ └───────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 4.4.2 Conversation Detail View

**Components:**
1. **Conversation Timeline** -- Full history of AI and human messages
2. **Customer Context Panel** -- AI-generated customer summary
3. **AI Reasoning Panel** -- Why AI took each action
4. **Action Controls** -- Approve, modify, take over

#### 4.4.3 Agent Settings

**Configurable Parameters:**
- **Autonomy Level:**
  - Full autonomy (AI handles everything, notify on escalation)
  - Supervised (AI drafts, human approves)
  - Assisted (AI suggests, human executes)
- **Escalation Thresholds:**
  - Invoice amount threshold
  - Customer value threshold
  - Overdue days before phone recommendation
- **Communication Limits:**
  - Maximum emails per invoice
  - Minimum days between contacts
  - Quiet hours (don't send before 8 AM or after 6 PM)
- **Payment Plan Rules:**
  - Eligible invoice amounts
  - Maximum installments
  - Minimum down payment

---

## 5. Feature 3: Predictive Cash Flow Intelligence (Post-MVP)

### 5.1 Overview

Predictive Cash Flow Intelligence provides ML-powered forecasting and risk assessment to help users anticipate cash flow and proactively manage collection priorities.

**Prerequisite:** Requires 6+ months of historical payment data for meaningful predictions.

### 5.2 Prediction Models

#### 5.2.1 Invoice Payment Probability Model

**Purpose:** Predict the likelihood that a specific invoice will be paid within various time windows.

**Predictions Generated:**
- P(paid in 7 days)
- P(paid in 14 days)
- P(paid in 30 days)
- P(paid by due date)
- Expected payment date (most likely date)

**Model Features:**

| Feature Category | Features |
|------------------|----------|
| **Invoice Features** | Amount, payment terms, days since invoice, days until/since due |
| **Customer Features** | Avg days to pay, payment variance, total invoices, total outstanding, longest overdue |
| **Relationship Features** | Customer tenure, invoice frequency, lifetime value, recent activity |
| **Temporal Features** | Day of week, month, quarter, holiday proximity, month-end proximity |
| **Communication Features** | Emails sent, response rate, last response, sentiment of last response |
| **External Features** | Industry, company size (if available), economic indicators |

**Model Architecture:**
- Gradient Boosting (XGBoost or LightGBM) for probability prediction
- Time series component for seasonal patterns
- Regular retraining with new payment data

**Accuracy Targets:**
- P(paid in 7 days): AUROC > 0.85
- Expected payment date: ±3 days for 70% of invoices

#### 5.2.2 Customer Risk Scoring Model

**Purpose:** Assess the credit risk of each customer based on payment behavior and external signals.

**Risk Score Components:**

| Component | Weight | Description |
|-----------|--------|-------------|
| **Payment History Score** | 40% | Based on historical payment timeliness |
| **Outstanding Balance Score** | 20% | Current AR as % of typical monthly billing |
| **Trend Score** | 20% | Are payment times improving or worsening? |
| **External Signal Score** | 20% | Company news, industry trends, economic data |

**Risk Categories:**
- **Low Risk (Score 0-30):** Consistently pays early/on-time
- **Medium Risk (Score 31-60):** Occasional delays, generally reliable
- **High Risk (Score 61-80):** Frequent delays, requires active management
- **Critical Risk (Score 81-100):** Significant collection risk, consider terms change

**Alerts:**
- Notify user when customer risk score increases by >20 points
- Weekly risk summary for all customers
- Pre-invoice risk assessment (before sending new invoice)

#### 5.2.3 Cash Flow Forecasting Model

**Purpose:** Predict expected cash inflows from accounts receivable over the next 4-12 weeks.

**Forecast Output:**
```
Week 1: €23,450 (±€3,200) - 85% confidence
Week 2: €18,700 (±€4,100) - 78% confidence
Week 3: €31,200 (±€5,500) - 72% confidence
Week 4: €15,800 (±€4,800) - 65% confidence
```

**Methodology:**
1. For each open invoice, get P(paid in week N)
2. Expected value = Invoice Amount x P(paid in week N)
3. Aggregate across all invoices
4. Apply Monte Carlo simulation for confidence intervals

### 5.3 Functional Requirements

#### 5.3.1 Payment Probability Dashboard (Priority: P0)

**User Story:** As a user, I want to see which invoices are likely to be paid soon so I can prioritize my follow-up efforts.

**Acceptance Criteria:**
- Invoice list includes "Payment Probability" column
- Color-coded probability badges:
  - Green (>70%): Likely to pay soon
  - Yellow (40-70%): Uncertain
  - Red (<40%): Unlikely without intervention
- Sort/filter by payment probability
- Tooltip shows probability breakdown and reasoning

**UI Enhancement:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  INVOICE LIST - PRIORITIZED BY AI                                    │
├─────────────────────────────────────────────────────────────────────┤
│ Customer     │ Amount   │ Due      │ Status   │ Pay Prob  │ Action  │
├──────────────┼──────────┼──────────┼──────────┼───────────┼─────────┤
│ Gamma LLC    │ €2,100   │ +14 days │ Overdue  │ 23% (Low) │ Escalate│
│ Beta Inc     │ €8,200   │ +7 days  │ Overdue  │ 52% (Med) │ Active  │
│ Acme Corp    │ €4,500   │ +3 days  │ Overdue  │ 85% (High)│ Monitor │
│ Delta Tech   │ €3,300   │ -5 days  │ Due Soon │ 91% (High)│ On Track│
└─────────────────────────────────────────────────────────────────────┘
```

#### 5.3.2 Cash Flow Forecast View (Priority: P0)

**User Story:** As a user, I want to see predicted cash inflows for the next 4-8 weeks so I can plan my business finances.

**Acceptance Criteria:**
- Dedicated "Cash Flow Forecast" page
- Time series chart showing:
  - Predicted weekly cash inflows
  - Confidence interval bands
  - Historical actuals (for comparison)
- Table breakdown by week, expected amount, contributing invoices, confidence level
- Export forecast to CSV

**Forecast Dashboard:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  CASH FLOW FORECAST                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  €50K ┤                    ╭──╮                                     │
│       │        ╭──╮      ╭─╯  ╰─╮                                   │
│  €30K ┤      ╭─╯  ╰╮    ╭╯      ╰─╮                                 │
│       │    ╭─╯     ╰──╮╭╯         ╰──╮                              │
│  €10K ┤  ╭─╯          ╰╯             ╰──                            │
│       └──┴────┬────┬────┬────┬────┬────┬────                        │
│            Week1 Week2 Week3 Week4 Week5 Week6                      │
│                                                                      │
│  -- Predicted  ░░ Confidence Range  -- Historical                    │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│ Week    │ Expected   │ Range          │ Top Contributors            │
├─────────┼────────────┼────────────────┼─────────────────────────────┤
│ Week 1  │ €23,450    │ €20K - €27K    │ Acme (€4.5K), Beta (€8.2K) │
│ Week 2  │ €18,700    │ €14K - €23K    │ Delta (€3.3K), ...         │
│ Week 3  │ €31,200    │ €25K - €37K    │ Epsilon (€12K), ...        │
└─────────────────────────────────────────────────────────────────────┘
```

#### 5.3.3 Customer Risk Profiles (Priority: P0)

**User Story:** As a user, I want to see a risk assessment for each customer to help me decide on credit terms and collection intensity.

**Acceptance Criteria:**
- Customer detail page includes "AI Risk Assessment" section
- Risk score (0-100) with category label
- Risk trend indicator (improving/stable/worsening)
- Contributing factors explained
- Historical risk score chart
- Recommended actions based on risk level

**Customer Risk Profile:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  CUSTOMER: Acme Corp                                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │  AI RISK ASSESSMENT                                             │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │                                                                  │ │
│ │  RISK SCORE: 28 (LOW RISK)  Trend: Improving                    │ │
│ │  ████████░░░░░░░░░░░░░░░░░░                                     │ │
│ │                                                                  │ │
│ │  FACTORS:                                                        │ │
│ │  + Payment History: Avg 12 days to pay (vs 30 day terms)        │ │
│ │  + Trend: Payment times improving over last 6 months            │ │
│ │  ~ Current AR: €4,500 outstanding (normal for volume)           │ │
│ │  + Relationship: 2-year customer, €45K annual spend             │ │
│ │                                                                  │ │
│ │  AI RECOMMENDATION:                                              │ │
│ │  "Low-risk customer with excellent payment history. Consider    │ │
│ │   offering extended terms (Net 45) to strengthen relationship." │ │
│ │                                                                  │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 5.3.4 Proactive Risk Alerts (Priority: P1)

**User Story:** As a user, I want to be alerted when a customer's risk profile changes significantly so I can take action.

**Alert Triggers:**
- Customer risk score increases by >20 points in 30 days
- Customer has unusual payment delay (>2x their average)
- Customer has 3+ overdue invoices simultaneously
- Large invoice (>€10K) approaching due date with low payment probability
- New customer's first invoice is overdue

**Alert Delivery:**
- In-app notification
- Daily email digest (configurable)
- Real-time email for critical alerts

**Alert Example:**
```
RISK ALERT: Beta Inc

Risk Score: 45 → 67 (+22 in 30 days)

What changed:
- Last 3 invoices paid avg 45 days late (vs previous avg 10 days)
- Current outstanding: €14,200 (2x normal)
- No response to last 2 reminder emails

Recommended Actions:
1. Call accounts payable directly
2. Consider holding new work until balance cleared
3. Review credit terms

[View Customer Profile] [Contact Customer] [Dismiss]
```

#### 5.3.5 Working Capital Optimization (Priority: P2)

**User Story:** As a user, I want AI to recommend actions that could improve my cash flow.

**Recommendations Engine:**

| Scenario | AI Recommendation | Expected Impact |
|----------|-------------------|-----------------|
| Customer usually pays Day 25 | Offer 2% discount for payment by Day 10 | 15-day DSO improvement |
| High-value customer, low risk | Extend Net 45 terms to strengthen relationship | 3% churn risk reduction |
| New customer, unknown risk | Require 50% deposit on first project | Risk mitigation |
| Customer with cash flow issues | Offer 3-month payment plan | 40% higher collection rate |

#### 5.3.6 Invoice Anomaly Detection (Priority: P1)

**User Story:** As a user, I want the AI to flag unusual invoices before I send reminders.

**Anomalies Detected:**
- Invoice amount significantly higher than typical for customer
- Invoice to new customer with high-risk signals
- Duplicate invoice number
- Invoice date in distant past
- Amount doesn't match typical project size

**Example Alert:**
```
ANOMALY DETECTED: Invoice #INV-2024-112

This invoice for €47,500 to "NewCorp Ltd" is unusual:
- 3x larger than your typical invoice (avg €15,000)
- First invoice to this customer
- No signed contract on file

Before sending reminders, please verify:
[ ] Amount is correct
[ ] Customer has approved the work
[ ] Payment terms are agreed

[Confirm & Proceed] [Review Invoice] [Cancel Reminders]
```

### 5.4 AI Insights Hub UI

**Components:**
1. **Cash Flow Forecast Widget** -- Chart + summary
2. **Payment Probability Summary** -- Distribution of invoices by probability
3. **Risk Overview** -- Customer risk distribution
4. **Action Recommendations** -- AI-suggested actions
5. **Anomaly Alerts** -- Items needing attention

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────────────┐
│  AI INSIGHTS HUB                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │  NEXT 4 WEEKS FORECAST      │ │  PAYMENT PROBABILITY            │ │
│ │                             │ │                                  │ │
│ │ Expected: €89,650           │ │  High (>70%):   12 invoices     │ │
│ │ Range: €72K - €107K         │ │  Medium:         8 invoices     │ │
│ │                             │ │  Low (<40%):     4 invoices     │ │
│ │ [View Full Forecast]        │ │                                  │ │
│ └─────────────────────────────┘ └─────────────────────────────────┘ │
│                                                                      │
│ ┌─────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │  RISK ALERTS (3)            │ │  AI RECOMMENDATIONS             │ │
│ │                             │ │                                  │ │
│ │ - Beta Inc: Risk +22pts     │ │ - Offer Acme 2% early pay       │ │
│ │ - Gamma LLC: 45 days OD     │ │   Est. impact: 15 days DSO      │ │
│ │ - New invoice anomaly       │ │ - Call Beta Inc AP directly     │ │
│ │                             │ │   Est. impact: €8,200 collected │ │
│ │ [View All Alerts]           │ │ [View All Recommendations]       │ │
│ └─────────────────────────────┘ └─────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Data Model Extensions

### 6.1 New Entities for Invoice Ingestion Hub

#### InvoiceUploadBatch
```
id: UUID (PK)
company_id: UUID (FK)
upload_type: Enum (single, bulk, csv_import)
total_files: Integer
processed_files: Integer
successful_files: Integer
failed_files: Integer
status: Enum (uploading, processing, review_pending, completed, failed)
metadata: JSONB (nullable, stores column mappings for CSV, etc.)
created_by: UUID (FK → users)
created_at: Timestamp
completed_at: Timestamp (nullable)

Index: company_id, status, created_at
```

#### InvoiceUploadItem
```
id: UUID (PK)
batch_id: UUID (FK → InvoiceUploadBatch)
file_name: String
file_url: String (S3/MinIO path)
file_hash: String (SHA-256, for dedup)
file_size_bytes: Integer
status: Enum (queued, processing, ready, review_pending, accepted, rejected, failed)
ocr_confidence_score: Decimal(3,2) (nullable, 0.00-1.00)
ocr_extracted_data: JSONB (nullable)
ocr_processing_time_ms: Integer (nullable)
error_message: Text (nullable)
invoice_id: UUID (FK → invoices, nullable, set after acceptance)
created_at: Timestamp
processed_at: Timestamp (nullable)

Index: batch_id, status, file_hash
```

#### CSVImportProfile
```
id: UUID (PK)
company_id: UUID (FK)
profile_name: String
column_mapping: JSONB
date_format: String (nullable)
number_format: String (nullable)
delimiter: String (default ',')
encoding: String (default 'utf-8')
last_used_at: Timestamp (nullable)
created_at: Timestamp
updated_at: Timestamp

Index: company_id
```

#### IntegrationProvider
```
id: UUID (PK)
company_id: UUID (FK)
provider: Enum (sevdesk, xero, lexoffice, quickbooks, custom_webhook)
display_name: String
access_token: String (encrypted)
refresh_token: String (encrypted, nullable)
token_expires_at: Timestamp (nullable)
webhook_url: String (nullable, for custom webhook)
webhook_api_key: String (encrypted, nullable)
sync_direction: Enum (import, export, bidirectional)
auto_sync_enabled: Boolean (default false)
auto_sync_interval: Enum (hourly, daily, weekly) (default 'daily')
auto_sync_time: Time (nullable, default 02:00)
last_sync_at: Timestamp (nullable)
last_sync_status: Enum (success, failed, partial) (nullable)
last_sync_error: Text (nullable)
sync_config: JSONB (nullable, provider-specific config)
field_mapping_overrides: JSONB (nullable, custom field mappings)
status: Enum (active, disconnected, error)
created_at: Timestamp
updated_at: Timestamp

Index: company_id, provider, status
```

#### WebhookEvent
```
id: UUID (PK)
provider_id: UUID (FK → IntegrationProvider)
event_type: Enum (invoice_created, invoice_updated, payment_received, contact_updated)
payload: JSONB
processing_status: Enum (received, processing, processed, failed)
error_message: Text (nullable)
received_at: Timestamp
processed_at: Timestamp (nullable)

Index: provider_id, processing_status, received_at
```

### 6.2 Core Entities (from MVP)

#### Company
```
id: UUID (PK)
name: String
slug: String (unique, for email)
email: String
default_payment_terms: Integer (days)
default_currency: String (ISO 4217)
eu_regulation_enabled: Boolean
created_at: Timestamp
updated_at: Timestamp
```

#### User
```
id: UUID (PK)
company_id: UUID (FK)
email: String (unique)
password_hash: String
name: String
timezone: String
email_notifications: JSONB
created_at: Timestamp
last_login_at: Timestamp
```

#### Customer
```
id: UUID (PK)
company_id: UUID (FK)
name: String
email: String
contact_person: String (nullable)
default_payment_terms: Integer (nullable)
notes: Text (nullable)
created_at: Timestamp
updated_at: Timestamp
```

#### Invoice
```
id: UUID (PK)
company_id: UUID (FK)
customer_id: UUID (FK)
invoice_number: String
amount: Decimal(10,2)
currency: String (ISO 4217)
invoice_date: Date
payment_terms_days: Integer
due_date: Date
status: Enum (pending, due_soon, overdue, paid)
file_url: String (nullable)
last_reminder_date: Timestamp (nullable)
next_action_date: Timestamp (nullable)
reminder_sequence_step: Integer (default 0)
source: Enum (manual, upload, bulk_upload, csv_import, api_sync, email_forward)
upload_item_id: UUID (FK → InvoiceUploadItem, nullable)
ocr_processed: Boolean (default false)
ocr_confidence_score: Decimal(3,2) (nullable, 0.00-1.00)
ocr_extracted_data: JSONB (nullable)
external_id: String (nullable, ID in source accounting system)
external_provider: String (nullable, e.g., 'sevdesk', 'xero')
external_synced_at: Timestamp (nullable)
external_sync_status: Enum (not_synced, synced, sync_failed) (default 'not_synced')
created_at: Timestamp
updated_at: Timestamp

Index: company_id, customer_id, status, due_date, external_id, source
```

#### Payment
```
id: UUID (PK)
invoice_id: UUID (FK)
amount: Decimal(10,2)
payment_date: Date
payment_method: Enum (bank_transfer, check, cash, other)
source: Enum (manual, csv_import, api_sync)
notes: Text (nullable)
created_at: Timestamp
```

#### ReminderEvent
```
id: UUID (PK)
invoice_id: UUID (FK)
template_type: Enum (friendly, firm)
sent_at: Timestamp
recipient_email: String
delivery_status: Enum (sent, failed, bounced)
opened_at: Timestamp (nullable)
is_manual: Boolean (default false)
created_at: Timestamp
```

#### ReminderSequence
```
id: UUID (PK)
company_id: UUID (FK)
steps: JSONB
  [
    {day_offset: -5, template: 'friendly', enabled: true},
    {day_offset: 0, template: 'friendly', enabled: true},
    {day_offset: 7, template: 'friendly', enabled: true},
    {day_offset: 21, template: 'firm', enabled: true}
  ]
created_at: Timestamp
updated_at: Timestamp
```

#### EmailTemplate
```
id: UUID (PK)
company_id: UUID (FK)
template_type: Enum (friendly, firm)
subject: String
body: Text (HTML)
created_at: Timestamp
updated_at: Timestamp
```

### 6.3 AI Layer Entities (Post-MVP)

#### AIConversation
```
id: UUID (PK)
invoice_id: UUID (FK)
customer_id: UUID (FK)
status: Enum (active, paused, completed, escalated)
autonomy_level: Enum (full, supervised, assisted)
current_stage: Enum (initial_outreach, follow_up, negotiation, escalated, resolved)
total_messages_sent: Integer
total_responses_received: Integer
last_action_at: Timestamp
next_action_at: Timestamp
escalation_reason: Text (nullable)
outcome: Enum (paid, payment_plan, dispute, churned, written_off) (nullable)
created_at: Timestamp
updated_at: Timestamp

Index: invoice_id, customer_id, status, next_action_at
```

#### AIMessage
```
id: UUID (PK)
conversation_id: UUID (FK)
direction: Enum (outbound, inbound)
channel: Enum (email, phone_script, linkedin)
message_type: Enum (ai_generated, human_approved, human_written, customer_reply)
content: Text
subject: Text (nullable)
sentiment_score: Decimal(3,2) (nullable, -1.0 to 1.0)
intent_classification: String (nullable)
confidence_score: Decimal(3,2) (nullable, 0.00 to 1.00)
ai_reasoning: Text (nullable)
delivery_status: Enum (draft, approved, sent, delivered, failed, opened, clicked)
sent_at: Timestamp (nullable)
opened_at: Timestamp (nullable)
created_at: Timestamp

Index: conversation_id, direction, sent_at
```

#### AIAction
```
id: UUID (PK)
conversation_id: UUID (FK)
action_type: Enum (send_message, schedule_follow_up, offer_payment_plan, escalate, pause, resume, mark_paid)
status: Enum (pending_approval, approved, executed, rejected, cancelled)
ai_confidence: Decimal(3,2) (0.00 to 1.00)
ai_reasoning: Text
human_reviewer_id: UUID (FK, nullable)
human_decision_at: Timestamp (nullable)
human_notes: Text (nullable)
executed_at: Timestamp (nullable)
created_at: Timestamp

Index: conversation_id, status, created_at
```

#### PaymentPrediction
```
id: UUID (PK)
invoice_id: UUID (FK)
prediction_date: Date
prob_7_days: Decimal(3,2)
prob_14_days: Decimal(3,2)
prob_30_days: Decimal(3,2)
prob_by_due_date: Decimal(3,2)
expected_payment_date: Date
confidence_score: Decimal(3,2)
model_version: String
feature_importance: JSONB
actual_payment_date: Date (nullable, filled when paid)
created_at: Timestamp

Index: invoice_id, prediction_date
```

#### CustomerRiskScore
```
id: UUID (PK)
customer_id: UUID (FK)
score_date: Date
risk_score: Integer (0-100)
risk_category: Enum (low, medium, high, critical)
payment_history_score: Integer (0-100)
outstanding_balance_score: Integer (0-100)
trend_score: Integer (0-100)
external_signal_score: Integer (0-100)
contributing_factors: JSONB
model_version: String
created_at: Timestamp

Index: customer_id, score_date
```

#### CashFlowForecast
```
id: UUID (PK)
company_id: UUID (FK)
forecast_date: Date
target_week_start: Date
expected_amount: Decimal(12,2)
lower_bound: Decimal(12,2)
upper_bound: Decimal(12,2)
confidence_level: Decimal(3,2)
contributing_invoices: JSONB
actual_amount: Decimal(12,2) (nullable, filled after week completes)
model_version: String
created_at: Timestamp

Index: company_id, forecast_date, target_week_start
```

#### AILearningEvent
```
id: UUID (PK)
event_type: Enum (action_outcome, user_edit, user_override, customer_feedback)
conversation_id: UUID (FK, nullable)
action_id: UUID (FK, nullable)
original_value: JSONB
outcome_value: JSONB
learning_signal: Enum (positive, negative, neutral)
processed: Boolean (default false)
created_at: Timestamp

Index: event_type, processed, created_at
```

### 6.4 Extensions to Existing Entities (Post-MVP AI)

#### Invoice (AI additions)
```
+ ai_conversation_id: UUID (FK, nullable)
+ payment_probability_7d: Decimal(3,2) (nullable)
+ payment_probability_30d: Decimal(3,2) (nullable)
+ expected_payment_date: Date (nullable)
+ prediction_updated_at: Timestamp (nullable)
+ anomaly_flags: JSONB (nullable)
```

#### Customer (AI additions)
```
+ risk_score: Integer (nullable, 0-100)
+ risk_category: Enum (low, medium, high, critical) (nullable)
+ risk_updated_at: Timestamp (nullable)
+ ai_customer_summary: Text (nullable)
+ avg_days_to_pay: Decimal(5,2) (nullable)
+ payment_reliability_score: Decimal(3,2) (nullable, 0.00-1.00)
+ preferred_contact_channel: Enum (email, phone, linkedin) (nullable)
+ preferred_contact_time: JSONB (nullable)
+ relationship_value_score: Decimal(10,2) (nullable)
```

### 6.5 Relationships

**Core (MVP):**
- Company → Users (1:N)
- Company → Customers (1:N)
- Company → Invoices (1:N)
- Company → ReminderSequence (1:1)
- Company → EmailTemplates (1:N)
- Company → IntegrationProviders (1:N)
- Company → InvoiceUploadBatches (1:N)
- Company → CSVImportProfiles (1:N)
- Customer → Invoices (1:N)
- Invoice → Payments (1:N)
- Invoice → ReminderEvents (1:N)
- InvoiceUploadBatch → InvoiceUploadItems (1:N)
- InvoiceUploadItem → Invoice (1:1, nullable)
- IntegrationProvider → SyncLogs (1:N)
- IntegrationProvider → WebhookEvents (1:N)

**AI Layer (Post-MVP):**
- Invoice → AIConversation (1:1)
- Customer → AIConversations (1:N)
- AIConversation → AIMessages (1:N)
- AIConversation → AIActions (1:N)
- AIConversation → AILearningEvents (1:N)
- Invoice → PaymentPredictions (1:N)
- Customer → CustomerRiskScores (1:N)
- Company → CashFlowForecasts (1:N)

---

## 7. API Endpoints

### 7.1 Invoice Ingestion APIs (MVP)

```
# Single Upload
POST   /api/invoices/upload                      - Upload single invoice file (triggers OCR)
GET    /api/invoices/:id/ocr-results             - Get OCR extraction results
POST   /api/invoices/:id/process-ocr             - Re-process OCR for invoice

# Bulk Upload
POST   /api/invoices/upload/batch                - Upload batch of files
GET    /api/invoices/upload/batch/:id            - Get batch status and items
GET    /api/invoices/upload/batch/:id/items      - List items in batch
POST   /api/invoices/upload/batch/:id/accept-all - Accept all high-confidence items
POST   /api/invoices/upload/item/:id/accept      - Accept single item
POST   /api/invoices/upload/item/:id/reject      - Reject single item

# CSV Import
POST   /api/invoices/import/csv                  - Upload CSV file
POST   /api/invoices/import/csv/preview          - Preview CSV with column mapping
POST   /api/invoices/import/csv/execute           - Execute CSV import with mappings
GET    /api/invoices/import/csv/profiles          - List saved CSV profiles
POST   /api/invoices/import/csv/profiles          - Save CSV mapping profile
DELETE /api/invoices/import/csv/profiles/:id      - Delete CSV profile
GET    /api/invoices/import/csv/template          - Download CSV template

# Import Payments (CSV)
POST   /api/payments/import/csv                  - Upload payment CSV
POST   /api/payments/import/csv/preview          - Preview matches
POST   /api/payments/import/csv/execute           - Execute payment matching
```

### 7.2 Third-Party Integration APIs (MVP)

```
# Provider Management
GET    /api/integrations                          - List all integrations
GET    /api/integrations/:provider                - Get integration details
POST   /api/integrations/:provider/connect        - Initiate OAuth flow
GET    /api/integrations/:provider/callback       - OAuth callback handler
POST   /api/integrations/:provider/disconnect     - Disconnect integration
PUT    /api/integrations/:provider/config         - Update sync configuration

# Sync Operations
POST   /api/integrations/:provider/sync           - Trigger manual sync
GET    /api/integrations/:provider/sync-logs      - Get sync history
POST   /api/integrations/:provider/sync/retry     - Retry failed syncs

# Webhook (for custom integrations)
POST   /api/webhooks/:company-slug/invoices       - Receive invoice via webhook
GET    /api/webhooks/:company-slug/events          - List webhook events
POST   /api/webhooks/:company-slug/regenerate-key  - Regenerate API key
```

### 7.3 Core Invoice APIs (MVP)

```
GET    /api/invoices                              - List invoices (with filters)
GET    /api/invoices/:id                          - Get invoice detail
POST   /api/invoices                              - Create invoice (manual entry)
PUT    /api/invoices/:id                          - Update invoice
DELETE /api/invoices/:id                          - Delete invoice
POST   /api/invoices/:id/mark-paid                - Mark as paid
POST   /api/invoices/:id/send-reminder            - Send manual reminder
```

### 7.4 Collection Agent APIs (Post-MVP)

```
# Conversation Management
GET    /api/ai/conversations                      - List AI conversations
GET    /api/ai/conversations/:id                  - Get conversation detail
POST   /api/ai/conversations/:id/pause            - Pause AI handling
POST   /api/ai/conversations/:id/resume           - Resume AI handling
POST   /api/ai/conversations/:id/escalate         - Escalate to human
POST   /api/ai/conversations/:id/take-over        - Human takes over

# Action Management
GET    /api/ai/actions/pending                    - List pending approvals
POST   /api/ai/actions/:id/approve                - Approve AI action
POST   /api/ai/actions/:id/reject                 - Reject AI action
POST   /api/ai/actions/:id/modify                 - Modify and approve

# Message Management
GET    /api/ai/messages/:conversation_id          - Get conversation messages
POST   /api/ai/messages/:conversation_id/draft    - Create human message draft
POST   /api/ai/messages/:id/send                  - Send message

# Settings
GET    /api/ai/settings                           - Get AI settings
PUT    /api/ai/settings                           - Update AI settings
GET    /api/ai/settings/payment-plans             - Get payment plan rules
PUT    /api/ai/settings/payment-plans             - Update payment plan rules
```

### 7.5 Prediction APIs (Post-MVP)

```
# Invoice Predictions
GET    /api/ai/predictions/invoice/:id            - Get invoice payment prediction
POST   /api/ai/predictions/invoices/refresh       - Refresh all predictions

# Customer Risk
GET    /api/ai/risk/customer/:id                  - Get customer risk profile
GET    /api/ai/risk/customers                     - List all customer risk scores
GET    /api/ai/risk/alerts                        - Get risk alerts

# Cash Flow Forecast
GET    /api/ai/forecast                           - Get cash flow forecast
GET    /api/ai/forecast/history                   - Get forecast vs actuals history

# Recommendations
GET    /api/ai/recommendations                    - Get AI recommendations
POST   /api/ai/recommendations/:id/accept         - Accept recommendation
POST   /api/ai/recommendations/:id/dismiss        - Dismiss recommendation
```

### 7.6 Analytics APIs (Post-MVP)

```
GET    /api/ai/analytics/agent-performance        - Agent success metrics
GET    /api/ai/analytics/prediction-accuracy      - Model accuracy metrics
GET    /api/ai/analytics/learning-events          - Learning signal summary
```

---

## 8. Background Jobs

### 8.1 Invoice Ingestion Jobs (MVP)

#### OCR Processing Job
- **Trigger:** On-demand (file upload event)
- **Purpose:** Process uploaded PDFs with OCR
- **Concurrency:** Up to 5 parallel OCR jobs
- **Logic:**
  1. Dequeue file from processing queue
  2. Call OCR service (OpenAI Vision primary, AWS Textract fallback)
  3. Extract invoice fields with confidence scores
  4. Attempt customer matching (name/email fuzzy match)
  5. Store results in `InvoiceUploadItem.ocr_extracted_data`
  6. Update item status to `ready` or `failed`
  7. If batch: check if all items processed, update batch status
  8. Send WebSocket/SSE notification to user
- **Timeout:** 30 seconds per file
- **Error Handling:** Mark as failed, log error, allow manual retry

#### CSV Import Processing Job
- **Trigger:** On-demand (CSV import execute)
- **Purpose:** Process CSV rows into invoices
- **Logic:**
  1. Parse CSV with configured column mapping
  2. Validate each row against business rules
  3. Match customers (exact email, fuzzy name)
  4. Create new customers for unmatched rows
  5. Check for duplicates against existing invoices
  6. Create invoices in batches of 100
  7. Generate import report (success/skip/error counts)
  8. Notify user of completion

#### Third-Party Sync Job
- **Frequency:** Daily at configured time (default 2:00 AM) or manual trigger
- **Purpose:** Sync invoices and payments with connected accounting systems
- **Logic:**
  1. Get all companies with active integrations and auto-sync enabled
  2. For each integration:
     - Refresh OAuth token if needed
     - Fetch invoices changed since last sync
     - Compare with local invoices (by external_id or invoice_number)
     - Create/update invoices based on sync direction
     - Sync payment status
     - Sync customer data
     - Log sync results to SyncLog
     - Update `last_sync_at` timestamp
  3. Handle rate limits per provider
- **Error Handling:**
  - Retry failed API calls (3 attempts, exponential backoff)
  - Log errors to SyncLog
  - Notify user of sync failures via email
  - Continue processing other companies if one fails

#### Webhook Processing Job
- **Trigger:** On webhook receipt (event-driven)
- **Purpose:** Process incoming webhook payloads
- **Logic:**
  1. Validate API key and payload
  2. Store raw event in WebhookEvent table
  3. Parse and validate invoice data
  4. Create or update invoice
  5. Update webhook event status

### 8.2 Core Jobs (MVP)

#### Status Update Job
- **Frequency:** Every 6 hours
- **Purpose:** Update invoice statuses based on due dates
- **Logic:**
  - Find invoices where `due_date - 7 days <= NOW()` and status = 'pending' → set to 'due_soon'
  - Find invoices where `due_date <= NOW()` and status != 'paid' → set to 'overdue'

#### Reminder Sending Job
- **Frequency:** Every 4 hours
- **Purpose:** Send scheduled reminders
- **Logic:**
  - Find invoices where `next_action_date <= NOW()` and status != 'paid'
  - Get company's reminder sequence
  - Determine which step to send based on `reminder_sequence_step`
  - Send email, log event, update next action date

#### Daily Summary Email Job
- **Frequency:** Daily at 8 AM (user timezone)
- **Purpose:** Send daily summary to users who opted in
- **Content:** Total outstanding, new overdue, payments received, action items

### 8.3 AI Layer Jobs (Post-MVP)

#### Agent Decision Loop
- **Frequency:** Every 1 hour
- **Purpose:** Process agent decisions and execute approved actions
- **Logic:**
  1. Find conversations with `next_action_at <= NOW()`
  2. For each: load context, generate AI decision, execute or queue for approval
  3. Schedule next action

#### Response Processing Job
- **Frequency:** Every 15 minutes
- **Purpose:** Process incoming customer replies
- **Logic:**
  1. Check email inbox for new messages
  2. Match to existing conversations
  3. Classify intent and sentiment
  4. Update conversation state
  5. Trigger response or escalation

#### Payment Prediction Refresh
- **Frequency:** Daily at 3 AM
- **Purpose:** Update payment predictions for all open invoices

#### Customer Risk Score Refresh
- **Frequency:** Daily at 4 AM
- **Purpose:** Update risk scores for all customers

#### Cash Flow Forecast Generation
- **Frequency:** Daily at 5 AM
- **Purpose:** Generate weekly cash flow forecasts

#### Model Retraining Pipeline
- **Frequency:** Weekly (Sunday 2 AM)
- **Purpose:** Retrain ML models with new data

#### Learning Event Processing
- **Frequency:** Daily at 6 AM
- **Purpose:** Process learning signals from user actions

---

## 9. Technical Requirements

### 9.1 OCR & Document Processing

**Primary Provider:** OpenAI Vision API (GPT-4 Vision) for structured extraction
**Fallback Provider:** AWS Textract or Google Cloud Vision API
**Self-hosted Option:** PaddleOCR (for cost optimization at scale)

**Requirements:**
- <10 second processing for single-page invoice
- Parallel processing support (up to 5 concurrent)
- Structured output format (JSON) with confidence scores per field
- Support for PDF, PNG, JPG, JPEG
- File deduplication via SHA-256 hashing
- Cost monitoring and per-company usage limits

### 9.2 LLM Integration (Post-MVP)

**Primary Provider:** OpenAI GPT-4 or Anthropic Claude
**Use Cases:** Message generation, reply classification, sentiment analysis, customer summaries

**Requirements:**
- API abstraction layer (support multiple providers)
- Prompt versioning and management
- Response caching for repeated queries
- Cost monitoring and limits
- Fallback to simpler model if primary unavailable

### 9.3 ML Infrastructure (Post-MVP)

**Model Serving:**
- Scikit-learn or XGBoost models for predictions
- Model versioning and A/B testing capability
- Feature store for consistent feature engineering
- Monitoring for model drift

**Training Pipeline:**
- Weekly automated retraining
- Data validation checks
- Model performance comparison
- Automated rollback if performance degrades

### 9.4 Integration Infrastructure (MVP)

**Requirements:**
- OAuth 2.0 client for SevDesk, Xero, LexOffice
- Encrypted token storage (AES-256)
- Token auto-refresh before expiry
- Rate limit management per provider
- Retry logic with exponential backoff
- Webhook receiver with signature validation
- Integration health monitoring

### 9.5 File Storage (MVP)

**Requirements:**
- S3-compatible object storage (AWS S3 or MinIO)
- Organized by company: `/{company_id}/invoices/{year}/{file_hash}.pdf`
- Pre-signed URLs for secure file access (expires in 1 hour)
- Automatic cleanup of orphaned files (weekly job)
- Maximum storage per company: 10GB (MVP)

### 9.6 Vector Database (Post-MVP, Optional)

**Use Cases:** Customer communication embeddings, semantic search, similar customer situations
**Options:** Pinecone, Weaviate, or Chroma

### 9.7 Event Streaming (Post-MVP)

**Use Cases:** AI action tracking, real-time learning signals, audit trail
**Options:** Redis Streams, Kafka, or database-based event log

---

## 10. Privacy & Security

### 10.1 Data Handling

- **File Storage:** All uploaded files stored encrypted at rest (AES-256)
- **OCR Processing:** Invoice images sent to OCR provider -- no sensitive bank details extracted for storage
- **LLM Data:** Never send sensitive financial data to external LLMs (post-MVP)
- **Anonymization:** Customer names/amounts can be sent; full bank details cannot
- **Logging:** Log system actions but redact sensitive content (amounts, names) in debug logs
- **Retention:** Invoice data follows 7-year accounting retention; AI conversation data same policy
- **Integration Tokens:** Encrypted at rest, never logged, auto-rotated on refresh

### 10.2 User Consent

- **AI Disclosure:** Users must acknowledge AI will communicate with their customers (post-MVP)
- **Customer Disclosure:** Optional footer in AI emails: "This message was composed with AI assistance"
- **Opt-out:** Customers can request human-only communication
- **Integration Consent:** User explicitly authorizes each third-party connection
- **Data Sync Consent:** Clear explanation of what data is synced before authorization

### 10.3 Audit Trail

- Every invoice ingestion logged with source and method
- Every integration sync logged with details and outcomes
- Every AI action logged with timestamp, action type, AI reasoning, confidence score, human approval
- Every user action on invoices logged (create, edit, delete, mark paid)
- Audit logs retained for 7 years (GDPR + accounting compliance)

### 10.4 GDPR Compliance

- Data export: User can export all data (invoices, customers, history) as JSON/CSV
- Data deletion: User can delete account and all associated data
- Data portability: Standard export formats for migration
- Third-party data processing: DPA (Data Processing Agreement) with all providers
- Right to explanation: AI decisions are explainable (reasoning stored)

---

## 11. Success Metrics

### 11.1 Invoice Ingestion Metrics (MVP)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Single upload time-to-tracked | < 2 minutes | From upload click to confirmed invoice |
| Bulk upload throughput | 50 invoices in < 8 min | Processing + review time |
| OCR accuracy rate | > 80% high-confidence | % of invoices with all fields auto-extracted correctly |
| CSV import success rate | > 95% | % of valid rows successfully imported |
| Integration sync success rate | > 98% | % of syncs completing without errors |
| Ingestion method adoption | Track distribution | % using upload vs CSV vs sync vs manual |

### 11.2 Collection Agent Metrics (Post-MVP)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Autonomous handling rate | > 80% | % of invoices resolved without human intervention |
| Response time | < 4 hours | Time from customer reply to AI response |
| Escalation rate | < 15% | % of conversations escalated to human |
| User override rate | < 10% | % of AI drafts modified by users |
| Payment plan success rate | > 70% | % of offered plans that result in payment |

### 11.3 Prediction Accuracy Metrics (Post-MVP)

| Metric | Target | Measurement |
|--------|--------|-------------|
| 7-day payment prediction AUROC | > 0.85 | Model accuracy on 7-day predictions |
| Expected payment date accuracy | ±3 days for 70% | Prediction vs actual payment date |
| Risk score stability | < 5% daily variance | Score shouldn't fluctuate wildly |
| Cash flow forecast accuracy | ±10% | Predicted vs actual weekly cash flow |

### 11.4 Business Impact Metrics

| Metric | Target (MVP) | Target (AI Layer) |
|--------|-------------|-------------------|
| DSO reduction | 10-30% | 40-50% |
| Collection rate | > 90% | > 95% |
| Time to first payment | Baseline | -30% reduction |
| Customer churn from collections | N/A | < 2% |
| Time saved per week | 5+ hours | 10+ hours |

---

## 12. Implementation Roadmap

### Phase 1: Core Ingestion + Tracking (Weeks 1-4) -- MVP

- [ ] Single invoice upload with OCR integration
- [ ] Bulk upload pipeline (multi-file, batch review queue)
- [ ] CSV invoice import with column mapping
- [ ] Manual invoice entry form
- [ ] Due date engine and status state machine
- [ ] Basic dashboard (total outstanding, overdue list, DSO)
- [ ] Invoice list with filters and search
- [ ] Customer management (CRUD, payment terms)

### Phase 2: Reminders + Integrations (Weeks 5-8) -- MVP

- [ ] Reminder sequence configuration
- [ ] Email template editor (friendly, firm)
- [ ] Automated reminder sending job
- [ ] Email forwarding ingestion
- [ ] SevDesk integration (OAuth, bidirectional sync)
- [ ] Payment tracking (manual mark paid, CSV payment import)
- [ ] Daily summary email
- [ ] Company and user settings
- [ ] CSV import profile saving

### Phase 3: Additional Integrations (Weeks 9-12) -- V1

- [ ] Xero integration (one-way import)
- [ ] LexOffice integration (one-way import)
- [ ] Generic webhook integration for custom systems
- [ ] Integration health dashboard and sync logs
- [ ] Improved OCR accuracy with feedback loop
- [ ] Email open/click tracking for reminders

### Phase 4: AI Foundation (Weeks 13-16) -- Post-MVP

- [ ] Set up LLM integration layer
- [ ] Implement basic AI message generation
- [ ] Build AI conversation data model
- [ ] Create Agent Control Center UI skeleton
- [ ] Implement manual approval workflow for AI actions

### Phase 5: Autonomous Agent (Weeks 17-20) -- Post-MVP

- [ ] Implement customer reply classification
- [ ] Build adaptive cadence logic
- [ ] Add payment plan negotiation
- [ ] Implement escalation triggers and workflow
- [ ] Complete Agent Control Center UI

### Phase 6: Predictions + Intelligence (Weeks 21-24) -- Post-MVP

- [ ] Build payment prediction model (requires 6+ months data)
- [ ] Implement customer risk scoring
- [ ] Create cash flow forecasting
- [ ] Build AI Insights Hub UI
- [ ] Implement alert system

### Phase 7: Learning + Optimization (Weeks 25-28) -- Post-MVP

- [ ] Implement learning event tracking
- [ ] Build model retraining pipeline
- [ ] Add A/B testing framework
- [ ] Create analytics dashboards
- [ ] Performance tuning and optimization

---

## 13. Dependencies & Risks

### 13.1 Dependencies

| Dependency | Type | Phase | Mitigation |
|------------|------|-------|------------|
| OCR service (OpenAI Vision / Textract) | External | MVP | Multi-provider support, fallback chain |
| Email service (SES / SendGrid) | External | MVP | Multiple ESP support, deliverability monitoring |
| SevDesk API access | External | MVP | API versioning awareness, fallback to CSV import |
| Xero / LexOffice API access | External | V1 | Independent of MVP, degrade gracefully |
| Object storage (S3 / MinIO) | Infrastructure | MVP | Self-hosted MinIO as backup |
| LLM API (OpenAI / Anthropic) | External | Post-MVP | Multi-provider, caching, fallbacks |
| Historical data for ML | Internal | Post-MVP | Need 6+ months of payment data; start collecting from Day 1 |
| User adoption | Internal | All | Gradual rollout, supervised AI mode first |

### 13.2 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OCR accuracy too low for user trust | Medium | High | Side-by-side review UI, confidence scores, easy manual correction |
| Bulk upload overwhelms OCR budget | Medium | Medium | Rate limiting, usage caps per plan, queuing |
| CSV format variations cause import failures | High | Medium | Flexible parser, template download, saved profiles |
| Third-party API changes break sync | Medium | Medium | Adapter pattern, versioned clients, monitoring |
| AI sends inappropriate collection message | Medium | High | Strict guardrails, approval workflow, monitoring |
| Prediction model inaccurate early on | High | Medium | Start conservative, require 6mo data, A/B test |
| Customer complains about AI communication | Low | High | Disclosure option, human takeover, opt-out |
| LLM costs exceed budget | Medium | Medium | Caching, simpler models for routine tasks, usage limits |
| Data privacy concerns (GDPR) | Low | High | Clear consent, no sensitive data to LLMs, encryption at rest |
| Integration token leakage | Low | Critical | Encrypted storage, never logged, audit trail |

---

## Document Control

**Approval Required From:**
- [ ] Product Manager
- [ ] Engineering Lead
- [ ] AI/ML Lead
- [ ] Legal/Compliance
- [ ] CEO

**Change Log:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-25 | AI Product Team | Initial AI-native specification |
| 2.0 | 2026-02-07 | Product Team | Added Invoice Ingestion Hub (single, bulk, CSV), Third-Party Accounting Integration module (SevDesk, Xero, LexOffice, webhook), restructured for MVP-first approach, fixed section numbering, updated data model with ingestion entities, revised roadmap and success metrics |

---

**Next Steps:**
1. Review and approve this specification
2. Prioritize MVP features for Sprint 1 (Single Upload + CSV Import)
3. Create technical architecture document for ingestion pipeline
4. Set up OCR provider accounts and test invoice extraction accuracy
5. Design UI mockups for upload flows and batch review queue
6. Estimate development timeline per phase
7. Begin Sprint 1 planning
