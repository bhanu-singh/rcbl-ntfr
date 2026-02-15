# Development Planning Document
## Receivable Notification System - Implementation Roadmap

**Document Version:** 1.0  
**Created:** January 25, 2026  
**Target Release:** MVP in 10 weeks  
**Team Size:** 4-5 engineers (2 backend, 1 frontend, 1 full-stack, 1 QA/DevOps)

---

## 1. Executive Summary

### 1.1 Project Overview
Building an AI-enhanced receivable management system with OCR capabilities and SevDesk integration. The system will help European SMEs reduce DSO through automated invoice tracking and intelligent payment reminders.

### 1.2 Development Approach
- **Agile/Scrum:** 2-week sprints
- **MVP First:** Core functionality before AI enhancements
- **Vertical Slicing:** Complete features end-to-end
- **Continuous Delivery:** Deploy to staging every sprint

### 1.3 Success Criteria
- All P0 stories completed
- 90%+ test coverage for critical paths
- Performance benchmarks met
- Security audit passed
- UAT completed with 5 pilot users

---

## 2. Epic Breakdown

### Epic 1: Foundation & Infrastructure (Weeks 1-2)
**Goal:** Set up technical foundation for development

**Stories:**

#### Story 1.1: Project Setup & Architecture
**Priority:** P0  
**Points:** 8  
**Assignee:** Tech Lead

**Description:**
Set up project repository, CI/CD pipeline, and development environment.

**Acceptance Criteria:**
- [ ] Monorepo structure with backend and frontend
- [ ] Docker compose for local development
- [ ] CI pipeline (GitHub Actions) with lint, test, build
- [ ] Staging environment on Fly.io/Railway
- [ ] Database migrations system
- [ ] Environment configuration management
- [ ] Logging and monitoring setup (Sentry)
- [ ] API documentation structure (OpenAPI/Swagger)

**Technical Notes:**
- Backend: Rust (Axum) + PostgreSQL + Redis
- Frontend: React + TypeScript + TailwindCSS
- Use SQLx for type-safe database queries

**Dependencies:** None

---

#### Story 1.2: Authentication & User Management
**Priority:** P0  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Implement user registration, login, and session management.

**Acceptance Criteria:**
- [ ] User registration with email verification
- [ ] Login with JWT tokens
- [ ] Password reset flow
- [ ] Password hashing (bcrypt)
- [ ] Session management
- [ ] Protected route middleware
- [ ] User profile management

**API Endpoints:**
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- POST /api/auth/forgot-password
- GET /api/auth/me

**Dependencies:** Story 1.1

---

#### Story 1.3: Database Schema & Migrations
**Priority:** P0  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Create database schema for all core entities.

**Acceptance Criteria:**
- [ ] Migration files for all tables
- [ ] Seed data for testing
- [ ] Database indexes for performance
- [ ] Entity relationship validation
- [ ] Rollback scripts

**Tables:**
- companies
- users
- customers
- invoices
- payments
- reminder_events
- reminder_sequences
- email_templates
- accounting_integrations
- sync_logs

**Dependencies:** Story 1.1

---

#### Story 1.4: Frontend Foundation
**Priority:** P0  
**Points:** 5  
**Assignee:** Frontend Engineer

**Description:**
Set up frontend architecture with routing, state management, and UI components.

**Acceptance Criteria:**
- [ ] React app with TypeScript
- [ ] React Router setup
- [ ] TanStack Query for API state
- [ ] Zustand for global state
- [ ] TailwindCSS configuration
- [ ] shadcn/ui component library
- [ ] Axios HTTP client with interceptors
- [ ] Error boundary setup
- [ ] Loading state components

**Dependencies:** Story 1.1

---

### Epic 2: Invoice Management Core (Weeks 2-4)
**Goal:** Build core invoice tracking functionality

#### Story 2.1: Company & Customer Management
**Priority:** P0  
**Points:** 5  
**Assignee:** Full-stack Engineer

**Description:**
Allow users to manage their company profile and customer database.

**Acceptance Criteria:**
- [ ] Company settings page
- [ ] Customer list view with search
- [ ] Add/edit customer form
- [ ] Customer detail page
- [ ] Customer-Invoice relationship
- [ ] Validation for required fields

**API Endpoints:**
- CRUD for /api/customers
- PUT /api/settings/company

**UI Components:**
- CustomerTable
- CustomerForm
- CustomerDetail

**Dependencies:** Stories 1.2, 1.3, 1.4

---

