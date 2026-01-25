# AI-Native Functional Specification
## Receivable Notification System - AI Enhancement Layer

**Document Version:** 1.0  
**Last Updated:** January 25, 2026  
**Product Stage:** AI-Native Enhancement (Post-MVP)  
**Dependencies:** Requires core MVP functionality as defined in `functional-spec.md`

---

## 1. Executive Summary

### 1.1 Vision
Transform the Receivable Notification System from a **rule-based automation tool** into an **AI-native collections platform** that autonomously manages the entire accounts receivable lifecycle while preserving customer relationships.

### 1.2 Core AI Capabilities

| Capability | Description | Business Impact |
|------------|-------------|-----------------|
| **Autonomous Collection Agent** | AI agent that handles collection conversations end-to-end | 80% reduction in manual follow-up |
| **Predictive Cash Flow Intelligence** | ML models that forecast payments and identify risks | 40-50% DSO reduction |

### 1.3 Success Criteria
- **DSO reduction:** 40-50% improvement (vs 10-30% with base MVP)
- **Autonomous handling rate:** 80% of collection conversations handled without human intervention
- **Payment prediction accuracy:** >85% accuracy on 7-day payment probability
- **Cash flow forecast accuracy:** ±10% accuracy on weekly cash flow predictions
- **Customer relationship score:** Maintain or improve NPS despite automated collections

### 1.4 Key Differentiators
- **From static reminders to adaptive conversations** – AI learns what works for each customer
- **From reactive tracking to predictive intelligence** – Know which invoices will be paid before due date
- **From transactional to relationship-aware** – AI balances getting paid with preserving valuable customers

---

## 2. Architecture Overview

### 2.1 AI Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                               │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │  Dashboard  │  │ AI Insights Hub │  │ Collection Agent Control Center │  │
│  └─────────────┘  └─────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI ORCHESTRATION LAYER                             │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │  Collection Agent Engine    │  │  Prediction & Analytics Engine      │   │
│  │  - Conversation Manager     │  │  - Payment Probability Model        │   │
│  │  - Response Generator       │  │  - Cash Flow Forecaster             │   │
│  │  - Escalation Handler       │  │  - Risk Scoring Engine              │   │
│  │  - Channel Optimizer        │  │  - Customer Behavior Analyzer       │   │
│  └─────────────────────────────┘  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA & ML INFRASTRUCTURE                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ LLM Gateway │  │ ML Models   │  │ Vector DB   │  │ Event Stream        │ │
│  │ (OpenAI/    │  │ (Payment    │  │ (Embeddings │  │ (Customer           │ │
│  │  Anthropic) │  │  Prediction)│  │  & Context) │  │  Interactions)      │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CORE MVP LAYER                                     │
│  (Invoice Management, Customer Management, Reminder System, Integrations)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Integration Points with Core MVP

| Core MVP Component | AI Enhancement |
|--------------------|----------------|
| Invoice Ingestion | AI extracts context, identifies contract type, flags anomalies |
| Due Date Engine | AI predicts actual payment date vs contractual due date |
| Reminder System | Replaced by Autonomous Collection Agent |
| Dashboard | Enhanced with AI Insights Hub |
| Customer Management | Enriched with AI-generated customer intelligence |

---

## 3. Feature 1: Autonomous Collection Agent

### 3.1 Overview

The Autonomous Collection Agent (ACA) is an AI-powered system that manages the entire collection lifecycle for each invoice, from initial reminder through payment resolution or human escalation.

### 3.2 Agent Capabilities

#### 3.2.1 Core Agent Functions

| Function | Description | Autonomy Level |
|----------|-------------|----------------|
| **Initial Outreach** | Generates personalized reminder based on customer history | Fully Autonomous |
| **Follow-up Cadence** | Determines optimal timing and frequency | Fully Autonomous |
| **Tone Adaptation** | Adjusts communication style based on context | Fully Autonomous |
| **Response Handling** | Processes and responds to customer replies | Semi-Autonomous (may escalate) |
| **Negotiation** | Proposes payment plans, discusses disputes | Semi-Autonomous |
| **Escalation** | Hands off to human when needed | Human-in-the-loop |

