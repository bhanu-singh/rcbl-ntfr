# Product Functional Specification (PFS)
## Receivable Notification System - MVP

**Document Version:** 1.1  
**Last Updated:** January 25, 2026  
**Product Stage:** MVP (Minimum Viable Product)  
**Target Timeline:** 6-10 weeks

---

## 1. Executive Summary

### 1.1 Product Vision
Build a lightweight, automated accounts receivable management system that helps European SMEs reduce Days Sales Outstanding (DSO) by 10-30% through intelligent invoice tracking and automated payment reminders.

### 1.2 MVP Success Criteria
- **User can see value on Day 1** - immediate visibility into overdue invoices
- **Reduces manual work** - eliminates need for manual invoice tracking spreadsheets
- **Drives payment action** - automated reminders result in faster payments
- **Revenue-ready** - product is sellable and customers will pay for it

### 1.3 Out of Scope for MVP
- Open Banking integration (V1)
- Multi-currency support (V2)
- Additional ERP integrations beyond SevDesk (V2)
- SMS/WhatsApp reminders (V2)
- Multi-language support (V2)
- Role-based access control (V2)

---

## 2. User Personas & Use Cases

### 2.1 Primary Persona: "Sarah - Small Agency Owner"
- **Role:** Founder/Finance Manager at 10-person consulting agency
- **Pain:** Spends 5+ hours/week chasing late invoices via email
- **Goal:** Get paid on time without manual follow-up
- **Tech Savvy:** Moderate - uses Gmail, SevDesk, basic tools
- **Budget:** €50-100/month for tools that save time

### 2.2 Secondary Persona: "Marcus - Freelance Consultant"
- **Role:** Solo B2B consultant
- **Pain:** Loses track of which invoices are overdue
- **Goal:** Professional automated reminders without seeming pushy
- **Tech Savvy:** High
- **Budget:** €20-50/month

### 2.3 Core User Journey (MVP)
1. User uploads/emails invoices to system
2. System automatically extracts invoice data using OCR (or user reviews/corrects)
3. System calculates due dates based on payment terms
4. System automatically detects overdue invoices
5. System sends automated reminder emails at configured intervals
6. User marks invoices as paid when payment received (or syncs from SevDesk)
7. User views dashboard showing outstanding amounts and DSO
8. User can sync invoices bidirectionally with SevDesk accounting software

---

## 3. Functional Requirements

### 3.1 Invoice Ingestion

#### 3.1.1 Manual Upload (Priority: P0)
**User Story:** As a user, I want to upload invoice PDFs/CSVs so the system can track them.

**Acceptance Criteria:**
- User can drag-and-drop or click to upload files
- Supported formats: PDF, CSV
- File size limit: 10MB per file
- Batch upload: up to 10 files at once
- After upload, user manually enters:
  - Customer name (dropdown if exists, or create new)
  - Invoice number
  - Invoice amount
  - Currency (default: EUR)
  - Invoice date
  - Payment terms (Net 15/30/60 or custom days)
- System stores original file in object storage
- System generates unique invoice ID
- System calculates due date automatically

**Edge Cases:**
- Duplicate invoice number → show warning, allow override
- Invalid file format → show clear error message
- Upload failure → show retry option with progress indicator

**UI Requirements:**
- Clean upload area with visual feedback
- Form validation with inline error messages
- Preview of uploaded file name and size
- Auto-save draft as user types

#### 3.1.2 Email Forwarding (Priority: P0)
**User Story:** As a user, I want to forward invoices to a dedicated email address so they're automatically added to the system.

**Acceptance Criteria:**
- Each company gets unique email: `{company-slug}@invoices.{domain}`
- System receives email via SMTP/IMAP
- System extracts:
  - Sender email (map to customer if exists)
  - Subject line
  - PDF attachments
  - Email body text
- System creates draft invoice requiring user review
- User receives notification: "New invoice received - please review"
- User completes missing fields in web UI
- System confirms invoice is tracked

**Edge Cases:**
- Multiple attachments → create separate draft for each PDF
- No attachment → save email body as note, flag for review
- Unknown sender → create new customer draft
- Spam/invalid emails → ignore based on simple rules

**Technical Notes:**
- Use dedicated email service (AWS SES, SendGrid, Postmark)
- Store raw email for audit trail
- Implement basic spam filtering

#### 3.1.3 OCR Invoice Parsing (Priority: P0)
**User Story:** As a user, I want the system to automatically extract invoice data from PDFs so I don't have to manually enter everything.

**Acceptance Criteria:**
- When user uploads PDF invoice, system automatically processes it with OCR
- OCR extracts the following fields:
  - Invoice number
  - Invoice date
  - Due date (if present)
  - Customer name
  - Customer address
  - Customer email (if present)
  - Total amount
  - Currency
  - Payment terms (Net 15/30/60, etc.)
  - Line items (optional, for future use)
  - IBAN/bank details (if present)
- After OCR processing, user sees pre-filled form with extracted data
- User can review, edit, and confirm extracted data
- Confidence score shown for each extracted field (high/medium/low)
- Fields with low confidence highlighted for user review
- User can manually correct any field before saving
- If OCR fails or confidence is too low, fall back to manual entry

**OCR Processing Flow:**
1. User uploads PDF
2. System queues PDF for OCR processing
3. Background job processes PDF (async, shows loading state)
4. OCR service extracts data
5. System attempts to match customer by name/email
6. User sees review screen with extracted data
7. User confirms or edits fields
8. Invoice saved with OCR metadata