#### Story 2.2: Manual Invoice Creation
**Priority:** P0  
**Points:** 5  
**Assignee:** Full-stack Engineer

**Description:**
Allow users to manually create and manage invoices.

**Acceptance Criteria:**
- [ ] Invoice creation form
- [ ] Due date auto-calculation
- [ ] Customer selection dropdown
- [ ] Payment terms selection
- [ ] Invoice list view with filters
- [ ] Invoice detail page
- [ ] Edit and delete functionality
- [ ] Duplicate invoice number validation

**UI Components:**
- InvoiceForm
- InvoiceTable
- InvoiceDetail
- StatusBadge

**Dependencies:** Story 2.1

---

#### Story 2.3: File Upload & Storage
**Priority:** P0  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Implement secure file upload for invoice attachments.

**Acceptance Criteria:**
- [ ] File upload endpoint with validation
- [ ] S3/MinIO integration
- [ ] File type validation (PDF, CSV, images)
- [ ] File size limits (10MB)
- [ ] Virus scanning (ClamAV or similar)
- [ ] Secure file URLs (signed URLs)
- [ ] Batch upload support (up to 10 files)

**API Endpoints:**
- POST /api/invoices/upload
- GET /api/invoices/:id/download

**Dependencies:** Story 1.3

---

#### Story 2.4: Invoice Status Management
**Priority:** P0  
**Points:** 3  
**Assignee:** Backend Engineer

**Description:**
Implement automatic status transitions and background jobs.

**Acceptance Criteria:**
- [ ] Status enum: pending, due_soon, overdue, paid
- [ ] Background job for status updates (every 6 hours)
- [ ] Transition logic:
  - pending → due_soon (7 days before due)
  - pending/due_soon → overdue (on due date)
- [ ] Status change logging
- [ ] Manual status override capability

**Technical Notes:**
- Use tokio-cron or similar for scheduling
- Implement idempotent job execution

**Dependencies:** Story 2.2

---

### Epic 3: OCR & Intelligent Processing (Weeks 3-5)
**Goal:** Implement AI-powered invoice data extraction

#### Story 3.1: OCR Service Integration
**Priority:** P0  
**Points:** 8  
**Assignee:** Backend Engineer

**Description:**
Integrate OCR service for automatic invoice data extraction.

**Acceptance Criteria:**
- [ ] OCR service abstraction layer
- [ ] OpenAI Vision API integration
- [ ] Fallback to AWS Textract
- [ ] Structured data extraction:
  - Invoice number
  - Invoice date
  - Due date
  - Customer name
  - Amount
  - Currency
  - Payment terms
- [ ] Confidence scoring per field
- [ ] Error handling for failed OCR
- [ ] OCR result caching

**Technical Notes:**
- Create OCR provider trait/interface
- Implement retry logic with exponential backoff
- Store raw OCR results for debugging

**Dependencies:** Story 2.3

---

#### Story 3.2: OCR Review & Validation UI
**Priority:** P0  
**Points:** 5  
**Assignee:** Frontend Engineer

**Description:**
Build UI for reviewing and correcting OCR-extracted data.

**Acceptance Criteria:**
- [ ] Side-by-side PDF preview and form
- [ ] Visual confidence indicators:
  - Green: High confidence (>80%)
  - Yellow: Medium confidence (50-80%)
  - Red: Low confidence (<50%)
- [ ] Inline field editing
- [ ] "Accept All" button for high-confidence extractions
- [ ] "Re-run OCR" button
- [ ] Progress indicator during processing
- [ ] Mobile-responsive layout

**UI Components:**
- OCRReviewModal
- PDFViewer
- ConfidenceIndicator
- ExtractedDataForm

**Dependencies:** Story 3.1

---

#### Story 3.3: AI-Powered Data Validation
**Priority:** P1  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Implement intelligent validation and error resolution for OCR data.

**Acceptance Criteria:**
- [ ] Customer name fuzzy matching
- [ ] Duplicate invoice detection
- [ ] Amount validation (reasonable range)
- [ ] Date validation (not in future, reasonable range)
- [ ] Payment terms extraction from text
- [ ] Auto-correction suggestions
- [ ] Anomaly flagging (unusual amounts, etc.)

**Examples:**
- "Acme Corp Ltd" → match to "Acme Corporation"
- Detect duplicate invoice numbers
- Flag amount 10x higher than average

**Dependencies:** Story 3.1

---

#### Story 3.4: Email Invoice Ingestion
**Priority:** P1  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Implement email forwarding for automatic invoice capture.

