from pathlib import Path

import cv2
import fitz
import numpy as np

from app.core.config import settings


class DocumentLoadError(ValueError):
    pass


def load_document_pages(
    file_path: str,
    mime_type: str,
) -> list[np.ndarray]:
    path = Path(file_path)

    if not path.exists():
        raise DocumentLoadError(
            f"No existe el documento: {file_path}"
        )

    if mime_type == "application/pdf":
        return _load_pdf_pages(path)

    if mime_type in {
        "image/png",
        "image/jpeg",
    }:
        image = cv2.imread(
            str(path),
            cv2.IMREAD_COLOR,
        )

        if image is None:
            raise DocumentLoadError(
                "No fue posible decodificar la imagen"
            )

        return [image]

    raise DocumentLoadError(
        f"Tipo de documento no soportado: {mime_type}"
    )


def _load_pdf_pages(
    path: Path,
) -> list[np.ndarray]:
    pages: list[np.ndarray] = []

    try:
        document = fitz.open(path)
    except Exception as error:
        raise DocumentLoadError(
            "No fue posible abrir el documento PDF"
        ) from error

    try:
        if document.page_count == 0:
            raise DocumentLoadError(
                "El PDF no contiene páginas"
            )

        page_count = min(
            document.page_count,
            settings.max_pdf_pages,
        )

        for index in range(page_count):
            page = document.load_page(index)

            pixmap = page.get_pixmap(
                dpi=settings.ocr_dpi,
                alpha=False,
            )

            image_bytes = pixmap.tobytes("png")

            image_array = np.frombuffer(
                image_bytes,
                dtype=np.uint8,
            )

            image = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR,
            )

            if image is None:
                raise DocumentLoadError(
                    f"No fue posible convertir la página {index + 1}"
                )

            pages.append(image)

    finally:
        document.close()

    return pages
