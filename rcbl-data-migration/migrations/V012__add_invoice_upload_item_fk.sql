-- Resolves the circular dependency between invoices and invoice_upload_items.
-- invoices was created first (V005) with upload_item_id as a plain UUID column.
-- Now that invoice_upload_items exists (V011), we add the FK constraint.

ALTER TABLE invoices
    ADD CONSTRAINT fk_invoices_upload_item
        FOREIGN KEY (upload_item_id)
        REFERENCES invoice_upload_items(id)
        ON DELETE SET NULL;