#### 3.2.2 Agent Decision Framework

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT DECISION LOOP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. OBSERVE                                                      │
│     ├── Invoice status & history                                 │
│     ├── Customer behavior patterns                               │
│     ├── Previous communication outcomes                          │
│     ├── External signals (company news, seasonality)             │
│     └── Current communication context                            │
│                                                                  │
│  2. ANALYZE                                                      │
│     ├── Payment probability score                                │
│     ├── Customer relationship value                              │
│     ├── Risk of churn vs cost of delay                           │
│     ├── Optimal action recommendation                            │
│     └── Confidence level                                         │
│                                                                  │
│  3. DECIDE                                                       │
│     ├── If confidence > threshold → Act autonomously             │
│     ├── If confidence < threshold → Request human review         │
│     └── If high-risk action → Require human approval             │
│                                                                  │
│  4. ACT                                                          │
│     ├── Generate communication                                   │
│     ├── Select channel (email, phone script)                     │
│     ├── Execute action                                           │
│     └── Schedule follow-up                                       │
│                                                                  │
│  5. LEARN                                                        │
│     ├── Track outcome                                            │
│     ├── Update customer model                                    │
│     └── Improve future predictions                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Functional Requirements

#### 3.3.1 Intelligent Outreach Generation (Priority: P0)

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

#### 3.3.2 Adaptive Communication Cadence (Priority: P0)

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

#### 3.3.3 Customer Reply Processing (Priority: P0)

**User Story:** As a user, I want the AI to understand and appropriately respond to customer replies without my intervention for routine cases.

**Acceptance Criteria:**
- AI monitors incoming emails to company inbox
- AI classifies customer replies into categories:
  - **Payment Confirmation** – "Payment sent today"
  - **Payment Promise** – "Will pay by Friday"
  - **Dispute** – "We have concerns about the invoice"
  - **Request for Info** – "Can you resend the invoice?"
  - **Negotiation Request** – "Can we pay in installments?"
  - **Out of Office** – Auto-reply detection
  - **Unrelated** – Not about this invoice
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

#### 3.3.4 Automated Payment Plan Negotiation (Priority: P1)

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

I understand—cash flow timing can be challenging. I'd be happy to 
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

#### 3.3.5 Multi-Channel Orchestration (Priority: P1)

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
- Friendly but direct—this is unusual for them
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

#### 3.3.6 Escalation Management (Priority: P0)

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

#### 3.3.7 Learning & Optimization (Priority: P1)

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
┌─────────────────────────────────────────────────────────┐
│                    LEARNING LOOP                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ACTION → OUTCOME → ANALYSIS → MODEL UPDATE → ACTION    │
│                                                          │
│  Example:                                                │
│  - Sent friendly reminder to Customer X                  │
│  - No response after 5 days                              │
│  - Analysis: Customer X responds better to firm tone     │
│  - Update: Increase firmness for Customer X              │
│  - Next action: Use firmer tone                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Technical Requirements:**
- Outcome tracking for every AI action
- A/B testing framework
- Model retraining pipeline (weekly)
- Explainability dashboard (why did AI do X?)

### 3.4 Agent Control Center UI

#### 3.4.1 Agent Dashboard

**Components:**
1. **Active Conversations** - List of invoices AI is currently managing
2. **Pending Approvals** - Actions requiring human approval
3. **Recent Activity** - Timeline of AI actions
4. **Performance Metrics** - Success rates, response times
5. **Escalation Queue** - Items needing human intervention

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🤖 Collection Agent Control Center                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐      │
│ │ Active: 47       │ │ Pending: 5       │ │ Success Rate: 78%│      │
│ │ conversations    │ │ approvals        │ │ this month       │      │
│ └──────────────────┘ └──────────────────┘ └──────────────────┘      │
│                                                                      │
│ ⚠️ PENDING APPROVALS                                                │
│ ┌───────────────────────────────────────────────────────────────┐   │
│ │ □ Acme Corp - €12,300 - AI wants to offer payment plan        │   │
│ │   [Approve] [Modify] [Reject]                                  │   │
│ │ □ TechStart - €5,000 - Customer dispute detected              │   │
│ │   [View Details] [Take Over] [Let AI Continue]                 │   │
│ └───────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ 📋 ACTIVE CONVERSATIONS                                             │
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

