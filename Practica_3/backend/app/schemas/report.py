from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


ReportFormat = Literal[
    "PDF",
    "XLSX",
    "CSV",
]

ReportType = Literal[
    "INVOICE_DETAIL",
    "ADMINISTRATIVE",
    "SUMMARY",
    "ERRORS",
]


class ReportGenerateRequest(BaseModel):
    report_type: ReportType = "ADMINISTRATIVE"
    format: ReportFormat

    date_from: date | None = None
    date_to: date | None = None

    provider_id: int | None = Field(
        default=None,
        gt=0,
    )

    status: str | None = None

    @model_validator(mode="after")
    def validate_date_range(
        self,
    ) -> "ReportGenerateRequest":
        if (
            self.date_from is not None
            and self.date_to is not None
            and self.date_from > self.date_to
        ):
            raise ValueError(
                "La fecha inicial no puede ser mayor "
                "que la fecha final"
            )

        return self


class ReportResponse(BaseModel):
    id: int
    report_type: str
    format: str
    status: str

    file_name: str | None
    filters: dict

    generated_by: int | None
    generated_by_name: str | None

    error_message: str | None

    created_at: datetime
    generated_at: datetime | None


class ReportQueuedResponse(BaseModel):
    message: str
    task_id: str
    report: ReportResponse


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
