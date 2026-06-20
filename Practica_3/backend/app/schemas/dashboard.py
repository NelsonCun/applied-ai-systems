from decimal import Decimal

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_invoices: int
    pending_invoices: int
    processing_invoices: int
    processed_invoices: int
    rejected_invoices: int
    error_invoices: int
    duplicate_invoices: int
    processed_total: Decimal
    processed_tax: Decimal
    average_ocr_confidence: Decimal


class StatusMetric(BaseModel):
    status: str
    invoice_count: int
    total_amount: Decimal


class ProviderMetric(BaseModel):
    provider_id: int | None
    provider_name: str
    invoice_count: int
    processed_count: int
    total_amount: Decimal
    average_confidence: Decimal


class MonthlyMetric(BaseModel):
    month: str
    invoice_count: int
    processed_count: int
    total_amount: Decimal


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    by_status: list[StatusMetric]
    by_provider: list[ProviderMetric]
    monthly: list[MonthlyMetric]
