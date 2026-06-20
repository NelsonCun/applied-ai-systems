from typing import Any

from psycopg import Connection


EMAIL_COLUMNS = """
    email_log.id,

    email_log.report_id,
    report.report_type::TEXT AS report_type,
    report.format::TEXT AS report_format,
    report.file_name AS report_file_name,

    email_log.requested_by,
    users.full_name AS requested_by_name,

    email_log.recipient_email::TEXT
        AS recipient_email,

    email_log.subject,
    email_log.body,
    email_log.attachment_name,

    email_log.status,
    email_log.smtp_message_id,
    email_log.error_message,

    email_log.started_at,
    email_log.sent_at,

    email_log.created_at,
    email_log.updated_at
"""


def create_email_log(
    connection: Connection,
    report_id: int,
    requested_by: int,
    recipient_email: str,
    subject: str,
    body: str,
    attachment_name: str | None,
) -> dict[str, Any]:
    query = """
        INSERT INTO email_logs (
            report_id,
            requested_by,
            recipient_email,
            subject,
            body,
            attachment_name,
            status
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            'PENDING'
        )
        RETURNING id
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                report_id,
                requested_by,
                recipient_email,
                subject,
                body,
                attachment_name,
            ),
        )

        email_id = int(
            cursor.fetchone()["id"]
        )

    connection.commit()

    email_log = find_email_log_by_id(
        connection,
        email_id,
    )

    if email_log is None:
        raise RuntimeError(
            "No fue posible recuperar el registro de correo"
        )

    return email_log


def find_email_log_by_id(
    connection: Connection,
    email_id: int,
) -> dict[str, Any] | None:
    query = f"""
        SELECT {EMAIL_COLUMNS}
        FROM email_logs email_log

        INNER JOIN reports report
            ON report.id = email_log.report_id

        LEFT JOIN users
            ON users.id = email_log.requested_by

        WHERE email_log.id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (email_id,))
        return cursor.fetchone()


def get_email_delivery_payload(
    connection: Connection,
    email_id: int,
) -> dict[str, Any] | None:
    query = """
        SELECT
            email_log.id,
            email_log.report_id,
            email_log.recipient_email::TEXT
                AS recipient_email,
            email_log.subject,
            email_log.body,
            email_log.attachment_name,
            email_log.status,

            report.report_type::TEXT
                AS report_type,
            report.format::TEXT
                AS report_format,
            report.status::TEXT
                AS report_status,
            report.file_name,
            report.file_path

        FROM email_logs email_log

        INNER JOIN reports report
            ON report.id = email_log.report_id

        WHERE email_log.id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (email_id,))
        return cursor.fetchone()


def list_email_logs(
    connection: Connection,
    page: int,
    page_size: int,
) -> tuple[list[dict[str, Any]], int]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM email_logs
            """
        )

        total = int(
            cursor.fetchone()["total"]
        )

    offset = (page - 1) * page_size

    query = f"""
        SELECT {EMAIL_COLUMNS}
        FROM email_logs email_log

        INNER JOIN reports report
            ON report.id = email_log.report_id

        LEFT JOIN users
            ON users.id = email_log.requested_by

        ORDER BY
            email_log.created_at DESC,
            email_log.id DESC

        LIMIT %s
        OFFSET %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (page_size, offset),
        )

        items = cursor.fetchall()

    return items, total


def mark_email_running(
    connection: Connection,
    email_id: int,
) -> None:
    query = """
        UPDATE email_logs
        SET
            status = 'RUNNING',
            started_at = CURRENT_TIMESTAMP,
            error_message = NULL
        WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (email_id,))

    connection.commit()


def mark_email_success(
    connection: Connection,
    email_id: int,
    smtp_message_id: str,
) -> None:
    query = """
        UPDATE email_logs
        SET
            status = 'SUCCESS',
            smtp_message_id = %s,
            sent_at = CURRENT_TIMESTAMP,
            error_message = NULL
        WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                smtp_message_id,
                email_id,
            ),
        )

    connection.commit()


def mark_email_error(
    connection: Connection,
    email_id: int,
    error_message: str,
) -> None:
    query = """
        UPDATE email_logs
        SET
            status = 'ERROR',
            error_message = %s
        WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                error_message[:2000],
                email_id,
            ),
        )

    connection.commit()
