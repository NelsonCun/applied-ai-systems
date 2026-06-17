import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from app.core.nit import (
    normalize_nit,
    validate_nit_format,
)


def normalize_ocr_text(
    text: str,
) -> str:
    normalized = (
        text.replace("\r", "\n")
        .replace("–", "-")
        .replace("—", "-")
        .replace("’", "'")
    )

    lines = [
        " ".join(line.split())
        for line in normalized.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)


def parse_decimal(
    raw_value: str,
) -> Decimal | None:
    cleaned = re.sub(
        r"[^0-9,.\-]",
        "",
        raw_value,
    )

    if not cleaned:
        return None

    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(".") > cleaned.rfind(","):
            cleaned = cleaned.replace(",", "")
        else:
            cleaned = (
                cleaned.replace(".", "")
                .replace(",", ".")
            )

    elif "," in cleaned:
        decimal_part = cleaned.rsplit(
            ",",
            1,
        )[-1]

        if len(decimal_part) == 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")

    elif "." in cleaned:
        decimal_part = cleaned.rsplit(
            ".",
            1,
        )[-1]

        if len(decimal_part) != 2:
            cleaned = cleaned.replace(".", "")

    try:
        return Decimal(cleaned).quantize(
            Decimal("0.01")
        )
    except InvalidOperation:
        return None


def extract_invoice_number(
    text: str,
) -> str | None:
    patterns = [
        (
            r"(?:FACTURA\s*(?:NO\.?|N[ÚU]MERO)?|"
            r"NO\.?\s*FACTURA)\s*[:#-]?\s*"
            r"([A-Z0-9][A-Z0-9\-]{2,30})"
        ),
        (
            r"(?:DOCUMENTO|SERIE)\s*[:#-]?\s*"
            r"([A-Z0-9][A-Z0-9\-]{2,30})"
        ),
    ]

    upper_text = text.upper()

    for pattern in patterns:
        match = re.search(
            pattern,
            upper_text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    return None


def extract_date(
    text: str,
) -> date | None:
    patterns = [
        (
            r"(?:FECHA(?:\s+DE\s+EMISI[ÓO]N)?)"
            r"\s*[:\-]?\s*"
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        ),
        (
            r"(?:FECHA(?:\s+DE\s+EMISI[ÓO]N)?)"
            r"\s*[:\-]?\s*"
            r"(\d{4}-\d{1,2}-\d{1,2})"
        ),
    ]

    date_formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%Y-%m-%d",
    ]

    upper_text = text.upper()

    for pattern in patterns:
        match = re.search(
            pattern,
            upper_text,
            re.IGNORECASE,
        )

        if not match:
            continue

        raw_date = match.group(1)

        for date_format in date_formats:
            try:
                return datetime.strptime(
                    raw_date,
                    date_format,
                ).date()
            except ValueError:
                continue

    return None


def extract_nit(
    text: str,
) -> str | None:
    match = re.search(
        r"\bNIT\s*[:#-]?\s*"
        r"(CF|C/F|[0-9]{1,9}-?[0-9Kk]?)\b",
        text,
        re.IGNORECASE,
    )

    if not match:
        return None

    nit = normalize_nit(
        match.group(1)
    )

    return nit


def extract_provider_name(
    text: str,
) -> str | None:
    match = re.search(
        r"(?:PROVEEDOR|EMISOR|RAZ[ÓO]N\s+SOCIAL)"
        r"\s*[:\-]\s*(.{3,180})",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return None


def extract_labeled_amount(
    text: str,
    labels: tuple[str, ...],
    excluded_labels: tuple[str, ...] = (),
) -> Decimal | None:
    lines = text.splitlines()

    for line in lines:
        upper_line = line.upper()

        if not any(
            label in upper_line
            for label in labels
        ):
            continue

        if any(
            label in upper_line
            for label in excluded_labels
        ):
            continue

        numeric_values = re.findall(
            r"(?:Q|GTQ|\$)?\s*"
            r"([0-9][0-9\s.,]*[0-9]|[0-9])",
            line,
            re.IGNORECASE,
        )

        if not numeric_values:
            continue

        value = parse_decimal(
            numeric_values[-1]
        )

        if value is not None:
            return value

    return None


def parse_invoice_text(
    raw_text: str,
) -> dict[str, Any]:
    text = normalize_ocr_text(raw_text)

    return {
        "invoice_number": extract_invoice_number(
            text
        ),
        "invoice_date": extract_date(text),
        "provider_name": extract_provider_name(
            text
        ),
        "nit": extract_nit(text),
        "subtotal": extract_labeled_amount(
            text,
            ("SUBTOTAL", "SUB TOTAL"),
        ),
        "tax": extract_labeled_amount(
            text,
            ("IVA", "IMPUESTO", "IMPUESTOS"),
        ),
        "total": extract_labeled_amount(
            text,
            ("TOTAL",),
            ("SUBTOTAL", "SUB TOTAL"),
        ),
        "currency": "GTQ",
        "normalized_text": text,
    }


def validate_extracted_data(
    data: dict[str, Any],
    confidence: float,
    minimum_confidence: float,
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    required_fields = {
        "invoice_number": "Número de factura",
        "invoice_date": "Fecha",
        "provider_name": "Proveedor",
        "nit": "NIT",
        "subtotal": "Subtotal",
        "tax": "Impuestos",
        "total": "Total",
    }

    for field, label in required_fields.items():
        if data.get(field) is None:
            errors.append(
                {
                    "field": field,
                    "message": (
                        f"No se pudo extraer: {label}"
                    ),
                }
            )

    nit = data.get("nit")

    if (
        nit is not None
        and not validate_nit_format(nit)
    ):
        errors.append(
            {
                "field": "nit",
                "message": "El formato del NIT no es válido",
            }
        )

    invoice_date = data.get(
        "invoice_date"
    )

    if (
        invoice_date is not None
        and invoice_date > date.today()
    ):
        errors.append(
            {
                "field": "invoice_date",
                "message": (
                    "La fecha de la factura está en el futuro"
                ),
            }
        )

    subtotal = data.get("subtotal")
    tax = data.get("tax")
    total = data.get("total")

    if (
        subtotal is not None
        and tax is not None
        and total is not None
    ):
        difference = abs(
            (subtotal + tax) - total
        )

        if difference > Decimal("0.10"):
            errors.append(
                {
                    "field": "total",
                    "message": (
                        "El subtotal más impuestos no coincide "
                        "con el total"
                    ),
                }
            )

    if confidence < minimum_confidence:
        errors.append(
            {
                "field": "ocr_confidence",
                "message": (
                    "La confianza OCR es inferior al mínimo "
                    f"permitido ({minimum_confidence}%)"
                ),
            }
        )

    return errors
