-- Materialized views for expensive analytics queries.
-- Refreshed concurrently by the nightly Hetzner cron job
-- (POST /internal/cron/refresh-materialized-views).

-- ── customer_payment_stats ────────────────────────────────────────────────────
-- Precomputed payment behavior summary per customer.
-- Used by the AI risk scorer as a feature source and by the customer detail page.

CREATE MATERIALIZED VIEW customer_payment_stats AS
SELECT
    c.id                                                            AS customer_id,
    c.company_id,
    COUNT(DISTINCT i.id)                                            AS total_invoices,
    COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'paid')          AS paid_invoices,
    COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'overdue')       AS overdue_invoices,
    SUM(i.amount)                                                   AS total_billed,
    COALESCE(SUM(p.amount), 0)                                      AS total_paid,
    AVG(p.payment_date - i.due_date)                                AS avg_days_late,
    MAX(i.due_date)                                                 AS last_invoice_due_date,
    NOW()                                                           AS refreshed_at
FROM customers c
LEFT JOIN invoices i  ON i.customer_id = c.id   AND i.deleted_at IS NULL
LEFT JOIN payments p  ON p.invoice_id  = i.id
WHERE c.deleted_at IS NULL
GROUP BY c.id, c.company_id;

CREATE UNIQUE INDEX ON customer_payment_stats(customer_id);
CREATE INDEX        ON customer_payment_stats(company_id);


-- ── company_ar_summary ────────────────────────────────────────────────────────
-- Pre-aggregated accounts receivable KPIs per company.
-- Powers the Dashboard stats endpoint (replaces expensive real-time aggregation).

CREATE MATERIALIZED VIEW company_ar_summary AS
SELECT
    i.company_id,
    COUNT(*)                                              AS total_invoices,
    COUNT(*) FILTER (WHERE i.status = 'overdue')         AS overdue_count,
    COUNT(*) FILTER (WHERE i.status = 'due_soon')        AS due_soon_count,
    COUNT(*) FILTER (WHERE i.status = 'paid')            AS paid_count,
    SUM(i.amount)                                        AS total_amount,
    SUM(i.amount) FILTER (WHERE i.status = 'overdue')   AS overdue_amount,
    SUM(i.amount) FILTER (WHERE i.status IN ('pending', 'due_soon', 'overdue')) AS outstanding_amount,
    -- DSO: (Outstanding / Total Billed) * 30
    CASE
        WHEN SUM(i.amount) > 0
        THEN ROUND((SUM(i.amount) FILTER (WHERE i.status IN ('pending', 'due_soon', 'overdue')) / SUM(i.amount)) * 30, 1)
        ELSE 0
    END                                                  AS dso_days,
    NOW()                                                AS refreshed_at
FROM invoices i
WHERE i.deleted_at IS NULL
GROUP BY i.company_id;

CREATE UNIQUE INDEX ON company_ar_summary(company_id);