**Acceptance Criteria:**
- [ ] Unique email address per company
- [ ] Email webhook endpoint
- [ ] Attachment extraction (PDF)
- [ ] Email body text extraction
- [ ] Sender email mapping to customers
- [ ] Draft invoice creation from email
- [ ] User notification: "New invoice received"
- [ ] Spam filtering basics

**Technical Notes:**
- Use webhook from email service (SendGrid, AWS SES)
- Store raw email for audit
- Implement idempotent processing

**Dependencies:** Stories 2.3, 3.1

---

### Epic 4: Automated Reminders (Weeks 4-6)
**Goal:** Build intelligent reminder system

#### Story 4.1: Reminder Sequence Configuration
**Priority:** P0  
**Points:** 3  
**Assignee:** Full-stack Engineer

**Description:**
Allow users to configure reminder schedules and templates.

**Acceptance Criteria:**
- [ ] Default reminder sequence:
  - Day -5: Due soon
  - Day 0: Due today
  - Day +7: Friendly overdue
  - Day +21: Firm overdue
- [ ] Enable/disable individual reminders
- [ ] Adjust day offsets
- [ ] Visual timeline display
- [ ] Per-company configuration

**UI Components:**
- ReminderSequenceEditor
- TimelineVisualization

**Dependencies:** Story 2.4

---

#### Story 4.2: Email Template System
**Priority:** P0  
**Points:** 5  
**Assignee:** Full-stack Engineer

**Description:**
Build customizable email templates with variables.

**Acceptance Criteria:**
- [ ] Default templates (friendly, firm)
- [ ] Template variable system:
  - {customer_name}
  - {invoice_number}
  - {invoice_amount}
  - {due_date}
  - {days_overdue}
- [ ] Rich text editor for templates
- [ ] Live preview with sample data
- [ ] Template versioning

**UI Components:**
- TemplateEditor
- TemplatePreview
- VariableSelector

**Dependencies:** Story 4.1

---

#### Story 4.3: SMTP & Email Sending
**Priority:** P0  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Implement email delivery infrastructure.

**Acceptance Criteria:**
- [ ] System email sending (AWS SES/SendGrid)
- [ ] Custom SMTP configuration
- [ ] Email queue system (Redis + worker)
- [ ] Retry logic (3 attempts, exponential backoff)
- [ ] Bounce handling
- [ ] Delivery status tracking
- [ ] Rate limiting (100 emails/hour)

**Technical Notes:**
- Use background job queue (Bull/BullMQ)
- Implement circuit breaker for email provider
- Store email logs for compliance

**Dependencies:** Story 1.1

---

#### Story 4.4: Automated Reminder Engine
**Priority:** P0  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Build background job system for sending reminders automatically.

**Acceptance Criteria:**
- [ ] Scheduled job every 4 hours
- [ ] Query invoices needing reminders
- [ ] Check reminder sequence rules
- [ ] Generate personalized emails
- [ ] Attach invoice PDF
- [ ] Update invoice reminder tracking
- [ ] Log all reminder events
- [ ] Handle timezone correctly

**Algorithm:**
```
For each company:
  For each invoice where status != 'paid':
    Get company's reminder sequence
    Determine current step based on days relative to due_date
    Check if reminder already sent for this step
    If not sent and step is enabled:
      Generate email from template
      Add to send queue
      Update invoice.next_action_date
```

**Dependencies:** Stories 4.2, 4.3

---

#### Story 4.5: Manual Reminder Override
**Priority:** P1  
**Points:** 3  
**Assignee:** Frontend Engineer

**Description:**
Allow users to send manual reminders outside the sequence.

**Acceptance Criteria:**
- [ ] "Send Reminder Now" button on invoice detail
- [ ] Template selection dropdown
- [ ] Email preview before sending
- [ ] Inline editing of email content
- [ ] Immediate send functionality
- [ ] Log as manual reminder

**UI Components:**
- SendReminderModal
- EmailPreview

**Dependencies:** Story 4.4

---

### Epic 5: Payment Tracking (Weeks 5-6)
**Goal:** Implement payment recording and matching

#### Story 5.1: Manual Payment Marking
**Priority:** P0  
**Points:** 3  
**Assignee:** Full-stack Engineer

**Description:**
Allow users to mark invoices as paid.

