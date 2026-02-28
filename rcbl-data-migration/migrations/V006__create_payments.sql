-- Tracks payments received against invoices.
-- Over-payment validation is enforced by a trigger in V020.

CREATE TABLE payments (
    id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id     UUID         NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    amount         DECIMAL(10,2) NOT NULL,
    payment_date   DATE         NOT NULL,
    payment_method VARCHAR(20)  NOT NULL CHECK (payment_method IN ('bank_transfer', 'check', 'cash', 'other')),
    source         VARCHAR(20)  NOT NULL CHECK (source IN ('manual', 'csv_import', 'api_sync')),
    notes          TEXT,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_payment_amount CHECK (amount > 0)
);

CREATE INDEX idx_payments_invoice_id   ON payments(invoice_id);
CREATE INDEX idx_payments_payment_date ON payments(payment_date);
CREATE INDEX idx_payments_created_at   ON payments(created_at);
