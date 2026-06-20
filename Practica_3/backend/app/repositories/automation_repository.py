from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb


AUTOMATION_COLUMNS = """
    id,
    invoice_id,
    triggered_by,
    automation_type,
    status::TEXT AS status,
    target_url,
    result,
    evidence_path,
    error_message,
    started_at,
    finished_at,
    created_at
"""


def create_rpa_run(
    connection: Connection,
    invoice_id: int,
    triggered_by: int,
    target_url: str,
) -> dict[str, Any]:
    query = """
        INSERT INTO automation_runs (
            invoice_id,
            triggered_by,
            automation_type,
            status,
            target_url
        )
        VALUES (
            %s,
            %s,
            'REGISTER_INVOICE',
            'PENDING',
            %s
        )
        RETURNING id
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                invoice_id,
                triggered_by,
                target_url,
            ),
        )

        run_id = int(
            cursor.fetchone()["id"]
        )

    connection.commit()

    result = find_rpa_run_by_id(
        connection,
        run_id,
    )

    if result is None:
        raise RuntimeError(
            "No fue posible recuperar la automatización"
        )

    return result


def find_rpa_run_by_id(
    connection: Connection,
    run_id: int,
) -> dict[str, Any] | None:
    query = f"""
        SELECT {AUTOMATION_COLUMNS}
        FROM automation_runs
        WHERE id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (run_id,))
        return cursor.fetchone()


def get_rpa_payload(
    connection: Connection,
    run_id: int,
) -> dict[str, Any] | None:
    query = """
        SELECT
            run.id AS run_id,
            run.status::TEXT AS run_status,
            run.target_url,

            invoice.id AS invoice_id,
            invoice.invoice_number,
            invoice.invoice_date,
            invoice.subtotal,
            invoice.tax,
            invoice.total,
            invoice.currency,
            invoice.status::TEXT AS invoice_status,

            COALESCE(
                provider.name,
                invoice.detected_provider_name
            ) AS provider_name,

            COALESCE(
                provider.nit::TEXT,
                invoice.detected_nit
            ) AS nit

        FROM automation_runs run

        INNER JOIN invoices invoice
            ON invoice.id = run.invoice_id

        LEFT JOIN providers provider
            ON provider.id = invoice.provider_id

        WHERE run.id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (run_id,))
        return cursor.fetchone()


def list_rpa_runs(
    connection: Connection,
    page: int,
    page_size: int,
) -> tuple[list[dict[str, Any]], int]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM automation_runs
            WHERE automation_type = 'REGISTER_INVOICE'
            """
        )

        total = int(
            cursor.fetchone()["total"]
        )

    query = f"""
        SELECT {AUTOMATION_COLUMNS}
        FROM automation_runs
        WHERE automation_type = 'REGISTER_INVOICE'
        ORDER BY created_at DESC, id DESC
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


def mark_rpa_running(
    connection: Connection,
    run_id: int,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE automation_runs
            SET
                status = 'RUNNING',
                started_at = CURRENT_TIMESTAMP,
                error_message = NULL
            WHERE id = %s
            """,
            (run_id,),
        )

    connection.commit()


def mark_rpa_success(
    connection: Connection,
    run_id: int,
    result: dict[str, Any],
    evidence_path: str,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE automation_runs
            SET
                status = 'SUCCESS',
                result = %s,
                evidence_path = %s,
                finished_at = CURRENT_TIMESTAMP,
                error_message = NULL
            WHERE id = %s
            """,
            (
                Jsonb(result),
                evidence_path,
                run_id,
            ),
        )

    connection.commit()


def mark_rpa_error(
    connection: Connection,
    run_id: int,
    error_message: str,
    evidence_path: str | None,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE automation_runs
            SET
                status = 'ERROR',
                error_message = %s,
                evidence_path = %s,
                finished_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                error_message[:2000],
                evidence_path,
                run_id,
            ),
        )

    connection.commit()
