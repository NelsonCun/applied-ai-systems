import mimetypes
import smtplib
from email.message import EmailMessage
from email.utils import (
    formataddr,
    formatdate,
    make_msgid,
)
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.core.config import settings
from app.repositories.email_repository import (
    get_email_delivery_payload,
    mark_email_error,
    mark_email_running,
    mark_email_success,
)


def send_report_email(
    email_id: int,
) -> dict[str, Any]:
    connection = psycopg.connect(
        settings.database_url,
        row_factory=dict_row,
    )

    try:
        payload = get_email_delivery_payload(
            connection,
            email_id,
        )

        if payload is None:
            raise ValueError(
                "El registro de correo no existe"
            )

        if payload["report_status"] != "SUCCESS":
            raise ValueError(
                "El reporte todavía no está disponible"
            )

        if not payload["file_path"]:
            raise ValueError(
                "El reporte no tiene un archivo asociado"
            )

        file_path = Path(
            payload["file_path"]
        )

        if not file_path.is_file():
            raise FileNotFoundError(
                "El archivo físico del reporte no existe"
            )

        mark_email_running(
            connection,
            email_id,
        )

        message_id = make_msgid(
            domain="smartinvoice.com"
        )

        message = EmailMessage()

        message["From"] = formataddr(
            (
                settings.smtp_from_name,
                settings.smtp_from_email,
            )
        )

        message["To"] = payload[
            "recipient_email"
        ]

        message["Subject"] = payload[
            "subject"
        ]

        message["Date"] = formatdate(
            localtime=False
        )

        message["Message-ID"] = message_id

        message.set_content(
            payload["body"]
        )

        mime_type, _ = mimetypes.guess_type(
            file_path.name
        )

        if mime_type is None:
            main_type = "application"
            sub_type = "octet-stream"
        else:
            main_type, sub_type = (
                mime_type.split("/", 1)
            )

        with file_path.open("rb") as attachment:
            message.add_attachment(
                attachment.read(),
                maintype=main_type,
                subtype=sub_type,
                filename=(
                    payload["attachment_name"]
                    or file_path.name
                ),
            )

        with smtplib.SMTP(
            host=settings.smtp_host,
            port=settings.smtp_port,
            timeout=(
                settings.smtp_timeout_seconds
            ),
        ) as smtp:
            smtp.ehlo()

            if settings.smtp_use_tls:
                smtp.starttls()
                smtp.ehlo()

            if settings.smtp_username:
                smtp.login(
                    settings.smtp_username,
                    settings.smtp_password,
                )

            refused_recipients = (
                smtp.send_message(message)
            )

        if refused_recipients:
            raise RuntimeError(
                "El servidor SMTP rechazó al destinatario"
            )

        mark_email_success(
            connection=connection,
            email_id=email_id,
            smtp_message_id=message_id,
        )

        return {
            "email_id": email_id,
            "report_id": payload["report_id"],
            "recipient": payload[
                "recipient_email"
            ],
            "attachment": file_path.name,
            "smtp_message_id": message_id,
            "status": "SUCCESS",
        }

    except Exception as error:
        connection.rollback()

        try:
            mark_email_error(
                connection,
                email_id,
                str(error),
            )
        except Exception:
            connection.rollback()

        raise

    finally:
        connection.close()
