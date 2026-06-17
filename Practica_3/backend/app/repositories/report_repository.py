from datetime import date
from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb


REPORT_COLUMNS = """
    report.id,
    report.report_type::TEXT AS report_type,
    report.format::TEXT AS format,
    report.status::TEXT AS status,
    report.file_name,
    report.filters,
    report.generated_by,
    users.full_name AS generated_by_name,
    report.error_message,
    report.created_at,
    report.generated_at
"""


def create_report(
    connection: Connection,
    report_type: str,
    report_format: str,
    filters: dict[str, Any],
    generated_by: int,
) -> dict[str, Any]:
    query = """
        INSERT INTO reports (
            report_type,
            format,
            status,
            filters,
            generated_by
        )
        VALUES (
            %s::report_type,
            %s::report_format,
            'PENDING',
            %s,
            %s
        )
        RETURNING id
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                report_type,
                report_format,
                Jsonb(filters),
                generated_by,
            ),
        )
        report_id = int(
            cursor.fetchone()["id"]
        )

    connection.commit()

    report = find_report_by_id(
        connection,
        report_id,
    )

    if report is None:
        raise RuntimeError(
            "No fue posible recuperar el reporte creado"
        )

    return report


def find_report_by_id(
    connection: Connection,
    report_id: int,
) -> dict[str, Any] | None:
    query = f"""
        SELECT {REPORT_COLUMNS}
        FROM reports report
        LEFT JOIN users
            ON users.id = report.generated_by
        WHERE report.id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (report_id,))
        return cursor.fetchone()


def get_report_internal(
    connection: Connection,
    report_id: int,
) -> dict[str, Any] | None:
    query = """
        SELECT
            id,
            report_type::TEXT AS report_type,
            format::TEXT AS format,
            status::TEXT AS status,
            file_name,
            file_path,
            filters,
            generated_by,
            error_message,
            created_at,
            generated_at
        FROM reports
        WHERE id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (report_id,))
        return cursor.fetchone()


def list_reports(
    connection: Connection,
    page: int,
    page_size: int,
) -> tuple[list[dict[str, Any]], int]:
    count_query = """
        SELECT COUNT(*) AS total
        FROM reports
    """

    with connection.cursor() as cursor:
        cursor.execute(count_query)
        total = int(cursor.fetchone()["total"])

    query = f"""
        SELECT {REPORT_COLUMNS}
        FROM reports report
        LEFT JOIN users
            ON users.id = report.generated_by
        ORDER BY report.created_at DESC, report.id DESC
        LIMIT %s
        OFFSET %s
    """

    offset = (page - 1) * page_size

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (page_size, offset),
        )
        items = cursor.fetchall()

    return items, total


def mark_report_running(
    connection: Connection,
    report_id: int,
) -> None:
    query = """
        UPDATE reports
        SET
            status = 'RUNNING',
            error_message = NULL
        WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (report_id,))

    connection.commit()


def mark_report_success(
    connection: Connection,
    report_id: int,
    file_name: str,
    file_path: str,
) -> None:
    query = """
        UPDATE reports
        SET
            status = 'SUCCESS',
            file_name = %s,
            file_path = %s,
            generated_at = CURRENT_TIMESTAMP,
            error_message = NULL
        WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                file_name,
                file_path,
                report_id,
            ),
        )

    connection.commit()


def mark_report_error(
    connection: Connection,
    report_id: int,
    error_message: str,
) -> None:
    query = """
        UPDATE reports
        SET
            status = 'ERROR',
            error_message = %s,
            generated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                error_message[:2000],
                report_id,
            ),
        )

    connection.commit()


def get_report_rows(
    connection: Connection,
    filters: dict[str, Any],
    report_type: str,
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    parameters: list[Any] = []

    date_from = filters.get("date_from")
    date_to = filters.get("date_to")
    provider_id = filters.get("provider_id")
    status_filter = filters.get("status")

    if date_from:
        conditions.append(
            "invoice.invoice_date >= %s"
        )
        parameters.append(
            date.fromisoformat(date_from)
        )

    if date_to:
        conditions.append(
            "invoice.invoice_date <= %s"
        )
        parameters.append(
            date.fromisoformat(date_to)
        )

    if provider_id:
        conditions.append(
            "invoice.provider_id = %s"
        )
        parameters.append(provider_id)

    if status_filter:
        conditions.append(
            "invoice.status::TEXT = %s"
        )
        parameters.append(status_filter)

    if report_type == "ERRORS":
        conditions.append(
            """
            invoice.status IN (
                'REJECTED',
                'ERROR',
                'DUPLICATE'
            )
            """
        )

    where_clause = ""

    if conditions:
        where_clause = (
            "WHERE " + " AND ".join(conditions)
        )

    query = f"""
        SELECT
            invoice.id,
            invoice.invoice_number,
            invoice.invoice_date,
            COALESCE(
                provider.name,
                invoice.detected_provider_name,
                'Sin proveedor'
            ) AS provider_name,
            COALESCE(
                provider.nit::TEXT,
                invoice.detected_nit,
                ''
            ) AS nit,
            category.name::TEXT AS category_name,
            invoice.subtotal,
            invoice.tax,
            invoice.total,
            invoice.currency,
            invoice.ocr_confidence,
            invoice.status::TEXT AS status,
            invoice.original_file_name,
            invoice.created_at
        FROM invoices invoice
        LEFT JOIN providers provider
            ON provider.id = invoice.provider_id
        LEFT JOIN invoice_categories category
            ON category.id = invoice.category_id
        {where_clause}
        ORDER BY
            invoice.invoice_date DESC NULLS LAST,
            invoice.created_at DESC,
            invoice.id DESC
    """

    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        return cursor.fetchall()
