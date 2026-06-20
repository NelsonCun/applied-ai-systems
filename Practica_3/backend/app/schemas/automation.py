from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AutomationRunResponse(BaseModel):
    id: int
    invoice_id: int | None
    triggered_by: int | None

    automation_type: str
    status: str

    target_url: str | None
    result: dict[str, Any]
    evidence_path: str | None
    error_message: str | None

    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class AutomationQueuedResponse(BaseModel):
    message: str
    task_id: str
    automation: AutomationRunResponse


class AutomationListResponse(BaseModel):
    items: list[AutomationRunResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