**Acceptance Criteria:**
- [ ] "Mark as Paid" button
- [ ] Payment date input (default: today)
- [ ] Payment amount (default: full amount)
- [ ] Payment method dropdown
- [ ] Notes field
- [ ] Confirmation modal
- [ ] Undo capability (5-second window)
- [ ] Partial payment support
- [ ] Update invoice status to "paid"
- [ ] Stop future reminders

**UI Components:**
- MarkPaidModal
- PaymentHistory

**Dependencies:** Story 2.4

---

#### Story 5.2: CSV Payment Import
**Priority:** P1  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Import bank statements to auto-match payments.

**Acceptance Criteria:**
- [ ] CSV upload endpoint
- [ ] Column mapping UI
- [ ] Auto-match by:
  - Exact amount
  - Invoice number in reference
  - Customer name
- [ ] Review screen for matches
- [ ] Manual match override
- [ ] Bulk mark as paid
- [ ] Support common formats (QuickBooks, Xero)

**UI Components:**
- CSVUploadModal
- PaymentMatcher
- ColumnMapper

**Dependencies:** Story 5.1

---

### Epic 6: SevDesk Integration (Weeks 6-8)
**Goal:** Build accounting software integration

#### Story 6.1: SevDesk OAuth Integration
**Priority:** P0  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Implement OAuth flow for SevDesk connection.

**Acceptance Criteria:**
- [ ] OAuth 2.0 flow implementation
- [ ] Connect/Disconnect endpoints
- [ ] Secure token storage (encrypted)
- [ ] Token refresh logic
- [ ] Connection status endpoint
- [ ] Error handling for auth failures

**API Endpoints:**
- POST /api/integrations/sevdesk/connect
- GET /api/integrations/sevdesk/callback
- POST /api/integrations/sevdesk/disconnect
- GET /api/integrations/sevdesk/status

**Dependencies:** Story 1.3

---

#### Story 6.2: SevDesk Invoice Sync
**Priority:** P0  
**Points:** 8  
**Assignee:** Backend Engineer

**Description:**
Implement bidirectional invoice synchronization.

**Acceptance Criteria:**
- [ ] Import invoices from SevDesk
- [ ] Map SevDesk fields to system fields
- [ ] Create/update invoices based on sync
- [ ] Export invoices to SevDesk
- [ ] Handle conflicts (last write wins)
- [ ] Sync status tracking per invoice
- [ ] Batch processing (100 per call)
- [ ] Rate limit handling

**Data Mapping:**
- SevDesk status → System status
- Contact → Customer
- Invoice fields mapping

**Background Job:**
- Daily sync at 2 AM
- Manual sync trigger
- Sync logging

**Dependencies:** Story 6.1

---

#### Story 6.3: Payment Status Sync
**Priority:** P1  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Sync payment status between systems.

**Acceptance Criteria:**
- [ ] Import payment status from SevDesk
- [ ] Export payment status to SevDesk
- [ ] Match payments by invoice number
- [ ] Handle partial payments
- [ ] Payment reconciliation report
- [ ] Conflict resolution UI

**Dependencies:** Story 6.2

---

#### Story 6.4: SevDesk Integration UI
**Priority:** P1  
**Points:** 3  
**Assignee:** Frontend Engineer

**Description:**
Build UI for managing SevDesk integration.

**Acceptance Criteria:**
- [ ] Connect/Disconnect button
- [ ] Connection status indicator
- [ ] Sync configuration:
  - Direction (import/export/bidirectional)
  - Auto-sync toggle
  - Sync time selection
- [ ] "Sync Now" button
- [ ] Sync history/logs view
- [ ] Error display

**UI Components:**
- SevDeskSettings
- SyncHistoryTable
- ConnectionStatus

**Dependencies:** Story 6.1

---

### Epic 7: Dashboard & Analytics (Weeks 7-8)
**Goal:** Build insights and reporting

#### Story 7.1: Dashboard Metrics
**Priority:** P0  
**Points:** 5  
**Assignee:** Full-stack Engineer

**Description:**
Create dashboard with key metrics.

**Acceptance Criteria:**
- [ ] Total outstanding amount card
- [ ] Overdue amount card (with count)
- [ ] DSO calculation and display
- [ ] Trend indicators (vs last month)
- [ ] Real-time data (no caching MVP)
- [ ] Responsive layout

**Metrics Calculation:**
- DSO = (Total AR / Total Credit Sales) × Days
- Simplified: Average days from invoice to payment

**UI Components:**
- MetricCard
- DashboardLayout

**Dependencies:** Stories 2.2, 5.1

---

