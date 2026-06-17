from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb


def get_invoice_for_processing(
    connection: Connection,
    invoice_id: int,
) -> dict[str, Any] | None:
    query = """
        SELECT
            invoice.id,
            invoice.file_path,
            invoice.mime_type,
            invoice.status::TEXT AS status,
            invoice.provider_id,
            invoice.category_id,
            provider.name AS provider_name,
            provider.nit::TEXT AS provider_nit
        FROM invoices invoice
        LEFT JOIN providers provider
            ON provider.id = invoice.provider_id
        WHERE invoice.id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (invoice_id,),
        )
        return cursor.fetchone()


def mark_invoice_processing(
    connection: Connection,
    invoice_id: int,
) -> None:
    query = """
        UPDATE invoices
        SET
            status = 'PROCESSING',
            attempt_count = attempt_count + 1,
            last_error = NULL
        WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (invoice_id,),
        )


def find_provider_by_nit(
    connection: Connection,
    nit: str,
) -> dict[str, Any] | None:
    query = """
        SELECT
            id,
            name,
            nit::TEXT AS nit,
            category_id
        FROM providers
        WHERE nit = %s
          AND is_active = TRUE
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (nit,))
        return cursor.fetchone()


def list_provider_candidates(
    connection: Connection,
) -> list[dict[str, Any]]:
    query = """
        SELECT
            id,
            name,
            nit::TEXT AS nit,
            category_id
        FROM providers
        WHERE is_active = TRUE
        ORDER BY name
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def insert_processing_log(
    connection: Connection,
    invoice_id: int,
    stage: str,
    status: str,
    message: str,
    details: dict[str, Any],
    duration_ms: int | None = None,
) -> None:
    query = """
        INSERT INTO processing_logs (
            invoice_id,
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
            %s::processing_stage,
            %s::execution_status,
            %s,
            %s,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            %s
        )
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                invoice_id,
                stage,
                status,
                message,
                Jsonb(details),
                duration_ms,
            ),
        )


def complete_invoice_processing(
    connection: Connection,
    invoice_id: int,
    data: dict[str, Any],
) -> None:
    query = """
        UPDATE invoices
        SET
            invoice_number = %(invoice_number)s,
            invoice_date = %(invoice_date)s,
            provider_id = %(provider_id)s,
            category_id = %(category_id)s,
            detected_provider_name = %(detected_provider_name)s,
            detected_nit = %(detected_nit)s,
            subtotal = %(subtotal)s,
            tax = %(tax)s,
            total = %(total)s,
            currency = %(currency)s,
            processed_file_path = %(processed_file_path)s,
            ocr_text = %(ocr_text)s,
            ocr_confidence = %(ocr_confidence)s,
            extracted_data = %(extracted_data)s,
            validation_errors = %(validation_errors)s,
            status = %(status)s::invoice_status,
            processed_at = CURRENT_TIMESTAMP,
            last_error = NULL
        WHERE id = %(invoice_id)s
    """

    parameters = {
        **data,
        "invoice_id": invoice_id,
        "extracted_data": Jsonb(
            data["extracted_data"]
        ),
        "validation_errors": Jsonb(
            data["validation_errors"]
        ),
    }

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            parameters,
        )


def fail_invoice_processing(
    connection: Connection,
    invoice_id: int,
    error_message: str,
) -> None:
    query = """
        UPDATE invoices
        SET
            status = 'ERROR',
            last_error = %s,
            processed_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                error_message[:2000],
                invoice_id,
            ),
        )