**Edge Cases:**
- Poor quality PDF/image → Show warning, allow manual entry
- Multi-page invoice → Process all pages, extract from first page primarily
- Non-English invoice → Attempt extraction, may have lower accuracy
- Scanned image (not PDF) → Convert to PDF first, then process
- OCR timeout (> 30 seconds) → Show error, allow manual entry
- Partial extraction → Pre-fill available fields, mark others as required

**Technical Requirements:**
- OCR service options:
  - Primary: OpenAI Vision API (GPT-4 Vision) for structured extraction
  - Fallback: AWS Textract or Google Cloud Vision API
  - Alternative: PaddleOCR (open source, self-hosted)
- Processing time target: < 10 seconds for typical invoice
- Support formats: PDF, PNG, JPG, JPEG
- File size limit: 10MB
- Store OCR results with confidence scores
- Cache OCR results for duplicate files (hash-based)

**UI Requirements:**
- Progress indicator during OCR processing
- Review screen with side-by-side PDF preview and extracted fields
- Visual indicators for confidence levels:
  - Green checkmark: High confidence (auto-filled)
  - Yellow warning: Medium confidence (review recommended)
  - Red alert: Low confidence (manual entry required)
- "Accept All" button for high-confidence extractions
- "Edit Field" inline editing
- "Re-run OCR" button if extraction seems wrong

**Data Quality:**
- Validate extracted amounts (numeric, positive)
- Validate dates (not in future, reasonable range)
- Validate email format if extracted
- Sanitize extracted text (remove special characters, trim whitespace)

#### 3.1.4 Manual Entry (Priority: P1)
**User Story:** As a user, I want to manually create an invoice record without uploading a file.

**Acceptance Criteria:**
- "Create Invoice" button in dashboard
- Same form fields as upload flow
- Optional file attachment (can trigger OCR if PDF)
- Save and immediately start tracking

---

### 3.2 Due Date Engine

#### 3.2.1 Due Date Calculation (Priority: P0)
**User Story:** As a user, I want the system to automatically calculate when invoices are due based on payment terms.

**Acceptance Criteria:**
- Formula: `due_date = invoice_date + payment_term_days`
- Supported payment terms:
  - Net 15 (15 days)
  - Net 30 (30 days)
  - Net 60 (60 days)
  - Net 90 (90 days)
  - Custom (user enters number of days)
- Display due date prominently on invoice detail
- Allow manual override of calculated due date
- Log when due date is manually changed

**Business Rules:**
- Due date calculation happens immediately on invoice creation
- If invoice date is in future, due date calculates from future date
- Weekend/holiday handling: NOT in MVP (V1 feature)

#### 3.2.2 EU Late Payment Regulation Flag (Priority: P1)
**User Story:** As a user in EU, I want to apply the 30-day maximum payment term regulation.

**Acceptance Criteria:**
- Company settings: toggle "Apply EU Late Payment Regulation"
- When enabled: cap payment terms at 30 days maximum
- Show warning if user tries to set terms > 30 days
- Allow override with confirmation: "This exceeds EU regulation limits"

**Technical Notes:**
- This is a soft enforcement (warning only)
- Future: add interest calculation for late payments per regulation

---

### 3.3 Invoice Status & Overdue Detection

#### 3.3.1 Status State Machine (Priority: P0)
**User Story:** As a user, I want to see the current status of each invoice at a glance.

**Status Definitions:**
- **Pending** - Due date is > 7 days away
- **Due Soon** - Due date is within 7 days
- **Overdue** - Past due date and not paid
- **Paid** - Payment received and matched

**Status Transitions:**
```
Pending → Due Soon (7 days before due date)
Due Soon → Overdue (on due date if not paid)
Any status → Paid (when user marks as paid)
```

**Acceptance Criteria:**
- Status updates automatically via scheduled job (runs every 6 hours)
- Status badge shown on invoice list and detail pages
- Color coding:
  - Pending: Gray
  - Due Soon: Yellow/Orange
  - Overdue: Red
  - Paid: Green
- Filter invoices by status
- Status change triggers reminder sequence evaluation

#### 3.3.2 Overdue Detection Job (Priority: P0)
**Technical Specification:**
- Background job runs every 6 hours
- Query: `SELECT * FROM invoices WHERE due_date < NOW() AND status != 'Paid'`
- Update status to 'Overdue'
- Trigger reminder sequence check
- Log status change with timestamp

---

### 3.4 Automated Reminder System

#### 3.4.1 Reminder Sequence Configuration (Priority: P0)
**User Story:** As a user, I want to configure when and how reminders are sent to customers.

**Default Reminder Sequence:**
1. **Day -5** (5 days before due): "Friendly reminder - invoice due soon"
2. **Day 0** (due date): "Invoice due today"
3. **Day +7** (7 days overdue): "Friendly overdue reminder"
4. **Day +21** (21 days overdue): "Firm overdue reminder"

**Acceptance Criteria:**
- Company-level default sequence
- User can enable/disable each reminder step
- User can adjust day offsets (e.g., change +7 to +5)
- User can select template for each step
- Changes apply to new invoices only (not retroactive)

**UI Requirements:**
- Visual timeline showing reminder schedule
- Toggle switches for each step
- Template preview

#### 3.4.2 Email Templates (Priority: P0)
**User Story:** As a user, I want professional, customizable email templates for reminders.

**Template Types:**
1. **Friendly Reminder** (for due soon and early overdue)
2. **Firm Reminder** (for significantly overdue)