#### 3.4.2 Conversation Detail View

**Components:**
1. **Conversation Timeline** - Full history of AI and human messages
2. **Customer Context Panel** - AI-generated customer summary
3. **AI Reasoning Panel** - Why AI took each action
4. **Action Controls** - Approve, modify, take over

#### 3.4.3 Agent Settings

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

## 4. Feature 2: Predictive Cash Flow Intelligence

### 4.1 Overview

Predictive Cash Flow Intelligence provides ML-powered forecasting and risk assessment to help users anticipate cash flow and proactively manage collection priorities.

### 4.2 Prediction Models

#### 4.2.1 Invoice Payment Probability Model

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

#### 4.2.2 Customer Risk Scoring Model

**Purpose:** Assess the credit risk of each customer based on their payment behavior and external signals.

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

#### 4.2.3 Cash Flow Forecasting Model

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
2. Expected value = Invoice Amount × P(paid in week N)
3. Aggregate across all invoices
4. Apply Monte Carlo simulation for confidence intervals

**Visualization:**
- Cash flow forecast chart (line graph with confidence bands)
- Weekly breakdown table
- Comparison to historical actuals

### 4.3 Functional Requirements

#### 4.3.1 Payment Probability Dashboard (Priority: P0)

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
│ 📊 INVOICE LIST - PRIORITIZED BY AI                                │
├─────────────────────────────────────────────────────────────────────┤
│ Customer     │ Amount   │ Due      │ Status   │ Payment Prob │ AI  │
├──────────────┼──────────┼──────────┼──────────┼──────────────┼─────┤
│ Gamma LLC    │ €2,100   │ +14 days │ Overdue  │ 🔴 23%       │ ⚠️  │
│ Beta Inc     │ €8,200   │ +7 days  │ Overdue  │ 🟡 52%       │ →   │
│ Acme Corp    │ €4,500   │ +3 days  │ Overdue  │ 🟢 85%       │ ✓   │
│ Delta Tech   │ €3,300   │ -5 days  │ Due Soon │ 🟢 91%       │ ✓   │
└─────────────────────────────────────────────────────────────────────┘

🔴 Low probability - AI recommends immediate escalation
🟡 Medium probability - AI actively managing  
🟢 High probability - Expected to pay without intervention
```

#### 4.3.2 Cash Flow Forecast View (Priority: P0)

**User Story:** As a user, I want to see predicted cash inflows for the next 4-8 weeks so I can plan my business finances.

**Acceptance Criteria:**
- Dedicated "Cash Flow Forecast" page
- Time series chart showing:
  - Predicted weekly cash inflows
  - Confidence interval bands
  - Historical actuals (for comparison)
- Table breakdown by:
  - Week
  - Expected amount (with range)
  - Contributing invoices
  - Confidence level
- Export forecast to CSV

**Forecast Dashboard:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 💰 CASH FLOW FORECAST                                               │
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
│  ━━ Predicted  ░░ Confidence Range  ── Historical                    │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│ Week    │ Expected   │ Range          │ Top Contributors           │
├─────────┼────────────┼────────────────┼────────────────────────────┤
│ Week 1  │ €23,450    │ €20K - €27K    │ Acme (€4.5K), Beta (€8.2K) │
│ Week 2  │ €18,700    │ €14K - €23K    │ Delta (€3.3K), ...         │
│ Week 3  │ €31,200    │ €25K - €37K    │ Epsilon (€12K), ...        │
└─────────────────────────────────────────────────────────────────────┘
```

