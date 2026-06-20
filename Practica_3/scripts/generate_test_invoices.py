import argparse
from io import BytesIO
from pathlib import Path

import fitz
import numpy as np
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


INVOICES = [
    {
        "file": "factura_tecnologia.pdf",
        "provider": "Tecnologia Maya, S.A.",
        "nit": "1234567-8",
        "number": "FAC-2026-001",
        "date": "17/06/2026",
        "subtotal": "1000.00",
        "tax": "120.00",
        "total": "1120.00",
        "format": "pdf",
    },
    {
        "file": "factura_quetzal.png",
        "provider": "Distribuidora Quetzal, S.A.",
        "nit": "7654321-0",
        "number": "FAC-2026-002",
        "date": "16/06/2026",
        "subtotal": "500.00",
        "tax": "60.00",
        "total": "560.00",
        "format": "png",
    },
    {
        "file": "factura_servicios_ruido.jpg",
        "provider": "Servicios Chapines",
        "nit": "9876543-K",
        "number": "FAC-2026-003",
        "date": "15/06/2026",
        "subtotal": "750.00",
        "tax": "90.00",
        "total": "840.00",
        "format": "jpg",
    },
]


def create_pdf_bytes(
    invoice: dict,
) -> bytes:
    buffer = BytesIO()

    document = canvas.Canvas(
        buffer,
        pagesize=A4,
    )

    width, height = A4

    document.setFont(
        "Helvetica-Bold",
        22,
    )
    document.drawString(
        70,
        height - 80,
        invoice["provider"],
    )

    document.setFont(
        "Helvetica",
        14,
    )

    rows = [
        f"PROVEEDOR: {invoice['provider']}",
        f"NIT: {invoice['nit']}",
        f"FACTURA No: {invoice['number']}",
        f"FECHA: {invoice['date']}",
        "",
        "DESCRIPCION: Productos o servicios facturados",
        "CANTIDAD: 1",
        "",
        f"SUBTOTAL: Q {invoice['subtotal']}",
        f"IVA: Q {invoice['tax']}",
        f"TOTAL: Q {invoice['total']}",
    ]

    y = height - 140

    for row in rows:
        document.drawString(
            70,
            y,
            row,
        )
        y -= 32

    document.rect(
        55,
        y - 20,
        width - 110,
        height - y - 100,
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

    page = document.load_page(0)

    pixmap = page.get_pixmap(
        dpi=220,
        alpha=False,
    )

    image = Image.open(
        BytesIO(
            pixmap.tobytes("png")
        )
    ).convert("RGB")

    document.close()

    return image


def add_mild_noise(
    image: Image.Image,
) -> Image.Image:
    rotated = image.rotate(
        1.2,
        expand=True,
        fillcolor="white",
    )

    array = np.asarray(
        rotated
    ).astype(np.int16)

    random = np.random.default_rng(2026)

    noise = random.normal(
        0,
        4,
        array.shape,
    )

    noisy = np.clip(
        array + noise,
        0,
        255,
    ).astype(np.uint8)

    return Image.fromarray(noisy)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    output_directory = Path(
        args.output
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    for invoice in INVOICES:
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

        elif invoice["format"] == "png":
            image = pdf_to_image(
                pdf_bytes
            )

            image.save(
                output_path,
                format="PNG",
            )

        else:
            image = pdf_to_image(
                pdf_bytes
            )

            image = add_mild_noise(
                image
            )

            image.save(
                output_path,
                format="JPEG",
                quality=92,
            )

        print(
            f"Generada: {output_path}"
        )


if __name__ == "__main__":
    main()
