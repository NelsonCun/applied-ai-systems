from app.reports.generator import generate_report
from app.tasks.celery_app import celery_app


@celery_app.task(
    name="smartinvoice.generate_report",
)
def generate_report_task(
    report_id: int,
) -> dict:
    return generate_report(report_id)
