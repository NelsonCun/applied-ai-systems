from datetime import date
from decimal import Decimal
from typing import Any

from app.core.nit import (
    normalize_nit,
    validate_nit_format,
)


class InvoiceReviewValidationError(
    ValueError
):
    pass


def validate_invoice_review(
    data: dict[str, Any],
    provider: dict[str, Any],
) -> dict[str, Any]:
    invoice_number = (
        data["invoice_number"].strip()
    )

    if not invoice_number:
        raise InvoiceReviewValidationError(
            "El número de factura es obligatorio"
        )

    if len(invoice_number) > 100:
        raise InvoiceReviewValidationError(
            "El número de factura supera los 100 caracteres"
        )

    if data["invoice_date"] > date.today():
        raise InvoiceReviewValidationError(
            "La fecha de la factura no puede estar en el futuro"
        )

    nit = normalize_nit(data["nit"])

    if not validate_nit_format(nit):
        raise InvoiceReviewValidationError(
            "El formato del NIT no es válido"
        )

    provider_nit = normalize_nit(
        provider["nit"]
    )

    if nit != provider_nit:
        raise InvoiceReviewValidationError(
            "El NIT no coincide con el proveedor seleccionado"
        )

    subtotal = Decimal(data["subtotal"])
    tax = Decimal(data["tax"])
    total = Decimal(data["total"])

    if subtotal < 0 or tax < 0 or total < 0:
        raise InvoiceReviewValidationError(
            "Los valores monetarios no pueden ser negativos"
        )

    difference = abs(
        subtotal + tax - total
    )

    if difference > Decimal("0.10"):
        raise InvoiceReviewValidationError(
            "El subtotal más los impuestos no coincide con el total"
        )

    currency = data["currency"].strip().upper()

    if len(currency) != 3:
        raise InvoiceReviewValidationError(
            "La moneda debe utilizar un código de tres letras"
        )

    return {
        **data,
        "invoice_number": invoice_number,
        "nit": nit,
        "currency": currency,
        "provider_name": provider["name"],
        "category_id": (
            data["category_id"]
            or provider["category_id"]
        ),
    }