**Template Variables:**
- `{customer_name}`
- `{invoice_number}`
- `{invoice_amount}`
- `{invoice_date}`
- `{due_date}`
- `{days_overdue}` (if applicable)
- `{company_name}`
- `{payment_link}` (if configured)

**Acceptance Criteria:**
- 2 default templates provided (friendly, firm)
- User can edit template text
- User can preview with sample data
- Templates stored per company
- Support basic HTML formatting (bold, italic, links)
- Subject line is customizable

**Default Template Example (Friendly):**
```
Subject: Friendly Reminder - Invoice {invoice_number} Due Soon

Hi {customer_name},

This is a friendly reminder that invoice {invoice_number} for {invoice_amount} is due on {due_date}.

Invoice Details:
- Invoice Number: {invoice_number}
- Amount: {invoice_amount}
- Due Date: {due_date}

If you've already sent payment, please disregard this reminder.

Thank you for your business!

Best regards,
{company_name}
```

#### 3.4.3 Email Sending (Priority: P0)
**User Story:** As a user, I want reminders sent automatically via email without manual intervention.

**Acceptance Criteria:**
- Background job runs every 4 hours
- Query invoices needing reminders based on sequence rules
- Send email via SMTP
- Attach invoice PDF (if available)
- Log each reminder sent:
  - Timestamp
  - Recipient
  - Template used
  - Delivery status
- Update invoice: `last_reminder_date`, `next_action_date`
- Handle email failures gracefully:
  - Retry 3 times with exponential backoff
  - Mark as failed after 3 attempts
  - Notify user of failed sends

**Technical Requirements:**
- Use transactional email service (AWS SES, SendGrid, Postmark)
- Rate limiting: max 100 emails/hour (MVP)
- From address: `{company-slug}@{domain}` or user's configured email
- Reply-to: user's email address
- Track open rates (optional pixel tracking)

#### 3.4.4 Manual Reminder Override (Priority: P1)
**User Story:** As a user, I want to manually send a reminder outside the automated sequence.