#### 4.3.3 Customer Risk Profiles (Priority: P0)

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
│ 🏢 CUSTOMER: Acme Corp                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🤖 AI RISK ASSESSMENT                                           │ │
│ ├─────────────────────────────────────────────────────────────────┤ │
│ │                                                                  │ │
│ │  RISK SCORE: 28 (LOW RISK) ↘️ Improving                         │ │
│ │  ████████░░░░░░░░░░░░░░░░░░                                     │ │
│ │                                                                  │ │
│ │  FACTORS:                                                        │ │
│ │  ✅ Payment History: Avg 12 days to pay (vs 30 day terms)       │ │
│ │  ✅ Trend: Payment times improving over last 6 months           │ │
│ │  ⚠️ Current AR: €4,500 outstanding (normal for volume)          │ │
│ │  ✅ Relationship: 2-year customer, €45K annual spend            │ │
│ │                                                                  │ │
│ │  AI RECOMMENDATION:                                              │ │
│ │  "Low-risk customer with excellent payment history. Consider    │ │
│ │   offering extended terms (Net 45) to strengthen relationship." │ │
│ │                                                                  │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

#### 4.3.4 Proactive Risk Alerts (Priority: P1)

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
⚠️ RISK ALERT: Beta Inc

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

#### 4.3.5 Working Capital Optimization (Priority: P2)

**User Story:** As a user, I want AI to recommend actions that could improve my cash flow, such as offering early payment discounts.

**Recommendations Engine:**

| Scenario | AI Recommendation | Expected Impact |
|----------|-------------------|-----------------|
| Customer usually pays Day 25 | Offer 2% discount for payment by Day 10 | Expect 60% take rate, 15-day DSO improvement |
| High-value customer, low risk | Extend Net 45 terms to strengthen relationship | 3% churn risk reduction |
| New customer, unknown risk | Require 50% deposit on first project | Risk mitigation |
| Customer with cash flow issues | Offer 3-month payment plan | 40% higher collection rate vs aggressive tactics |

**Acceptance Criteria:**
- "Opportunities" section on dashboard
- AI-generated recommendations with expected ROI
- User can accept/decline recommendations
- Track outcomes to improve future recommendations

#### 4.3.6 Invoice Anomaly Detection (Priority: P1)

**User Story:** As a user, I want the AI to flag unusual invoices before I send reminders.

**Anomalies Detected:**
- Invoice amount significantly higher than typical for customer
- Invoice to new customer with high-risk signals
- Duplicate invoice number
- Invoice date in distant past
- Amount doesn't match typical project size

**Example Alert:**
```
⚠️ ANOMALY DETECTED: Invoice #INV-2024-112

This invoice for €47,500 to "NewCorp Ltd" is unusual:
- 3x larger than your typical invoice (avg €15,000)
- First invoice to this customer
- No signed contract on file

Before sending reminders, please verify:
□ Amount is correct
□ Customer has approved the work
□ Payment terms are agreed

[Confirm & Proceed] [Review Invoice] [Cancel Reminders]
```

### 4.4 AI Insights Hub UI

#### 4.4.1 Main Insights Dashboard

**Components:**
1. **Cash Flow Forecast Widget** - Chart + summary
2. **Payment Probability Summary** - Distribution of invoices by probability
3. **Risk Overview** - Customer risk distribution
4. **Action Recommendations** - AI-suggested actions
5. **Anomaly Alerts** - Items needing attention

**Wireframe:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🧠 AI INSIGHTS HUB                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │ 💰 NEXT 4 WEEKS FORECAST    │ │ 📊 PAYMENT PROBABILITY          │ │
│ │                             │ │                                  │ │
│ │ Expected: €89,650           │ │ 🟢 High (>70%):   12 invoices   │ │
│ │ Range: €72K - €107K         │ │ 🟡 Medium:         8 invoices   │ │
│ │                             │ │ 🔴 Low (<40%):     4 invoices   │ │
│ │ [View Full Forecast]        │ │                                  │ │
│ └─────────────────────────────┘ └─────────────────────────────────┘ │
│                                                                      │
│ ┌─────────────────────────────┐ ┌─────────────────────────────────┐ │
│ │ ⚠️ RISK ALERTS (3)          │ │ 💡 AI RECOMMENDATIONS           │ │
│ │                             │ │                                  │ │
│ │ • Beta Inc: Risk ↑ +22pts   │ │ • Offer Acme 2% early pay       │ │
│ │ • Gamma LLC: 45 days OD     │ │   Est. impact: 15 days DSO ↓    │ │
│ │ • New invoice anomaly       │ │ • Call Beta Inc AP directly     │ │
│ │                             │ │   Est. impact: €8,200 collected │ │
│ │ [View All Alerts]           │ │ [View All Recommendations]       │ │
│ └─────────────────────────────┘ └─────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. Data Model Extensions
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