#### Story 7.2: Overdue & Upcoming Lists
**Priority:** P0  
**Points:** 3  
**Assignee:** Frontend Engineer

**Description:**
Display actionable lists of invoices.

**Acceptance Criteria:**
- [ ] Overdue invoices table
  - Sort by days overdue (desc)
  - Columns: Customer, Invoice #, Amount, Due Date, Days Overdue, Actions
- [ ] Upcoming due table (next 7 days)
- [ ] Quick actions: Send Reminder, Mark Paid
- [ ] Click to view invoice detail

**UI Components:**
- InvoiceTable
- ActionButtons

**Dependencies:** Story 7.1

---

#### Story 7.3: Invoice List & Search
**Priority:** P0  
**Points:** 5  
**Assignee:** Frontend Engineer

**Description:**
Build comprehensive invoice list with filtering.

**Acceptance Criteria:**
- [ ] Full invoice list with pagination (50/page)
- [ ] Filters:
  - Status (multi-select)
  - Customer (dropdown)
  - Date range (invoice/due date)
- [ ] Search: invoice number, customer name
- [ ] Sort by any column
- [ ] Export to CSV
- [ ] Bulk actions (mark paid, send reminder)

**UI Components:**
- FilterPanel
- SearchBar
- DataTable
- ExportButton

**Dependencies:** Story 2.2

---

#### Story 7.4: Invoice Detail View
**Priority:** P0  
**Points:** 3  
**Assignee:** Frontend Engineer

**Description:**
Create detailed invoice view with all information.

**Acceptance Criteria:**
- [ ] Invoice header with status badge
- [ ] Customer information section
- [ ] Invoice details (dates, amounts, terms)
- [ ] PDF preview/download
- [ ] Payment history
- [ ] Reminder history
- [ ] Notes section
- [ ] Action buttons

**UI Components:**
- InvoiceDetail
- PDFViewer
- ReminderHistory
- NotesSection

**Dependencies:** Story 2.2

---

### Epic 8: Settings & Configuration (Weeks 8-9)
**Goal:** Complete user-configurable features

#### Story 8.1: Company Settings
**Priority:** P0  
**Points:** 3  
**Assignee:** Full-stack Engineer

**Description:**
Build company configuration pages.

**Acceptance Criteria:**
- [ ] Company name, email
- [ ] Default payment terms
- [ ] Default currency
- [ ] EU Late Payment Regulation toggle
- [ ] Email forwarding address display
- [ ] Settings persistence

**UI Components:**
- CompanySettingsForm

**Dependencies:** Story 2.1

---

#### Story 8.2: SMTP Configuration
**Priority:** P1  
**Points:** 3  
**Assignee:** Full-stack Engineer

**Description:**
Allow custom SMTP for email sending.

**Acceptance Criteria:**
- [ ] SMTP settings form (host, port, user, pass)
- [ ] Test connection button
- [ ] Connection status display
- [ ] Secure credential storage
- [ ] Fallback to system SMTP

**UI Components:**
- SMTPSettingsForm
- ConnectionTester

**Dependencies:** Story 4.3

---

#### Story 8.3: User Preferences
**Priority:** P1  
**Points:** 2  
**Assignee:** Frontend Engineer

**Description:**
User-specific settings.

**Acceptance Criteria:**
- [ ] Timezone selection
- [ ] Email notification preferences:
  - Daily summary
  - Overdue alerts
  - Payment received alerts
- [ ] Password change

**UI Components:**
- UserSettingsForm
- NotificationPreferences

**Dependencies:** Story 1.2

---

### Epic 9: Polish & Launch (Weeks 9-10)
**Goal:** Prepare for production release

#### Story 9.1: Security Implementation
**Priority:** P0  
**Points:** 5  
**Assignee:** Tech Lead

**Description:**
Implement security hardening.

**Acceptance Criteria:**
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection
- [ ] Rate limiting (API)
- [ ] Security headers
- [ ] CORS configuration
- [ ] Penetration testing

**Dependencies:** All previous stories

---

#### Story 9.2: Testing & QA
**Priority:** P0  
**Points:** 8  
**Assignee:** QA Engineer

**Description:**
Comprehensive testing suite.

**Acceptance Criteria:**
- [ ] Unit tests (90%+ coverage for core logic)
- [ ] Integration tests for API endpoints
- [ ] E2E tests for critical user flows
- [ ] OCR accuracy testing
- [ ] Email delivery testing
- [ ] Performance testing
- [ ] Security testing
- [ ] Cross-browser testing

