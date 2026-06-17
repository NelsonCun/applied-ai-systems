from datetime import datetime, timezone

from app.tasks.celery_app import celery_app


@celery_app.task(name="smartinvoice.health")
def health_task() -> dict:
    return {
        "status": "worker available",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