### 5.2 New AI Entities

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
feature_importance: JSONB (top features contributing to prediction)
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

(Store daily snapshots for trend analysis)
```

#### CashFlowForecast
```
id: UUID (PK)
company_id: UUID (FK)
forecast_date: Date (when forecast was made)
target_week_start: Date
expected_amount: Decimal(12,2)
lower_bound: Decimal(12,2)
upper_bound: Decimal(12,2)
confidence_level: Decimal(3,2)
contributing_invoices: JSONB (invoice_id, expected_amount pairs)
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

### 5.2 Extensions to Existing Entities

#### Invoice (additions)
```
+ ai_conversation_id: UUID (FK, nullable)
+ payment_probability_7d: Decimal(3,2) (nullable)
+ payment_probability_30d: Decimal(3,2) (nullable)
+ expected_payment_date: Date (nullable)
+ prediction_updated_at: Timestamp (nullable)
+ anomaly_flags: JSONB (nullable)
```

#### Customer (additions)
```
+ risk_score: Integer (nullable, 0-100)
+ risk_category: Enum (low, medium, high, critical) (nullable)
+ risk_updated_at: Timestamp (nullable)
+ ai_customer_summary: Text (nullable)
+ avg_days_to_pay: Decimal(5,2) (nullable)
+ payment_reliability_score: Decimal(3,2) (nullable, 0.00-1.00)
+ preferred_contact_channel: Enum (email, phone, linkedin) (nullable)
+ preferred_contact_time: JSONB (nullable, day_of_week, time preferences)
+ relationship_value_score: Decimal(10,2) (nullable, lifetime value)
```

---

## 6. API Endpoints (AI Layer)

### 6.1 Collection Agent APIs

```
# Conversation Management
GET    /api/ai/conversations                    - List AI conversations
GET    /api/ai/conversations/:id                - Get conversation detail
POST   /api/ai/conversations/:id/pause          - Pause AI handling
POST   /api/ai/conversations/:id/resume         - Resume AI handling
POST   /api/ai/conversations/:id/escalate       - Escalate to human
POST   /api/ai/conversations/:id/take-over      - Human takes over

# Action Management
GET    /api/ai/actions/pending                  - List pending approvals
POST   /api/ai/actions/:id/approve              - Approve AI action
POST   /api/ai/actions/:id/reject               - Reject AI action
POST   /api/ai/actions/:id/modify               - Modify and approve

# Message Management
GET    /api/ai/messages/:conversation_id        - Get conversation messages
POST   /api/ai/messages/:conversation_id/draft  - Create human message draft
POST   /api/ai/messages/:id/send                - Send message

# Settings
GET    /api/ai/settings                         - Get AI settings
PUT    /api/ai/settings                         - Update AI settings
GET    /api/ai/settings/payment-plans           - Get payment plan rules
PUT    /api/ai/settings/payment-plans           - Update payment plan rules
```

### 6.2 Prediction APIs

```
# Invoice Predictions
GET    /api/ai/predictions/invoice/:id          - Get invoice payment prediction
POST   /api/ai/predictions/invoices/refresh     - Refresh all predictions

# Customer Risk
GET    /api/ai/risk/customer/:id                - Get customer risk profile
GET    /api/ai/risk/customers                   - List all customer risk scores
GET    /api/ai/risk/alerts                      - Get risk alerts

# Cash Flow Forecast
GET    /api/ai/forecast                         - Get cash flow forecast
GET    /api/ai/forecast/history                 - Get forecast vs actuals history

# Recommendations
GET    /api/ai/recommendations                  - Get AI recommendations
POST   /api/ai/recommendations/:id/accept       - Accept recommendation
POST   /api/ai/recommendations/:id/dismiss      - Dismiss recommendation
```

