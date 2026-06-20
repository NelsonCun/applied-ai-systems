CREATE OR REPLACE VIEW vw_invoice_listing AS
SELECT
    invoice.id,
    invoice.invoice_number,
    invoice.invoice_date,
    invoice.detected_provider_name,
    invoice.detected_nit,
    provider.name AS provider_name,
    provider.nit AS provider_nit,
    category.name AS category_name,
    invoice.subtotal,
    invoice.tax,
    invoice.total,
    invoice.currency,
    invoice.ocr_confidence,
    invoice.status,
    invoice.original_file_name,
    invoice.created_at,
    invoice.processed_at,
    creator.full_name AS created_by_name
FROM invoices invoice
LEFT JOIN providers provider
    ON provider.id = invoice.provider_id
LEFT JOIN invoice_categories category
    ON category.id = invoice.category_id
INNER JOIN users creator
    ON creator.id = invoice.created_by;

CREATE OR REPLACE VIEW vw_dashboard_summary AS
SELECT
    COUNT(*) AS total_invoices,

    COUNT(*) FILTER (
        WHERE status = 'PENDING'
    ) AS pending_invoices,

    COUNT(*) FILTER (
        WHERE status = 'PROCESSING'
    ) AS processing_invoices,

    COUNT(*) FILTER (
        WHERE status = 'PROCESSED'
    ) AS processed_invoices,

    COUNT(*) FILTER (
        WHERE status = 'REJECTED'
    ) AS rejected_invoices,

    COUNT(*) FILTER (
        WHERE status = 'ERROR'
    ) AS error_invoices,

    COUNT(*) FILTER (
        WHERE status = 'DUPLICATE'
    ) AS duplicate_invoices,

    COALESCE(
        SUM(total) FILTER (
            WHERE status = 'PROCESSED'
        ),
        0
    )::NUMERIC(14, 2) AS processed_total,

    COALESCE(
        SUM(tax) FILTER (
            WHERE status = 'PROCESSED'
        ),
        0
    )::NUMERIC(14, 2) AS processed_tax,

    COALESCE(
        ROUND(
            AVG(ocr_confidence) FILTER (
                WHERE ocr_confidence IS NOT NULL
            ),
            2
        ),
        0
    ) AS average_ocr_confidence
FROM invoices;

CREATE OR REPLACE VIEW vw_provider_statistics AS
SELECT
    provider.id AS provider_id,
    provider.name AS provider_name,
    provider.nit,

    COUNT(invoice.id) AS invoice_count,

    COUNT(invoice.id) FILTER (
        WHERE invoice.status = 'PROCESSED'
    ) AS processed_count,

    COALESCE(
        SUM(invoice.total) FILTER (
            WHERE invoice.status = 'PROCESSED'
        ),
        0
    )::NUMERIC(14, 2) AS total_amount,

    COALESCE(
        AVG(invoice.ocr_confidence) FILTER (
            WHERE invoice.ocr_confidence IS NOT NULL
        ),
        0
    )::NUMERIC(5, 2) AS average_confidence
FROM providers provider
LEFT JOIN invoices invoice
    ON invoice.provider_id = provider.id
GROUP BY
    provider.id,
    provider.name,
    provider.nit;

CREATE OR REPLACE VIEW vw_processing_performance AS
SELECT
    stage,
    COUNT(*) AS execution_count,

    COUNT(*) FILTER (
        WHERE status = 'SUCCESS'
    ) AS success_count,

    COUNT(*) FILTER (
        WHERE status = 'ERROR'
    ) AS error_count,

    COALESCE(
        ROUND(AVG(duration_ms), 2),
        0
    ) AS average_duration_ms
FROM processing_logs
GROUP BY stage;
