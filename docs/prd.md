
## **MVP (4–8 weeks)** — “Minimum usable for revenue”

1. **Invoice ingestion**

   * Upload PDF/CSV
   * Email forwarding (`invoices@domain`)
   * Manual entry

2. **Due date engine**

   * Calculate due date based on:

     * invoice date
     * payment terms (Net15/30/60)
     * EU Late Payment Regulation (optional flag)

3. **Overdue detection**

   * Status: `Pending | Due Soon | Overdue | Paid`

4. **Automated reminders**

   * Reminder templates (friendly, firm)
   * Send via email SMTP
   * Attach invoice link

5. **Bank payment matching**

   * Manual marking in MVP
   * CSV import of payments

6. **Dashboard**

   * Total outstanding
   * DSO estimate
   * Overdue list