### 6.3 Analytics APIs

```
GET    /api/ai/analytics/agent-performance      - Agent success metrics
GET    /api/ai/analytics/prediction-accuracy    - Model accuracy metrics
GET    /api/ai/analytics/learning-events        - Learning signal summary
```

---

## 7. Background Jobs (AI Layer)

### 7.1 Collection Agent Jobs

#### Agent Decision Loop (High Frequency)
- **Frequency:** Every 1 hour
- **Purpose:** Process agent decisions and execute approved actions
- **Logic:**
  1. Find conversations with `next_action_at <= NOW()`
  2. For each conversation:
     - Load context (invoice, customer, history)
     - Generate AI decision
     - If confidence > threshold: Execute autonomously
     - If confidence < threshold: Create pending approval
  3. Schedule next action for each conversation

#### Response Processing Job
- **Frequency:** Every 15 minutes
- **Purpose:** Process incoming customer replies
- **Logic:**
  1. Check email inbox for new messages
  2. Match to existing conversations
  3. Classify intent and sentiment
  4. Update conversation state
  5. Trigger appropriate response or escalation

### 7.2 Prediction Jobs

#### Payment Prediction Refresh
- **Frequency:** Daily at 3 AM
- **Purpose:** Update payment predictions for all open invoices
- **Logic:**
  1. Load all unpaid invoices
  2. For each invoice:
     - Gather features
     - Run prediction model
     - Store predictions
  3. Update invoice records with latest predictions

#### Customer Risk Score Refresh
- **Frequency:** Daily at 4 AM
- **Purpose:** Update risk scores for all customers
- **Logic:**
  1. Load all active customers
  2. For each customer:
     - Calculate component scores
     - Generate overall risk score
     - Detect risk changes
     - Generate alerts if needed
  3. Store daily snapshot

#### Cash Flow Forecast Generation
- **Frequency:** Daily at 5 AM
- **Purpose:** Generate weekly cash flow forecasts
- **Logic:**
  1. Get all open invoices with predictions
  2. Run Monte Carlo simulation
  3. Generate weekly forecasts with confidence intervals
  4. Store forecasts
  5. Compare previous forecasts with actuals

### 7.3 Learning Jobs

#### Model Retraining Pipeline
- **Frequency:** Weekly (Sunday 2 AM)
- **Purpose:** Retrain ML models with new data
- **Logic:**
  1. Extract training data from outcomes
  2. Validate data quality
  3. Retrain payment prediction model
  4. Retrain risk scoring model
  5. A/B test new model vs current
  6. Deploy if improvement meets threshold

#### Learning Event Processing
- **Frequency:** Daily at 6 AM
- **Purpose:** Process learning signals from user actions
- **Logic:**
  1. Find unprocessed learning events
  2. Aggregate signals by type
  3. Update model parameters
  4. Update agent behavior rules
  5. Mark events as processed

---

## 8. Technical Requirements

### 8.1 LLM Integration

**Primary Provider:** OpenAI GPT-4 or Anthropic Claude
**Use Cases:**
- Message generation
- Reply classification
- Sentiment analysis
- Customer summary generation

**Requirements:**
- API abstraction layer (support multiple providers)
- Prompt versioning and management
- Response caching for repeated queries
- Cost monitoring and limits
- Fallback to simpler model if primary unavailable

**Prompt Engineering:**
- Maintain prompt library with version control
- Include company brand voice guidelines
- Inject customer context dynamically
- Include guardrails to prevent off-brand messaging

### 8.2 ML Infrastructure

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

### 8.3 Vector Database (Optional)

**Use Cases:**
- Store customer communication embeddings
- Semantic search across conversation history
- Find similar customer situations

**Options:** Pinecone, Weaviate, or Chroma

### 8.4 Event Streaming

**Use Cases:**
- Track all AI actions and outcomes
- Real-time learning signals
- Audit trail