**Test Scenarios:**
- User registration/login
- Invoice CRUD operations
- OCR upload and review
- Reminder sending
- Payment marking
- SevDesk sync

**Dependencies:** All previous stories

---

#### Story 9.3: Documentation
**Priority:** P1  
**Points:** 3  
**Assignee:** Tech Lead

**Description:**
Create technical and user documentation.

**Acceptance Criteria:**
- [ ] API documentation (OpenAPI)
- [ ] User guide (getting started)
- [ ] FAQ document
- [ ] Integration guide (SevDesk)
- [ ] Troubleshooting guide
- [ ] Video tutorials (optional)

**Dependencies:** All previous stories

---

#### Story 9.4: Performance Optimization
**Priority:** P1  
**Points:** 5  
**Assignee:** Backend Engineer

**Description:**
Optimize system performance.

**Acceptance Criteria:**
- [ ] Database query optimization
- [ ] API response time < 200ms (p95)
- [ ] Dashboard load time < 2 seconds
- [ ] File upload optimization
- [ ] Frontend bundle optimization
- [ ] Caching strategy (Redis)
- [ ] Database indexing review

**Dependencies:** All previous stories

---

#### Story 9.5: Production Deployment
**Priority:** P0  
**Points:** 3  
**Assignee:** DevOps Engineer

**Description:**
Prepare production environment.

**Acceptance Criteria:**
- [ ] Production infrastructure setup
- [ ] SSL certificates
- [ ] Domain configuration
- [ ] Database backups (automated)
- [ ] Monitoring and alerting
- [ ] Log aggregation
- [ ] Disaster recovery plan
- [ ] Runbook documentation

**Dependencies:** Story 9.2

---

## 3. Sprint Planning

### Sprint 1: Foundation (Weeks 1-2)
**Goal:** Core infrastructure ready

**Stories:**
- 1.1 Project Setup & Architecture (8 pts)
- 1.2 Authentication & User Management (5 pts)
- 1.3 Database Schema & Migrations (5 pts)
- 1.4 Frontend Foundation (5 pts)

**Total:** 23 points

**Deliverables:**
- [ ] Development environment ready
- [ ] CI/CD pipeline working
- [ ] User can register and login
- [ ] Database schema deployed
- [ ] Frontend app running

---

### Sprint 2: Core Invoice Management (Weeks 2-4)
**Goal:** Basic invoice tracking

**Stories:**
- 2.1 Company & Customer Management (5 pts)
- 2.2 Manual Invoice Creation (5 pts)
- 2.3 File Upload & Storage (5 pts)
- 2.4 Invoice Status Management (3 pts)

**Total:** 18 points

**Deliverables:**
- [ ] User can manage customers
- [ ] User can create invoices
- [ ] File upload working
- [ ] Status transitions automated

---

### Sprint 3: OCR & Intelligence (Weeks 3-5)
**Goal:** AI-powered invoice processing

**Stories:**
- 3.1 OCR Service Integration (8 pts)
- 3.2 OCR Review & Validation UI (5 pts)
- 3.3 AI-Powered Data Validation (5 pts)

**Total:** 18 points

**Deliverables:**
- [ ] OCR extracts invoice data
- [ ] User can review/correct OCR
- [ ] Intelligent validation working

---

### Sprint 4: Reminders (Weeks 4-6)
**Goal:** Automated reminder system

**Stories:**
- 4.1 Reminder Sequence Configuration (3 pts)
- 4.2 Email Template System (5 pts)
- 4.3 SMTP & Email Sending (5 pts)
- 4.4 Automated Reminder Engine (5 pts)

**Total:** 18 points

**Deliverables:**
- [ ] Templates configurable
- [ ] Emails sending via queue
- [ ] Automated reminders working

---

### Sprint 5: Payments & Email (Weeks 5-6)
**Goal:** Payment tracking complete

**Stories:**
- 3.4 Email Invoice Ingestion (5 pts)
- 4.5 Manual Reminder Override (3 pts)
- 5.1 Manual Payment Marking (3 pts)
- 5.2 CSV Payment Import (5 pts)

**Total:** 16 points

**Deliverables:**
- [ ] Email forwarding captures invoices
- [ ] Payment marking working
- [ ] CSV import functional

---

### Sprint 6: SevDesk Integration (Weeks 6-8)
**Goal:** Accounting sync working

**Stories:**
- 6.1 SevDesk OAuth Integration (5 pts)
- 6.2 SevDesk Invoice Sync (8 pts)
- 6.3 Payment Status Sync (5 pts)

