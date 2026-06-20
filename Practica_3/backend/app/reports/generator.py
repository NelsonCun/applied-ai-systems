import csv
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from psycopg.rows import dict_row
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import settings
from app.repositories.report_repository import (
    get_report_internal,
    get_report_rows,
    mark_report_error,
    mark_report_running,
    mark_report_success,
)


HEADERS = [
    "ID",
    "Número",
    "Fecha",
    "Proveedor",
    "NIT",
    "Categoría",
    "Subtotal",
    "IVA",
    "Total",
    "Moneda",
    "Confianza OCR",
    "Estado",
    "Archivo",
]


def display_value(
    value: Any,
) -> str:
    if value is None:
        return ""

    if isinstance(value, Decimal):
        return f"{value:.2f}"

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return str(value)


def row_values(
    row: dict[str, Any],
) -> list[str]:
    return [
        display_value(row["id"]),
        display_value(row["invoice_number"]),
        display_value(row["invoice_date"]),
        display_value(row["provider_name"]),
        display_value(row["nit"]),
        display_value(row["category_name"]),
        display_value(row["subtotal"]),
        display_value(row["tax"]),
        display_value(row["total"]),
        display_value(row["currency"]),
        display_value(row["ocr_confidence"]),
        display_value(row["status"]),
        display_value(row["original_file_name"]),
    ]


def generate_csv(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as output:
        writer = csv.writer(output)
        writer.writerow(HEADERS)

        for row in rows:
            writer.writerow(row_values(row))


def generate_xlsx(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Facturas"

    sheet.append(HEADERS)

    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(
            horizontal="center"
        )

    for row in rows:
        sheet.append(row_values(row))

    widths = [
        10,
        20,
        14,
        32,
        18,
        20,
        14,
        14,
        14,
        10,
        16,
        16,
        32,
    ]

    for index, width in enumerate(
        widths,
        start=1,
    ):
        column = sheet.cell(
            row=1,
            column=index,
        ).column_letter

        sheet.column_dimensions[
            column
        ].width = width

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = (
        sheet.dimensions
    )

    workbook.save(path)


def generate_pdf(
    path: Path,
    rows: list[dict[str, Any]],
    filters: dict[str, Any],
) -> None:
    document = SimpleDocTemplate(
        str(path),
        pagesize=landscape(A4),
        rightMargin=0.8 * cm,
        leftMargin=0.8 * cm,
        topMargin=0.8 * cm,
        bottomMargin=0.8 * cm,
    )

    styles = getSampleStyleSheet()

    elements = [
        Paragraph(
            "SmartInvoice - Reporte administrativo",
            styles["Title"],
        ),
        Paragraph(
            (
                "Generado: "
                + datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )
            ),
            styles["Normal"],
        ),
        Paragraph(
            (
                "Filtros: "
                + ", ".join(
                    f"{key}={value}"
                    for key, value
                    in filters.items()
                    if value is not None
                )
            )
            if any(
                value is not None
                for value in filters.values()
            )
            else "Filtros: ninguno",
            styles["Normal"],
        ),
        Spacer(1, 0.4 * cm),
    ]

    compact_headers = [
        "ID",
        "Número",
        "Fecha",
        "Proveedor",
        "NIT",
        "Subtotal",
        "IVA",
        "Total",
        "OCR",
        "Estado",
    ]

    table_data = [compact_headers]

    for row in rows:
        table_data.append(
            [
                display_value(row["id"]),
                display_value(
                    row["invoice_number"]
                ),
                display_value(
                    row["invoice_date"]
                ),
                display_value(
                    row["provider_name"]
                )[:32],
                display_value(row["nit"]),
                display_value(row["subtotal"]),
                display_value(row["tax"]),
                display_value(row["total"]),
                display_value(
                    row["ocr_confidence"]
                ),
                display_value(row["status"]),
            ]
        )

    if not rows:
        table_data.append(
            [
                "Sin registros",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            1.0 * cm,
            2.8 * cm,
            2.2 * cm,
            5.1 * cm,
            2.5 * cm,
            2.2 * cm,
            1.9 * cm,
            2.2 * cm,
            1.7 * cm,
            2.3 * cm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#263238"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.25,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#ECEFF1"),
                    ],
                ),
            ]
        )
    )

    elements.append(table)
    document.build(elements)


def generate_report(
    report_id: int,
) -> dict[str, Any]:
    connection = psycopg.connect(
        settings.database_url,
        row_factory=dict_row,
    )

    try:
        report = get_report_internal(
            connection,
            report_id,
        )

        if report is None:
            raise ValueError(
                "El reporte no existe"
            )

        mark_report_running(
            connection,
            report_id,
        )

        rows = get_report_rows(
            connection=connection,
            filters=report["filters"],
            report_type=report["report_type"],
        )

        output_directory = Path(
            settings.reports_dir
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        extension = (
            report["format"].lower()
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        file_name = (
            f"smartinvoice_report_{report_id}_"
            f"{timestamp}.{extension}"
        )

        file_path = (
            output_directory / file_name
        )

        if report["format"] == "CSV":
            generate_csv(file_path, rows)

        elif report["format"] == "XLSX":
            generate_xlsx(file_path, rows)

        elif report["format"] == "PDF":
            generate_pdf(
                file_path,
                rows,
                report["filters"],
            )

        else:
            raise ValueError(
                "Formato de reporte no soportado"
            )

        mark_report_success(
            connection=connection,
            report_id=report_id,
            file_name=file_name,
            file_path=str(file_path),
        )

        return {
            "report_id": report_id,
            "status": "SUCCESS",
            "format": report["format"],
            "file_name": file_name,
            "record_count": len(rows),
        }

    except Exception as error:
        connection.rollback()

        try:
            mark_report_error(
                connection,
                report_id,
                str(error),
            )
        except Exception:
            connection.rollback()

        raise

    finally:
        connection.close()
