from app.rpa.invoice_registration import (
    execute_invoice_registration,
)
from app.tasks.celery_app import celery_app


@celery_app.task(
    name="smartinvoice.register_invoice_rpa",
)
def register_invoice_rpa_task(
    run_id: int,
) -> dict:
    return execute_invoice_registration(
        run_id
    )
