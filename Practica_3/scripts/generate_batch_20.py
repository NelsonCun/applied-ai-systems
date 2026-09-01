#!/usr/bin/env python3
"""
Genera un lote determinista de 20 facturas para validar SmartInvoice.

Requisitos del proyecto:
- PyMuPDF (fitz)
- numpy
- Pillow
- reportlab

Uso:
    python3 scripts/generate_batch_20.py \
        --output samples/batch_20 \
        --batch-code L20A \
        --clean
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from pathlib import Path

import fitz
import numpy as np
from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
)
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


PROVIDERS = [
    {
        "name": "Demo Ficticio Tecnologia Alfa",
        "nit": "9000001-9",
        "description": (
            "Computadoras, periféricos y accesorios tecnológicos"
        ),
        "category": "Tecnología",
    },
    {
        "name": "Demo Ficticio Oficina Beta",
        "nit": "9000002-9",
        "description": (
            "Papelería, mobiliario y suministros de oficina"
        ),
        "category": "Oficina",
    },
    {
        "name": "Demo Ficticio Servicios Gamma",
        "nit": "9000003-9",
        "description": (
            "Servicios profesionales de soporte y mantenimiento"
        ),
        "category": "Servicios",
    },
    {
        "name": "Demo Ficticio Comercial Delta",
        "nit": "9000004-9",
        "description": (
            "Alimentos y suministros para reunión empresarial"
        ),
        "category": "Alimentos",
    },
    {
        "name": "Demo Ficticio Suministros Epsilon",
        "nit": "9000005-9",
        "description": (
            "Servicio de transporte, logística y mensajería"
        ),
        "category": "Transporte",
    },
]


FORMAT_SEQUENCE = [
    "pdf",
    "png",
    "jpg",
    "pdf",
    "png",
    "jpg",
    "pdf",
    "png",
    "jpg",
    "pdf",
    "png",
    "jpg",
    "pdf",
    "png",
    "jpg",
    "pdf",
    "png",
    "jpg",
    "pdf",
    "png",
]


PROFILE_SEQUENCE = [
    "clean",
    "clean",
    "mild_noise",
    "clean",
    "low_contrast",
    "slight_rotation",
    "clean",
    "mild_noise",
    "low_contrast",
    "clean",
    "slight_rotation",
    "mild_noise",
    "clean",
    "low_contrast",
    "slight_rotation",
    "clean",
    "mild_noise",
    "low_contrast",
    "clean",
    "slight_rotation",
]


def money(value: Decimal) -> str:
    return str(
        value.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    )


def create_invoice_definitions(
    batch_code: str,
) -> list[dict]:
    invoices: list[dict] = []
    start_date = date(2026, 5, 1)

    for index in range(20):
        provider = PROVIDERS[
            index % len(PROVIDERS)
        ]

        subtotal = (
            Decimal("185.00")
            + Decimal(index) * Decimal("73.25")
            + Decimal(index % 4) * Decimal("19.50")
        ).quantize(Decimal("0.01"))

        tax = (
            subtotal * Decimal("0.12")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        total = subtotal + tax
        file_format = FORMAT_SEQUENCE[index]
        profile = PROFILE_SEQUENCE[index]
        invoice_number = (
            f"{batch_code}-2026-{index + 1:03d}"
        )

        provider_slug = (
            provider["category"]
            .lower()
            .replace("í", "i")
            .replace("ó", "o")
            .replace("á", "a")
            .replace("é", "e")
            .replace("ú", "u")
            .replace(" ", "_")
        )

        invoices.append(
            {
                "file": (
                    f"{batch_code.lower()}_"
                    f"{index + 1:02d}_"
                    f"{provider_slug}."
                    f"{file_format}"
                ),
                "provider": provider["name"],
                "nit": provider["nit"],
                "number": invoice_number,
                "date": (
                    start_date
                    + timedelta(days=index)
                ).strftime("%d/%m/%Y"),
                "subtotal": money(subtotal),
                "tax": money(tax),
                "total": money(total),
                "format": file_format,
                "profile": profile,
                "description": provider[
                    "description"
                ],
                "expected_category": provider[
                    "category"
                ],
            }
        )

    return invoices


def create_pdf_bytes(
    invoice: dict,
) -> bytes:
    buffer = BytesIO()

    document = canvas.Canvas(
        buffer,
        pagesize=A4,
    )

    width, height = A4

    document.setTitle(
        f"Factura {invoice['number']}"
    )

    document.setFont(
        "Helvetica-Bold",
        21,
    )
    document.drawString(
        62,
        height - 70,
        invoice["provider"],
    )

    document.setFont(
        "Helvetica-Bold",
        15,
    )
    document.drawString(
        62,
        height - 108,
        "FACTURA",
    )

    document.setFont(
        "Helvetica",
        13,
    )

    rows = [
        f"PROVEEDOR: {invoice['provider']}",
        f"NIT: {invoice['nit']}",
        f"FACTURA No: {invoice['number']}",
        f"FECHA: {invoice['date']}",
        "",
        f"DESCRIPCION: {invoice['description']}",
        "CANTIDAD: 1",
        "",
        f"SUBTOTAL: Q {invoice['subtotal']}",
        f"IVA: Q {invoice['tax']}",
        f"TOTAL: Q {invoice['total']}",
    ]

    y = height - 145

    for row in rows:
        document.drawString(
            70,
            y,
            row,
        )
        y -= 31

    document.setLineWidth(1)
    document.rect(
        52,
        y - 12,
        width - 104,
        height - y - 92,
    )

    document.setFont(
        "Helvetica",
        9,
    )
    document.drawString(
        62,
        46,
        (
            "Documento generado para pruebas "
            "controladas de SmartInvoice."
        ),
    )

    document.save()

    return buffer.getvalue()


def pdf_to_image(
    pdf_bytes: bytes,
) -> Image.Image:
    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf",
    )

    try:
        page = document.load_page(0)

        pixmap = page.get_pixmap(
            dpi=220,
            alpha=False,
        )

        return Image.open(
            BytesIO(
                pixmap.tobytes("png")
            )
        ).convert("RGB")

    finally:
        document.close()


def apply_profile(
    image: Image.Image,
    profile: str,
    seed: int,
) -> Image.Image:
    result = image.copy()

    if profile == "clean":
        return result

    if profile == "mild_noise":
        array = np.asarray(
            result
        ).astype(np.int16)

        random = np.random.default_rng(
            seed
        )

        noise = random.normal(
            0,
            2.4,
            array.shape,
        )

        noisy = np.clip(
            array + noise,
            0,
            255,
        ).astype(np.uint8)

        return Image.fromarray(noisy)

    if profile == "low_contrast":
        result = ImageEnhance.Contrast(
            result
        ).enhance(0.88)

        return ImageEnhance.Brightness(
            result
        ).enhance(1.03)

    if profile == "slight_rotation":
        angle = (
            0.55
            if seed % 2 == 0
            else -0.55
        )

        result = result.rotate(
            angle,
            expand=True,
            fillcolor="white",
        )

        return result.filter(
            ImageFilter.GaussianBlur(
                radius=0.15
            )
        )

    raise ValueError(
        f"Perfil desconocido: {profile}"
    )


def write_manifest(
    output_directory: Path,
    invoices: list[dict],
    batch_code: str,
) -> None:
    manifest = {
        "batch_code": batch_code,
        "count": len(invoices),
        "expected_terminal_status": (
            "PROCESSED"
        ),
        "invoices": invoices,
    }

    (
        output_directory
        / "expected_results.json"
    ).write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    with (
        output_directory
        / "expected_results.csv"
    ).open(
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "file",
                "provider",
                "nit",
                "number",
                "date",
                "subtotal",
                "tax",
                "total",
                "format",
                "profile",
                "expected_category",
            ],
            lineterminator="\n")

        writer.writeheader()

        for invoice in invoices:
            writer.writerow(
                {
                    key: invoice[key]
                    for key in writer.fieldnames
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        default="samples/batch_20",
        help=(
            "Directorio donde se generará "
            "el lote."
        ),
    )

    parser.add_argument(
        "--batch-code",
        default="L20A",
        help=(
            "Prefijo alfanumérico para números "
            "de factura y nombres de archivo."
        ),
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help=(
            "Elimina el directorio de salida "
            "antes de generar."
        ),
    )

    args = parser.parse_args()

    output_directory = Path(
        args.output
    )

    if (
        args.clean
        and output_directory.exists()
    ):
        shutil.rmtree(
            output_directory
        )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    invoices = create_invoice_definitions(
        args.batch_code.upper()
    )

    for index, invoice in enumerate(
        invoices,
        start=1,
    ):
        pdf_bytes = create_pdf_bytes(
            invoice
        )

        output_path = (
            output_directory
            / invoice["file"]
        )

        if invoice["format"] == "pdf":
            output_path.write_bytes(
                pdf_bytes
            )

        else:
            image = pdf_to_image(
                pdf_bytes
            )

            image = apply_profile(
                image=image,
                profile=invoice[
                    "profile"
                ],
                seed=202600 + index,
            )

            if invoice["format"] == "png":
                image.save(
                    output_path,
                    format="PNG",
                    optimize=True,
                )

            else:
                image.save(
                    output_path,
                    format="JPEG",
                    quality=95,
                    subsampling=0,
                )

        print(
            f"[{index:02d}/20] "
            f"{output_path} "
            f"({invoice['profile']})"
        )

    write_manifest(
        output_directory=output_directory,
        invoices=invoices,
        batch_code=args.batch_code.upper(),
    )

    generated_documents = [
        path
        for path in output_directory.iterdir()
        if path.suffix.lower()
        in {".pdf", ".png", ".jpg", ".jpeg"}
    ]

    print()
    print(
        "Facturas generadas:",
        len(generated_documents),
    )
    print(
        "Manifest:",
        output_directory
        / "expected_results.json",
    )
    print(
        "CSV esperado:",
        output_directory
        / "expected_results.csv",
    )


if __name__ == "__main__":
    main()
