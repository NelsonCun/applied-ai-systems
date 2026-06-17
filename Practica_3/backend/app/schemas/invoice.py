from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str | None
    invoice_date: date | None

    provider_id: int | None
    provider_name: str | None

    category_id: int | None
    category_name: str | None

    detected_provider_name: str | None
    detected_nit: str | None

    subtotal: Decimal | None
    tax: Decimal | None
    total: Decimal | None
    currency: str

    original_file_name: str
    file_path: str
    processed_file_path: str | None
    file_sha256: str
    mime_type: str
    file_size_bytes: int

    ocr_confidence: Decimal | None

    extracted_data: dict[str, Any]
    validation_errors: list[Any]

    status: str
    duplicate_of_invoice_id: int | None

    created_by: int
    created_at: datetime
    processed_at: datetime | None
    confirmed_at: datetime | None
    updated_at: datetime


class InvoiceUploadResponse(BaseModel):
    message: str
    is_duplicate: bool
    task_id: str | None = None
    invoice: InvoiceResponse


class BatchUploadError(BaseModel):
    file_name: str
    error: str


class BatchUploadResponse(BaseModel):
    received: int
    successful: int
    duplicates: int
    failed: int
    items: list[InvoiceUploadResponse]
    errors: list[BatchUploadError]


class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProcessingQueuedResponse(BaseModel):
    invoice_id: int
    task_id: str
    message: str