**Total:** 18 points

**Deliverables:**
- [ ] SevDesk OAuth working
- [ ] Invoice sync functional
- [ ] Payment sync working

---

### Sprint 7: Dashboard & UI (Weeks 7-8)
**Goal:** Complete user interface

**Stories:**
- 6.4 SevDesk Integration UI (3 pts)
- 7.1 Dashboard Metrics (5 pts)
- 7.2 Overdue & Upcoming Lists (3 pts)
- 7.3 Invoice List & Search (5 pts)
- 7.4 Invoice Detail View (3 pts)

**Total:** 19 points

**Deliverables:**
- [ ] Dashboard with metrics
- [ ] All list views working
- [ ] Invoice detail complete

---

### Sprint 8: Settings (Weeks 8-9)
**Goal:** Configuration complete

**Stories:**
- 8.1 Company Settings (3 pts)
- 8.2 SMTP Configuration (3 pts)
- 8.3 User Preferences (2 pts)

**Total:** 8 points

**Deliverables:**
- [ ] All settings pages working
- [ ] SMTP configurable
- [ ] User preferences saved

---

### Sprint 9: Security & Testing (Weeks 9-10)
**Goal:** Production ready

**Stories:**
- 9.1 Security Implementation (5 pts)
- 9.2 Testing & QA (8 pts)
- 9.3 Documentation (3 pts)

**Total:** 16 points

**Deliverables:**
- [ ] Security audit passed
- [ ] Test coverage > 90%
- [ ] Documentation complete

---

### Sprint 10: Launch (Week 10)
**Goal:** Go live

**Stories:**
- 9.4 Performance Optimization (5 pts)
- 9.5 Production Deployment (3 pts)

**Total:** 8 points

**Deliverables:**
- [ ] Performance optimized
- [ ] Production deployed
- [ ] Monitoring active

---

## 4. Resource Allocation

### Team Structure

| Role | Count | Responsibilities |
|------|-------|------------------|
| Tech Lead | 1 | Architecture, code review, DevOps |
| Senior Backend Engineer | 1 | Core backend, OCR, integrations |
| Backend Engineer | 1 | APIs, background jobs, database |
| Frontend Engineer | 1 | UI/UX, React components |
| Full-stack Engineer | 1 | End-to-end features, QA support |
| QA/DevOps Engineer | 1 | Testing, deployment, monitoring |

### Story Point Distribution

| Epic | Points | Primary Assignee |
|------|--------|------------------|
| 1. Foundation | 23 | Team |
| 2. Invoice Core | 18 | Full-stack + Backend |
| 3. OCR | 23 | Backend + Frontend |
| 4. Reminders | 21 | Full-stack + Backend |
| 5. Payments | 16 | Backend + Full-stack |
| 6. SevDesk | 21 | Backend + Frontend |
| 7. Dashboard | 19 | Frontend + Full-stack |
| 8. Settings | 8 | Full-stack |
| 9. Launch | 32 | Tech Lead + QA |
| **Total** | **181** | |

### Velocity Planning

- **Expected Velocity:** 18-20 points per 2-week sprint
- **Buffer:** 10% for bugs and unexpected issues
- **Total Sprints:** 10 sprints (20 weeks) → Compressed to 10 weeks with parallel work

---

## 5. Dependencies & Risks

### Critical Dependencies

| Dependency | Impact | Mitigation |
|------------|--------|------------|
| OpenAI Vision API availability | High | Implement AWS Textract fallback |
| SevDesk API access | High | Start with manual OAuth, request partnership |
| Email deliverability | High | Use established provider (SendGrid) |
| PostgreSQL performance | Medium | Add indexes, query optimization |
| OCR accuracy | Medium | Allow manual review, train on corrections |

### Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OCR accuracy below 80% | Medium | High | Multiple OCR providers, manual review fallback |
| SevDesk API rate limits | Low | Medium | Implement caching, batch processing |
| Email deliverability issues | Medium | High | Use dedicated IP, warm up gradually |
| Scope creep | High | Medium | Strict MVP definition, change control process |
| Team member availability | Low | High | Cross-training, documentation |
| AI API costs exceed budget | Medium | Medium | Implement caching, usage monitoring, rate limiting |

---

## 6. Definition of Done

### User Story Done Criteria
- [ ] Code implemented and reviewed
- [ ] Unit tests written (90%+ coverage for new code)
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] Product Owner acceptance