**Options:** Redis Streams, Kafka, or simpler database-based event log

---

## 9. Privacy & Security

### 9.1 Data Handling

- **LLM Data:** Never send sensitive financial data to external LLMs
- **Anonymization:** Customer names/amounts can be sent; full bank details cannot
- **Logging:** Log AI decisions but redact sensitive content
- **Retention:** AI conversation data follows same retention as core data (7 years)

### 9.2 User Consent

- **AI Disclosure:** Users must acknowledge AI will communicate with their customers
- **Customer Disclosure:** Optional footer in AI emails: "This message was composed with AI assistance"
- **Opt-out:** Customers can request human-only communication

### 9.3 Audit Trail

- Every AI action logged with:
  - Timestamp
  - Action type
  - AI reasoning
  - Confidence score
  - Human approval (if required)
  - Outcome

---

## 10. Success Metrics (AI Layer)

### 10.1 Collection Agent Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Autonomous handling rate | >80% | % of invoices resolved without human intervention |
| Response time | <4 hours | Time from customer reply to AI response |
| Escalation rate | <15% | % of conversations escalated to human |
| User override rate | <10% | % of AI drafts modified by users |
| Payment plan success rate | >70% | % of offered plans that result in payment |

### 10.2 Prediction Accuracy Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| 7-day payment prediction AUROC | >0.85 | Model accuracy on 7-day predictions |
| Expected payment date accuracy | ±3 days for 70% | Prediction vs actual payment date |
| Risk score stability | <5% daily variance | Score shouldn't fluctuate wildly |
| Cash flow forecast accuracy | ±10% | Predicted vs actual weekly cash flow |

### 10.3 Business Impact Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| DSO reduction | 40-50% | Compared to pre-AI baseline |
| Collection rate | >95% | % of invoices eventually collected |
| Time to first payment | -30% | Reduction in avg days to first payment |
| Customer churn from collections | <2% | % of customers churned due to collection tactics |

---

## 11. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- [ ] Set up LLM integration layer
- [ ] Implement basic message generation
- [ ] Build AI conversation data model
- [ ] Create Agent Control Center UI skeleton
- [ ] Implement manual approval workflow

### Phase 2: Autonomous Agent (Weeks 5-8)
- [ ] Implement response classification
- [ ] Build adaptive cadence logic
- [ ] Add payment plan negotiation
- [ ] Implement escalation triggers
- [ ] Complete Agent Control Center UI

### Phase 3: Predictions (Weeks 9-12)
- [ ] Build payment prediction model
- [ ] Implement customer risk scoring
- [ ] Create cash flow forecasting
- [ ] Build AI Insights Hub UI
- [ ] Implement alert system

### Phase 4: Learning & Optimization (Weeks 13-16)
- [ ] Implement learning event tracking
- [ ] Build model retraining pipeline
- [ ] Add A/B testing framework
- [ ] Create analytics dashboards
- [ ] Performance tuning and optimization

---

## 12. Dependencies & Risks

### 12.1 Dependencies

| Dependency | Type | Mitigation |
|------------|------|------------|
| LLM API (OpenAI/Anthropic) | External | Multi-provider support, caching, fallbacks |
| Email deliverability | External | Use established ESP, monitor reputation |
| Historical data for ML | Internal | Need 6+ months of payment data for accurate models |
| User adoption | Internal | Gradual rollout, supervised mode first |

### 12.2 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AI sends inappropriate message | Medium | High | Strict guardrails, approval workflow, monitoring |
| Prediction model is inaccurate | Medium | Medium | Start conservative, A/B test, manual override |
| Customer complains about AI | Low | High | Disclosure option, human takeover capability |
| LLM costs exceed budget | Medium | Medium | Caching, simpler models for routine tasks, usage limits |
| Data privacy concerns | Low | High | Clear consent, no sensitive data to LLMs, GDPR compliance |

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

---

**Next Steps:**
1. Review and approve this AI specification
2. Prioritize features for first release
3. Create technical architecture document
4. Estimate AI/ML infrastructure costs
5. Begin Phase 1 implementation
