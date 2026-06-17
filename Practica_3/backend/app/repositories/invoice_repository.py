from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb


INVOICE_COLUMNS = """
    invoice.id,
    invoice.invoice_number,
    invoice.invoice_date,

    invoice.provider_id,
    provider.name AS provider_name,

    invoice.category_id,
    category.name::TEXT AS category_name,

    invoice.detected_provider_name,
    invoice.detected_nit,

    invoice.subtotal,
    invoice.tax,
    invoice.total,
    invoice.currency,

    invoice.original_file_name,
    invoice.file_path,
    invoice.processed_file_path,
    invoice.file_sha256,
    invoice.mime_type,
    invoice.file_size_bytes,

    invoice.ocr_confidence,
    invoice.extracted_data,
    invoice.validation_errors,

    invoice.status::TEXT AS status,
    invoice.duplicate_of_invoice_id,

    invoice.created_by,
    invoice.created_at,
    invoice.processed_at,
    invoice.confirmed_at,
    invoice.updated_at
"""


def provider_exists(
    connection: Connection,
    provider_id: int,
) -> bool:
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM providers
            WHERE id = %s
              AND is_active = TRUE
        ) AS exists
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (provider_id,))
        row = cursor.fetchone()

    return bool(row["exists"])


def category_exists(
    connection: Connection,
    category_id: int,
) -> bool:
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM invoice_categories
            WHERE id = %s
              AND is_active = TRUE
        ) AS exists
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (category_id,))
        row = cursor.fetchone()

    return bool(row["exists"])


def find_original_by_hash(
    connection: Connection,
    file_sha256: str,
) -> dict[str, Any] | None:
    query = """
        SELECT
            id,
            file_path,
            original_file_name,
            mime_type,
            file_size_bytes
        FROM invoices
        WHERE file_sha256 = %s
          AND duplicate_of_invoice_id IS NULL
        ORDER BY id
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (file_sha256,))
        return cursor.fetchone()


def find_invoice_by_id(
    connection: Connection,
    invoice_id: int,
) -> dict[str, Any] | None:
    query = f"""
        SELECT {INVOICE_COLUMNS}
        FROM invoices invoice
        LEFT JOIN providers provider
            ON provider.id = invoice.provider_id
        LEFT JOIN invoice_categories category
            ON category.id = invoice.category_id
        WHERE invoice.id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (invoice_id,))
        return cursor.fetchone()


def create_invoice_record(
    connection: Connection,
    data: dict[str, Any],
) -> int:
    query = """
        INSERT INTO invoices (
            provider_id,
            category_id,
            original_file_name,
            file_path,
            file_sha256,
            mime_type,
            file_size_bytes,
            status,
            duplicate_of_invoice_id,
            created_by
        )
        VALUES (
            %(provider_id)s,
            %(category_id)s,
            %(original_file_name)s,
            %(file_path)s,
            %(file_sha256)s,
            %(mime_type)s,
            %(file_size_bytes)s,
            %(status)s,
            %(duplicate_of_invoice_id)s,
            %(created_by)s
        )
        RETURNING id
    """

    with connection.cursor() as cursor:
        cursor.execute(query, data)
        return int(cursor.fetchone()["id"])


def create_processing_log(
    connection: Connection,
    invoice_id: int,
    user_id: int,
    status: str,
    message: str,
    details: dict[str, Any],
) -> None:
    query = """
        INSERT INTO processing_logs (
            invoice_id,
            user_id,
            stage,
            status,
            message,
            details,
            started_at,
            finished_at,
            duration_ms
        )
        VALUES (
            %s,
            %s,
            'UPLOAD',
            %s,
            %s,
            %s,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            0
        )
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                invoice_id,
                user_id,
                status,
                message,
                Jsonb(details),
            ),
        )


def list_invoices(
    connection: Connection,
    page: int,
    page_size: int,
    search: str | None,
    status_filter: str | None,
    provider_id: int | None,
) -> tuple[list[dict[str, Any]], int]:
    conditions: list[str] = []
    parameters: list[Any] = []

    if search:
        search_value = f"%{search.strip()}%"

        conditions.append(
            """
            (
                COALESCE(invoice.invoice_number, '') ILIKE %s
                OR invoice.original_file_name ILIKE %s
                OR COALESCE(provider.name, '') ILIKE %s
                OR COALESCE(invoice.detected_nit, '') ILIKE %s
            )
            """
        )

        parameters.extend(
            [
                search_value,
                search_value,
                search_value,
                search_value,
            ]
        )

    if status_filter:
        conditions.append(
            "invoice.status::TEXT = %s"
        )
        parameters.append(status_filter)

    if provider_id is not None:
        conditions.append(
            "invoice.provider_id = %s"
        )
        parameters.append(provider_id)

    where_clause = ""

    if conditions:
        where_clause = (
            "WHERE " + " AND ".join(conditions)
        )

    count_query = f"""
        SELECT COUNT(*) AS total
        FROM invoices invoice
        LEFT JOIN providers provider
            ON provider.id = invoice.provider_id
        {where_clause}
    """

    with connection.cursor() as cursor:
        cursor.execute(
            count_query,
            parameters,
        )
        total = int(cursor.fetchone()["total"])

    offset = (page - 1) * page_size

    list_query = f"""
        SELECT {INVOICE_COLUMNS}
        FROM invoices invoice
        LEFT JOIN providers provider
            ON provider.id = invoice.provider_id
        LEFT JOIN invoice_categories category
            ON category.id = invoice.category_id
        {where_clause}
        ORDER BY invoice.created_at DESC, invoice.id DESC
        LIMIT %s
        OFFSET %s
    """

    list_parameters = [
        *parameters,
        page_size,
        offset,
    ]

    with connection.cursor() as cursor:
        cursor.execute(
            list_query,
            list_parameters,
        )
        invoices = cursor.fetchall()

    return invoices, total