### Sprint Done Criteria
- [ ] All stories meet Definition of Done
- [ ] No critical bugs
- [ ] Performance benchmarks met
- [ ] Staging environment stable
- [ ] Sprint demo completed

### Release Done Criteria
- [ ] All P0 stories complete
- [ ] Security audit passed
- [ ] Performance testing passed
- [ ] UAT completed with 5+ users
- [ ] Documentation complete
- [ ] Monitoring and alerting active
- [ ] Rollback plan tested

---

## 7. Communication Plan

### Daily Standups
- **Time:** 9:30 AM CET
- **Duration:** 15 minutes
- **Format:** What did you do? What will you do? Blockers?

### Sprint Planning
- **When:** Every 2 weeks, Monday 10 AM
- **Duration:** 2 hours
- **Attendees:** Full team + Product Owner

### Sprint Review
- **When:** Every 2 weeks, Friday 3 PM
- **Duration:** 1 hour
- **Format:** Demo working features

### Retrospectives
- **When:** Every 2 weeks, Friday 4 PM
- **Duration:** 1 hour
- **Format:** What went well? What didn't? Actions?

### Stakeholder Updates
- **When:** Weekly (Fridays)
- **Format:** Email summary
- **Content:** Sprint progress, blockers, upcoming milestones

---

## 8. Quality Assurance Strategy

### Testing Pyramid

```
    /\
   /  \  E2E Tests (10%) - Critical flows
  /____\
 /      \  Integration Tests (30%) - API, DB
/________\
          \  Unit Tests (60%) - Business logic
```

### Test Coverage Requirements
- Unit tests: 90%+ for core business logic
- Integration tests: All API endpoints
- E2E tests: Critical user flows

### Testing Environments
1. **Local:** Docker compose, developer testing
2. **Staging:** Production-like, feature testing
3. **Production:** Live environment, monitored

### QA Checklist per Story
- [ ] Happy path tested
- [ ] Edge cases tested
- [ ] Error handling verified
- [ ] Cross-browser tested (Chrome, Firefox, Safari)
- [ ] Mobile responsive verified
- [ ] Accessibility checked (WCAG 2.1 AA)

---

## 9. Monitoring & Success Metrics

### Development Metrics
- Velocity (points per sprint)
- Sprint completion rate
- Bug escape rate
- Code coverage
- Deployment frequency

### Product Metrics (MVP)
- Time to first invoice upload
- OCR accuracy rate
- Email delivery rate
- User activation rate
- Feature adoption rates

### Technical Metrics
- API response times (p50, p95, p99)
- Error rates
- Database query performance
- Background job success rate
- Infrastructure costs

### Alerting Thresholds
- API error rate > 1%
- Response time p95 > 500ms
- Background job failure > 5%
- Database connection pool > 80%

---

## 10. Post-Launch Plan

### Week 1: Hypercare
- Daily standups
- Monitor error rates closely
- Rapid bug fixes
- User feedback collection

### Week 2-4: Stabilization
- Bi-weekly releases for bug fixes
- Performance monitoring
- User onboarding improvements
- Documentation updates

### Month 2: Iteration
- Gather user feedback
- Prioritize V1 features
- Plan next development cycle
- Scale infrastructure if needed

---

## Appendix A: Story Point Reference

| Complexity | Points | Description |
|------------|--------|-------------|
| Simple | 2 | Simple UI change, config update |
| Small | 3 | Single API endpoint, simple form |
| Medium | 5 | Feature with backend + frontend |
| Large | 8 | Complex feature, integration |
| Epic | 13 | Multi-component feature |

---

## Appendix B: Technical Stack Decisions

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Backend | Rust (Axum) | Performance, type safety, team expertise |
| Database | PostgreSQL | Relational data, ACID compliance |
| Cache/Queue | Redis | Fast, proven, job queue support |
| Frontend | React + TypeScript | Ecosystem, type safety |
| Styling | TailwindCSS | Utility-first, rapid development |
| UI Components | shadcn/ui | Modern, accessible, customizable |
| State | TanStack Query | Server state management |
| Forms | React Hook Form | Performance, validation |
| OCR | OpenAI Vision | Accuracy, structured output |
| Email | SendGrid | Deliverability, tracking |
| Storage | AWS S3 | Scalable, reliable |
| Hosting | Fly.io | Simple, cost-effective |
| Monitoring | Sentry | Error tracking, performance |

---

**Document Owner:** Product Team  
**Next Review:** Weekly during sprints  
**Approval:** Tech Lead, Engineering Manager, Product Manager
