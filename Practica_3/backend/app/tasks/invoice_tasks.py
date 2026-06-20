import psycopg

from app.services.invoice_processing_service import (
    process_invoice,
)
from app.tasks.celery_app import celery_app


@celery_app.task(
    bind=True,
    name="smartinvoice.process_invoice",
    autoretry_for=(
        psycopg.OperationalError,
        ConnectionError,
        TimeoutError,
    ),
    retry_backoff=10,
    retry_jitter=True,
    retry_kwargs={
        "max_retries": 2,
    },
)
def process_invoice_task(
    self,
    invoice_id: int,
) -> dict:
    del self

    return process_invoice(
        invoice_id
    )
