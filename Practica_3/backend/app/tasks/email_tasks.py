from app.services.email_service import (
    send_report_email,
)
from app.tasks.celery_app import celery_app


@celery_app.task(
    name="smartinvoice.send_report_email",
)
def send_report_email_task(
    email_id: int,
) -> dict:
    return send_report_email(
        email_id
    )
