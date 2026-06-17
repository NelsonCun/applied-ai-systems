from typing import Any

from psycopg import Connection


def get_dashboard_summary(
    connection: Connection,
) -> dict[str, Any]:
    query = """
        SELECT
            total_invoices,
            pending_invoices,
            processing_invoices,
            processed_invoices,
            rejected_invoices,
            error_invoices,
            duplicate_invoices,
            processed_total,
            processed_tax,
            average_ocr_confidence
        FROM vw_dashboard_summary
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()


def get_status_metrics(
    connection: Connection,
) -> list[dict[str, Any]]:
    query = """
        SELECT
            status::TEXT AS status,
            COUNT(*) AS invoice_count,
            COALESCE(
                SUM(total),
                0
            )::NUMERIC(14, 2) AS total_amount
        FROM invoices
        GROUP BY status
        ORDER BY status
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_provider_metrics(
    connection: Connection,
    limit: int = 10,
) -> list[dict[str, Any]]:
    query = """
        SELECT
            provider_id,
            provider_name,
            invoice_count,
            processed_count,
            total_amount,
            average_confidence
        FROM vw_provider_statistics
        ORDER BY
            total_amount DESC,
            invoice_count DESC,
            provider_name
        LIMIT %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (limit,))
        return cursor.fetchall()


def get_monthly_metrics(
    connection: Connection,
) -> list[dict[str, Any]]:
    query = """
        SELECT
            TO_CHAR(
                DATE_TRUNC('month', created_at),
                'YYYY-MM'
            ) AS month,

            COUNT(*) AS invoice_count,

            COUNT(*) FILTER (
                WHERE status = 'PROCESSED'
            ) AS processed_count,

            COALESCE(
                SUM(total) FILTER (
                    WHERE status = 'PROCESSED'
                ),
                0
            )::NUMERIC(14, 2) AS total_amount
        FROM invoices
        WHERE created_at >= (
            DATE_TRUNC('month', CURRENT_DATE)
            - INTERVAL '11 months'
        )
        GROUP BY DATE_TRUNC('month', created_at)
        ORDER BY DATE_TRUNC('month', created_at)
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()
