from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class ReportEmailRequest(BaseModel):
    recipient: EmailStr

    subject: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    message: str | None = Field(
        default=None,
        min_length=3,
        max_length=5000,
    )


class EmailLogResponse(BaseModel):
    id: int

    report_id: int
    report_type: str | None
    report_format: str | None
    report_file_name: str | None

    requested_by: int | None
    requested_by_name: str | None

    recipient_email: EmailStr
    subject: str
    body: str

    attachment_name: str | None

    status: str
    smtp_message_id: str | None
    error_message: str | None

    started_at: datetime | None
    sent_at: datetime | None

    created_at: datetime
    updated_at: datetime


class EmailQueuedResponse(BaseModel):
    message: str
    task_id: str
    email: EmailLogResponse


class EmailListResponse(BaseModel):
    items: list[EmailLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