**Acceptance Criteria:**
- "Send Reminder Now" button on invoice detail page
- User selects template
- User can edit email before sending
- Email sends immediately
- Logged as manual reminder (doesn't affect sequence)

---

### 3.5 Payment Tracking

#### 3.5.1 Manual Payment Marking (Priority: P0)
**User Story:** As a user, I want to mark invoices as paid when I receive payment.

**Acceptance Criteria:**
- "Mark as Paid" button on invoice detail and list view
- Modal prompts for:
  - Payment date (default: today)
  - Payment amount (default: full invoice amount)
  - Payment method (dropdown: Bank Transfer, Check, Cash, Other)
  - Optional notes
- On confirm:
  - Create payment record
  - Update invoice status to "Paid"
  - Stop all future reminders for this invoice
  - Update dashboard totals
- Show confirmation message
- Allow undo within 5 seconds

**Edge Cases:**
- Partial payment → keep status as current, log partial payment, reduce outstanding amount
- Overpayment → show warning, allow user to confirm
- Payment date before invoice date → show warning

#### 3.5.2 CSV Payment Import (Priority: P1)
**User Story:** As a user, I want to import bank statement CSV to automatically match payments.

**Acceptance Criteria:**
- "Import Payments" button in dashboard
- Upload CSV file
- Map columns:
  - Date
  - Amount
  - Reference/Description
  - (Optional) Customer name
- System attempts auto-match based on:
  - Exact amount match
  - Invoice number in reference
  - Customer name match
- Show matching results:
  - Confirmed matches (green)
  - Suggested matches (yellow) - require user confirmation
  - Unmatched (gray) - user can manually match or skip
- User reviews and confirms matches
- Bulk mark as paid

**CSV Format Support:**
- Common formats: SevDesk, Xero, generic bank exports
- Flexible column mapping
- Date format detection (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD)

**Technical Notes:**
- Store original CSV for audit
- Log all matches with confidence score
- Allow re-processing of CSV if initial match was wrong

---

### 3.6 Customer Management

#### 3.6.1 Customer Records (Priority: P0)
**User Story:** As a user, I want to maintain a list of customers with their payment terms.

**Customer Fields:**
- Name (required)
- Email (required)
- Contact person name (optional)
- Default payment terms (Net 30, etc.)
- Notes (optional)
- Created date

**Acceptance Criteria:**
- "Customers" page with list view
- Add/Edit/Delete customer
- Search customers by name or email
- When creating invoice, select from customer dropdown
- Customer detail page shows:
  - All invoices for this customer
  - Total outstanding
  - Average days to payment
  - Payment history

#### 3.6.2 Customer Payment Terms (Priority: P0)
**User Story:** As a user, I want to set default payment terms per customer so I don't have to enter them for each invoice.

**Acceptance Criteria:**
- Customer profile has "Default Payment Terms" field
- When creating invoice for customer, auto-populate payment terms
- User can override on per-invoice basis
- Changing customer default doesn't affect existing invoices

---

### 3.7 Dashboard & Reporting

#### 3.7.1 Main Dashboard (Priority: P0)
**User Story:** As a user, I want a single screen showing my accounts receivable health.

**Dashboard Widgets:**

1. **Total Outstanding** (large card)
   - Sum of all unpaid invoices
   - Currency symbol
   - Trend indicator (vs last month)

2. **Overdue Amount** (large card)
   - Sum of overdue invoices
   - Red highlight
   - Count of overdue invoices

3. **DSO (Days Sales Outstanding)** (medium card)
   - Formula: `(Total AR / Total Credit Sales) × Number of Days`
   - Simplified MVP: Average days from invoice date to payment date for last 90 days
   - Industry benchmark comparison (optional)

4. **Overdue Invoice List** (table)
   - Columns: Customer, Invoice #, Amount, Due Date, Days Overdue, Status, Actions
   - Sort by days overdue (descending)
   - Click row to view detail
   - Quick action: Send Reminder, Mark Paid

5. **Upcoming Due** (table)
   - Invoices due in next 7 days
   - Same columns as overdue list

**Acceptance Criteria:**
- Dashboard loads in < 2 seconds
- Real-time data (no caching for MVP)
- Responsive design (works on tablet)
- Export overdue list to CSV

#### 3.7.2 Invoice List View (Priority: P0)
**User Story:** As a user, I want to see all invoices with filtering and search.

**Acceptance Criteria:**
- Table with columns: Status, Customer, Invoice #, Amount, Invoice Date, Due Date, Days Overdue, Actions
- Filters:
  - Status (multi-select)
  - Customer (dropdown)
  - Date range (invoice date or due date)
- Search: invoice number, customer name
- Sort by any column
- Pagination: 50 per page
- Bulk actions:
  - Mark as Paid
  - Send Reminder
  - Export to CSV

#### 3.7.3 Invoice Detail View (Priority: P0)
**User Story:** As a user, I want to see complete information about a single invoice.

**Acceptance Criteria:**
- Invoice header: Status badge, Invoice #, Amount
- Customer information section
- Dates: Invoice Date, Due Date, Days Overdue
- Payment terms
- Attached file (view/download PDF)
- Payment history (if any)
- Reminder history:
  - Date sent
  - Template used
  - Delivery status
  - (Optional) Open/click tracking
- Notes section (user can add notes)
- Action buttons:
  - Mark as Paid
  - Send Reminder
  - Edit Invoice
  - Delete Invoice

---

### 3.8 User & Company Settings

#### 3.8.1 Company Settings (Priority: P0)
**User Story:** As a user, I want to configure company-level settings.

**Settings:**
- Company name
- Company email (for reminders)
- Email forwarding address (read-only, generated)
- Default payment terms
- Default currency
- EU Late Payment Regulation toggle
- Reminder sequence configuration
- Email templates

**Acceptance Criteria:**
- Settings page with tabs/sections
- Save button with confirmation
- Changes take effect immediately for new invoices

#### 3.8.2 User Account (Priority: P0)
**User Story:** As a user, I want to manage my account.

**Settings:**
- Name
- Email
- Password change
- Timezone
- Email notification preferences:
  - Daily summary of overdue invoices
  - Alert when invoice becomes overdue
  - Alert when payment received

#### 3.8.3 SMTP Configuration (Priority: P0)
**User Story:** As a user, I want to send reminders from my own email address.

**Options:**
1. **Use system email** (default, easiest)
   - From: `{company-slug}@{domain}`
   - Reply-to: user's email
   
2. **Custom SMTP** (advanced)
   - User provides:
     - SMTP host
     - Port
     - Username
     - Password
     - From address
   - Test connection button
   - Fallback to system email if custom fails

**Acceptance Criteria:**
- Settings page with SMTP configuration
- Test email button sends test to user's email
- Show connection status (connected/failed)
- Secure storage of SMTP credentials (encrypted)

#### 3.8.4 SevDesk Integration (Priority: P0)
**User Story:** As a user, I want to sync invoices and payments with my SevDesk accounting software so I don't have to manage data in two places.

**Acceptance Criteria:**
- User can connect SevDesk account via OAuth
- User authorizes access to SevDesk API
- System stores SevDesk API credentials securely (encrypted)
- Connection status shown in settings (connected/disconnected)
- User can disconnect SevDesk integration at any time

**Sync Capabilities:**

1. **Import Invoices from SevDesk** (Bidirectional)
   - User can trigger manual sync: "Import from SevDesk"
   - System fetches invoices from SevDesk API
   - For each SevDesk invoice:
     - Check if invoice already exists (by invoice number)
     - If new: Create invoice in system
     - If exists: Update invoice if data differs
   - Map SevDesk fields to system fields:
     - `invoiceNumber` → invoice_number
     - `invoiceDate` → invoice_date
     - `dueDate` → due_date
     - `totalGross` → amount
     - `currency` → currency
     - `contact.name` → customer name
     - `contact.email` → customer email
     - `status` → map to system status (open → pending, paid → paid)
   - Sync frequency: Manual trigger + optional daily auto-sync

2. **Export Invoices to SevDesk** (Bidirectional)
   - When invoice created/updated in system, user can choose to sync to SevDesk
   - Create invoice in SevDesk if doesn't exist
   - Update invoice in SevDesk if already exists
   - Map system fields to SevDesk API format
   - Handle conflicts: Last write wins (or user preference)

3. **Payment Status Sync**
   - When payment marked as paid in SevDesk, sync to system
   - When payment marked as paid in system, sync to SevDesk (if enabled)
   - Match payments by invoice number and amount
   - Update invoice status automatically

4. **Customer Sync**
   - Import customers from SevDesk (contacts)
   - Create customer in system if doesn't exist
   - Link existing customers by name/email match
   - Sync customer payment terms if available

**Sync Configuration:**
- **Sync Direction:**
  - One-way: SevDesk → System (import only)
  - One-way: System → SevDesk (export only)
  - Two-way: Bidirectional sync (default)
- **Auto-sync:**
  - Enable/disable automatic daily sync
  - Set sync time (default: 2 AM user timezone)
  - Sync frequency: Daily, Weekly, Manual only
- **Conflict Resolution:**
  - Last write wins
  - Always prefer SevDesk
  - Always prefer System
  - Prompt user for conflicts

**SevDesk API Integration:**
- **Authentication:**
  - OAuth 2.0 flow
  - Store access token and refresh token securely
  - Auto-refresh expired tokens
  - Handle token revocation gracefully
- **API Endpoints Used:**
  - `GET /Invoice` - List invoices
  - `GET /Invoice/{id}` - Get invoice detail
  - `POST /Invoice` - Create invoice
  - `PUT /Invoice/{id}` - Update invoice
  - `GET /Contact` - List contacts (customers)
  - `GET /Voucher` - List payments/vouchers
  - Rate limiting: Respect SevDesk API limits (typically 100 requests/minute)

**Error Handling:**
- **API Errors:**
  - Invalid credentials → Show error, prompt to reconnect
  - Rate limit exceeded → Queue requests, retry with backoff
  - Network error → Retry 3 times, then notify user
  - API changes → Log error, notify admin, show user-friendly message
- **Data Conflicts:**
  - Invoice exists in both systems with different data → Show conflict resolution UI
  - Customer name mismatch → Create new customer or link manually
  - Payment amount mismatch → Flag for manual review

**UI Requirements:**
- **Settings Page:**
  - "Connect SevDesk" button (if not connected)
  - Connection status indicator
  - Last sync timestamp
  - "Sync Now" button (manual trigger)
  - Sync configuration options
  - "Disconnect" button
- **Sync Status Page:**
  - Show sync history/logs
  - List of synced invoices
  - Errors/warnings from last sync
  - "Retry Failed Syncs" button
- **Invoice Detail Page:**
  - Show SevDesk link if synced
  - "Sync to SevDesk" button (if not synced)
  - Sync status badge (synced/pending/error)

**Data Mapping:**

**SevDesk → System:**
```
SevDesk Invoice Status → System Status:
- 100 (Draft) → pending
- 200 (Sent) → pending
- 1000 (Paid) → paid
- 1001 (Overdue) → overdue
```

**System → SevDesk:**
```
System Status → SevDesk Invoice Status:
- pending → 200 (Sent)
- due_soon → 200 (Sent)
- overdue → 1001 (Overdue)
- paid → 1000 (Paid)
```

**Technical Notes:**
- Use SevDesk REST API v2
- Implement webhook support (future enhancement) for real-time sync
- Store sync metadata:
  - Last sync timestamp
  - Sync direction
  - Number of records synced
  - Errors encountered
- Implement idempotency: Use invoice number as unique identifier
- Batch operations: Sync up to 100 invoices per API call
- Background job for auto-sync: Runs daily at configured time

**Privacy & Security:**
- Encrypt stored API credentials
- Never log sensitive customer data
- Comply with GDPR for data sync
- User consent required before syncing data
- Allow user to revoke access at any time

---

## 4. Non-Functional Requirements

### 4.1 Performance
- Dashboard loads in < 2 seconds
- Invoice list with 1000 records loads in < 3 seconds
- File upload processes in < 5 seconds for 5MB file
- OCR processing completes in < 10 seconds for typical invoice
- SevDesk sync completes in < 30 seconds for 100 invoices
- Background jobs process within 5 minutes of scheduled time

### 4.2 Scalability (MVP Targets)
- Support up to 100 companies
- Up to 10,000 invoices per company
- Up to 1,000 customers per company
- Send up to 10,000 emails per day
- Process up to 1,000 OCR requests per day
- Handle up to 100 SevDesk sync operations per day

### 4.3 Security
- HTTPS only
- Password hashing (bcrypt)
- SQL injection prevention (parameterized queries)
- XSS prevention (input sanitization)
- CSRF protection
- File upload validation (type, size, malware scan)
- Secure SMTP credential storage (encryption at rest)
- Secure API token storage for accounting integrations (encryption at rest)
- OAuth 2.0 for third-party integrations
- Rate limiting on API endpoints

### 4.4 Data Privacy (GDPR Compliance)
- User can export all their data (JSON/CSV)
- User can delete their account and all data
- Data retention policy: 7 years for invoices (accounting requirement)
- Privacy policy and terms of service
- Cookie consent (if using analytics)

### 4.5 Reliability
- 99% uptime target
- Automated database backups (daily)
- Email sending retry logic (3 attempts)
- Graceful error handling with user-friendly messages
- System health monitoring

### 4.6 Usability
- Intuitive UI requiring no training
- Responsive design (desktop, tablet)
- Mobile-friendly (view-only for MVP)
- Consistent design language
- Loading states for all async operations
- Clear error messages with actionable guidance

### 4.7 Browser Support
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

---

## 5. Data Model

### 5.1 Core Entities

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
ocr_processed: Boolean (default false)
ocr_confidence_score: Decimal(3,2) (nullable, 0.00-1.00)
ocr_extracted_data: JSONB (nullable, stores raw OCR results)
sevdesk_invoice_id: String (nullable, external ID)
sevdesk_synced_at: Timestamp (nullable)
sevdesk_sync_status: Enum (not_synced, synced, sync_failed) (default 'not_synced')
created_at: Timestamp
updated_at: Timestamp

Index: company_id, customer_id, status, due_date, sevdesk_invoice_id
```

#### Payment
```
id: UUID (PK)
invoice_id: UUID (FK)
amount: Decimal(10,2)
payment_date: Date
payment_method: Enum (bank_transfer, check, cash, other)
source: Enum (manual, csv_import)
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

#### AccountingIntegration
```
id: UUID (PK)
company_id: UUID (FK)
provider: Enum (sevdesk, SevDesk, xero, lexoffice)
access_token: String (encrypted)
refresh_token: String (encrypted, nullable)
token_expires_at: Timestamp (nullable)
sync_direction: Enum (import, export, bidirectional)
auto_sync_enabled: Boolean (default false)
auto_sync_time: Time (nullable, default 02:00)
last_sync_at: Timestamp (nullable)
last_sync_status: Enum (success, failed, partial)
last_sync_error: Text (nullable)
sync_config: JSONB (nullable, provider-specific config)
created_at: Timestamp
updated_at: Timestamp

Index: company_id, provider
```

#### SyncLog
```
id: UUID (PK)
integration_id: UUID (FK)
sync_type: Enum (manual, automatic)
direction: Enum (import, export, bidirectional)
records_synced: Integer
records_failed: Integer
status: Enum (success, failed, partial)
error_message: Text (nullable)
started_at: Timestamp
completed_at: Timestamp (nullable)
created_at: Timestamp

Index: integration_id, started_at
```

### 5.2 Relationships
- Company → Users (1:N)
- Company → Customers (1:N)
- Company → Invoices (1:N)
- Company → ReminderSequence (1:1)
- Company → EmailTemplates (1:N)
- Company → AccountingIntegrations (1:N)
- Customer → Invoices (1:N)
- Invoice → Payments (1:N)
- Invoice → ReminderEvents (1:N)
- AccountingIntegration → SyncLogs (1:N)

---

## 6. API Endpoints (Internal Reference)

### 6.1 Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/forgot-password` - Password reset

### 6.2 Invoices
- `GET /api/invoices` - List invoices (with filters)
- `GET /api/invoices/:id` - Get invoice detail
- `POST /api/invoices` - Create invoice
- `PUT /api/invoices/:id` - Update invoice
- `DELETE /api/invoices/:id` - Delete invoice
- `POST /api/invoices/:id/mark-paid` - Mark as paid
- `POST /api/invoices/:id/send-reminder` - Send manual reminder
- `POST /api/invoices/upload` - Upload invoice file (triggers OCR)
- `POST /api/invoices/:id/process-ocr` - Re-process OCR for invoice
- `GET /api/invoices/:id/ocr-results` - Get OCR extraction results
- `POST /api/invoices/import-payments` - Import payment CSV

### 6.3 Customers
- `GET /api/customers` - List customers
- `GET /api/customers/:id` - Get customer detail
- `POST /api/customers` - Create customer
- `PUT /api/customers/:id` - Update customer
- `DELETE /api/customers/:id` - Delete customer

### 6.4 Dashboard
- `GET /api/dashboard/stats` - Get dashboard metrics
- `GET /api/dashboard/overdue` - Get overdue invoices
- `GET /api/dashboard/upcoming` - Get upcoming due invoices

### 6.5 Settings
- `GET /api/settings/company` - Get company settings
- `PUT /api/settings/company` - Update company settings
- `GET /api/settings/reminder-sequence` - Get reminder sequence
- `PUT /api/settings/reminder-sequence` - Update reminder sequence
- `GET /api/settings/templates` - Get email templates
- `PUT /api/settings/templates/:type` - Update template

### 6.6 Accounting Integrations
- `GET /api/integrations` - List connected integrations
- `GET /api/integrations/:provider` - Get integration details (e.g., sevdesk)
- `POST /api/integrations/sevdesk/connect` - Initiate SevDesk OAuth flow
- `GET /api/integrations/sevdesk/callback` - OAuth callback handler
- `POST /api/integrations/sevdesk/disconnect` - Disconnect SevDesk
- `POST /api/integrations/sevdesk/sync` - Trigger manual sync
- `GET /api/integrations/sevdesk/sync-logs` - Get sync history
- `PUT /api/integrations/sevdesk/config` - Update sync configuration

### 6.7 Email Ingestion (Internal)
- `POST /api/internal/email-webhook` - Receive forwarded emails

---

## 7. Background Jobs

### 7.1 Status Update Job
- **Frequency:** Every 6 hours
- **Purpose:** Update invoice statuses based on due dates
- **Logic:**
  - Find invoices where `due_date - 7 days <= NOW()` and status = 'pending' → set to 'due_soon'
  - Find invoices where `due_date <= NOW()` and status != 'paid' → set to 'overdue'

### 7.2 Reminder Sending Job
- **Frequency:** Every 4 hours
- **Purpose:** Send scheduled reminders
- **Logic:**
  - Find invoices where `next_action_date <= NOW()` and status != 'paid'
  - Get company's reminder sequence
  - Determine which step to send based on `reminder_sequence_step`
  - Send email
  - Log reminder event
  - Update `last_reminder_date`, `next_action_date`, `reminder_sequence_step`

### 7.3 Daily Summary Email Job
- **Frequency:** Daily at 8 AM (user timezone)
- **Purpose:** Send daily summary to users who opted in
- **Content:**
  - Total outstanding
  - New overdue invoices since yesterday
  - Payments received yesterday
  - Action items

### 7.4 OCR Processing Job
- **Frequency:** On-demand (triggered by file upload)
- **Purpose:** Process uploaded PDFs with OCR
- **Logic:**
  - Queue PDF for OCR processing
  - Call OCR service (OpenAI Vision, AWS Textract, etc.)
  - Extract invoice fields
  - Calculate confidence scores
  - Store results in `ocr_extracted_data` field
  - Update `ocr_processed` flag
  - Notify user if processing complete

### 7.5 SevDesk Sync Job
- **Frequency:** Daily at configured time (default 2 AM) or manual trigger
- **Purpose:** Sync invoices and payments with SevDesk
- **Logic:**
  - Get all companies with SevDesk integration enabled
  - For each company:
    - Check if auto-sync enabled
    - Fetch invoices from SevDesk API
    - Compare with local invoices
    - Create/update invoices based on sync direction
    - Sync payment status
    - Log sync results
    - Update `last_sync_at` timestamp
- **Error Handling:**
  - Retry failed API calls (3 attempts)
  - Log errors to SyncLog
  - Notify user of sync failures

---

## 8. User Flows

### 8.1 First-Time User Onboarding
1. User signs up (email + password)
2. User enters company name
3. System generates email forwarding address
4. User sees welcome screen with 3 options:
   - Upload first invoice
   - Forward invoice to email
   - Watch 2-min tutorial video
5. User uploads invoice
6. User fills in invoice details
7. System calculates due date
8. User sees dashboard with first invoice
9. Onboarding complete

### 8.2 Daily Usage Flow
1. User logs in
2. Views dashboard
3. Sees 3 overdue invoices
4. Clicks on most overdue invoice
5. Reviews reminder history (last sent 7 days ago)
6. Clicks "Send Reminder Now"
7. Selects "Firm" template
8. Reviews email preview
9. Clicks "Send"
10. Confirmation shown
11. Returns to dashboard

### 8.3 Payment Received Flow
1. User receives bank notification of payment
2. User logs into system
3. Searches for invoice by amount or customer
4. Clicks "Mark as Paid"
5. Confirms payment date and amount
6. Invoice status changes to "Paid"
7. Invoice removed from overdue list
8. Dashboard totals update

---

## 9. UI/UX Guidelines

### 9.1 Design Principles
- **Clarity over cleverness** - Clear labels, obvious actions
- **Progressive disclosure** - Show essential info first, details on demand
- **Immediate feedback** - Loading states, success/error messages
- **Forgiving** - Easy undo, confirmation for destructive actions
- **Consistent** - Same patterns throughout app

### 9.2 Key UI Patterns
- **Status badges** - Color-coded, consistent placement
- **Action buttons** - Primary (blue), Secondary (gray), Destructive (red)
- **Tables** - Sortable headers, hover states, row actions
- **Forms** - Inline validation, clear error messages, logical tab order
- **Modals** - For focused tasks (mark paid, send reminder)
- **Empty states** - Helpful guidance when no data

### 9.3 Color Palette
- **Primary:** Blue (#2563EB) - Actions, links
- **Success:** Green (#10B981) - Paid status, confirmations
- **Warning:** Orange (#F59E0B) - Due soon status
- **Danger:** Red (#EF4444) - Overdue status, errors
- **Neutral:** Gray (#6B7280) - Pending status, secondary text

### 9.4 Typography
- **Headings:** Inter or similar sans-serif, bold
- **Body:** Inter or similar, regular
- **Monospace:** For invoice numbers, amounts

---

## 10. Error Handling

### 10.1 User-Facing Errors
- **Network errors:** "Connection lost. Please check your internet and try again."
- **Validation errors:** Inline, specific (e.g., "Email address is invalid")
- **Server errors:** "Something went wrong. We've been notified and are looking into it."
- **File upload errors:** "File type not supported. Please upload PDF or CSV."

### 10.2 Email Sending Errors
- **SMTP failure:** Retry 3 times, then notify user
- **Invalid recipient:** Log error, notify user, don't retry
- **Rate limit:** Queue for later, send within 24 hours

### 10.3 Data Integrity
- **Duplicate invoice numbers:** Warn user, allow override
- **Orphaned records:** Background job to clean up
- **Concurrent edits:** Last write wins (acceptable for MVP)

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Business logic: due date calculation, status transitions
- Data validation: invoice amount, email format
- Template rendering: variable substitution

### 11.2 Integration Tests
- Email sending flow (end-to-end)
- Payment matching logic
- Background job execution

### 11.3 Manual Testing Checklist
- [ ] Upload invoice PDF and verify OCR extraction works
- [ ] Verify OCR confidence scores display correctly
- [ ] Test OCR with poor quality PDF (should handle gracefully)
- [ ] Review and edit OCR-extracted data before saving
- [ ] Upload invoice and verify all fields save correctly
- [ ] Forward email and verify invoice draft created
- [ ] Verify due date calculates correctly for Net 15/30/60
- [ ] Verify status changes from Pending → Due Soon → Overdue
- [ ] Send manual reminder and verify email received
- [ ] Mark invoice as paid and verify status updates
- [ ] Import payment CSV and verify matching works
- [ ] Connect SevDesk account via OAuth
- [ ] Import invoices from SevDesk and verify mapping
- [ ] Export invoice to SevDesk and verify creation
- [ ] Test bidirectional sync between system and SevDesk
- [ ] Verify payment status syncs from SevDesk
- [ ] Test sync conflict resolution
- [ ] Disconnect SevDesk integration
- [ ] View dashboard and verify all metrics are correct
- [ ] Test all filters and search on invoice list
- [ ] Test responsive design on tablet
- [ ] Test error handling (invalid file, network error, OCR failure, API errors, etc.)

### 11.4 User Acceptance Testing (UAT)
- 3-5 pilot users from target segment
- Real invoices, real customers
- 2-week trial period
- Feedback survey after trial
- Success metric: Would they pay for this?

---

## 12. Launch Checklist

### 12.1 Pre-Launch
- [ ] All P0 features complete and tested
- [ ] Security audit completed
- [ ] Privacy policy and terms of service published
- [ ] GDPR compliance verified (data export/delete)
- [ ] Email deliverability tested (not landing in spam)
- [ ] Error monitoring set up (Sentry or similar)
- [ ] Analytics set up (PostHog, Plausible, or similar)
- [ ] Backup and restore tested
- [ ] Performance tested (load testing)
- [ ] Documentation written (user guide, FAQ)

### 12.2 Launch Day
- [ ] Deploy to production
- [ ] Smoke test all critical flows
- [ ] Monitor error logs
- [ ] Monitor email sending
- [ ] Be available for support

### 12.3 Post-Launch (Week 1)
- [ ] Daily check of error logs
- [ ] Review user feedback
- [ ] Fix critical bugs within 24 hours
- [ ] Collect usage metrics
- [ ] Schedule user interviews

---

## 13. Success Metrics (MVP)

### 13.1 Product Metrics
- **Activation rate:** % of signups who upload first invoice
- **Time to first value:** Time from signup to first invoice tracked
- **OCR accuracy rate:** % of invoices with high-confidence OCR extraction (>80%)
- **OCR adoption rate:** % of users who use OCR vs manual entry
- **SevDesk connection rate:** % of users who connect SevDesk integration
- **Sync success rate:** % of SevDesk syncs that complete successfully
- **Active usage:** % of users who log in weekly
- **Invoice volume:** Average invoices per user per month
- **Reminder send rate:** % of invoices that get reminders sent
- **Payment tracking:** % of invoices marked as paid

### 13.2 Business Impact Metrics (User-Reported)
- **DSO reduction:** Average days reduced
- **Time saved:** Hours per week saved on manual chasing
- **Collection rate:** % of invoices paid within terms
- **User satisfaction:** NPS score

### 13.3 MVP Success Threshold
- **10 paying customers** within 8 weeks of launch
- **70% activation rate** (users who upload first invoice)
- **50% weekly active rate** (users who log in weekly)
- **NPS > 40** (users would recommend)

---

## 14. Known Limitations & Future Enhancements

### 14.1 MVP Limitations
- OCR accuracy may vary based on invoice quality and format
- OCR may not work well with handwritten invoices or non-standard formats
- No Open Banking - manual payment marking (except via SevDesk sync)
- Single accounting integration (SevDesk only, more in V2)
- Single user per company - no team collaboration
- English only - no multi-language support
- EUR only - no multi-currency (though system supports currency field)
- Basic email templates - no advanced personalization
- No mobile app - web only
- SevDesk sync is one-way or bidirectional, but not real-time (daily sync)

### 14.2 V1 Roadmap (Post-MVP)
- Improved OCR accuracy with machine learning
- Open Banking integration for automatic payment matching
- Multi-user support with roles
- Advanced reminder sequences (per customer)
- Cash flow forecasting
- Customer payment pattern analysis
- Additional accounting software integrations (SevDesk, Xero, LexOffice)
- Real-time webhook sync for SevDesk
- Mobile-responsive improvements

### 14.3 V2 Roadmap (6-12 months)
- Multi-language support (DE, FR, NL, PL)
- Multi-currency support
- SMS and WhatsApp reminders
- ERP integrations (SevDesk, Xero, LexOffice)
- Legal escalation workflow
- Credit risk scoring
- Advanced analytics and reporting
- API for third-party integrations

---

## 15. Appendix

### 15.1 Glossary
- **AR:** Accounts Receivable
- **DSO:** Days Sales Outstanding - average time to collect payment
- **Net 30:** Payment due 30 days after invoice date
- **Dunning:** Process of communicating with customers to collect overdue payments
- **OCR:** Optical Character Recognition - extracting text from images/PDFs
- **Open Banking:** API access to bank account data (with user consent)

### 15.2 References
- EU Late Payment Directive 2011/7/EU
- GDPR compliance requirements
- Email deliverability best practices
- Accounts receivable industry benchmarks

### 15.3 Assumptions
- Users have basic computer literacy
- Users have email access
- Users receive invoices as PDFs or can create them
- Users have bank account for receiving payments
- Target market is European SMEs (50-500 employees)

### 15.4 Dependencies
- Email service provider (AWS SES, SendGrid, Postmark)
- Object storage (S3 or compatible)
- Database (PostgreSQL)
- Hosting infrastructure (Fly.io, Railway, AWS)
- Domain and SSL certificate
- OCR service (OpenAI Vision API, AWS Textract, or Google Cloud Vision)
- SevDesk API access (OAuth 2.0 integration)
- Background job processor (Redis + Bull/BullMQ, or similar)

---

## Document Control

**Approval Required From:**
- [ ] Product Manager
- [ ] Engineering Lead
- [ ] Design Lead
- [ ] Founder/CEO

**Change Log:**
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-25 | Product Team | Initial MVP specification |
| 1.1 | 2026-01-25 | Product Team | Added OCR parsing and SevDesk integration |

---

**Next Steps:**
1. Review and approve this specification
2. Break down into engineering tasks
3. Create design mockups for key screens
4. Estimate development timeline
5. Begin sprint planning
