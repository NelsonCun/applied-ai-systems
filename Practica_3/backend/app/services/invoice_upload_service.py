import hashlib
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import UploadFile
from psycopg import Connection

from app.core.config import settings
from app.repositories.invoice_repository import (
    category_exists,
    create_invoice_record,
    create_processing_log,
    find_invoice_by_id,
    find_original_by_hash,
    provider_exists,
)


CHUNK_SIZE = 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


class UploadValidationError(ValueError):
    pass


def detect_mime_type(header: bytes) -> str | None:
    if header.startswith(b"%PDF-"):
        return "application/pdf"

    if header.startswith(b"\xFF\xD8\xFF"):
        return "image/jpeg"

    if header.startswith(
        b"\x89PNG\r\n\x1a\n"
    ):
        return "image/png"

    return None


def validate_references(
    connection: Connection,
    provider_id: int | None,
    category_id: int | None,
) -> None:
    if provider_id is not None:
        if provider_id <= 0:
            raise UploadValidationError(
                "El identificador del proveedor no es válido"
            )

        if not provider_exists(
            connection,
            provider_id,
        ):
            raise UploadValidationError(
                "El proveedor indicado no existe o está inactivo"
            )

    if category_id is not None:
        if category_id <= 0:
            raise UploadValidationError(
                "El identificador de categoría no es válido"
            )

        if not category_exists(
            connection,
            category_id,
        ):
            raise UploadValidationError(
                "La categoría indicada no existe o está inactiva"
            )


async def store_uploaded_invoice(
    connection: Connection,
    upload: UploadFile,
    user_id: int,
    provider_id: int | None = None,
    category_id: int | None = None,
) -> dict[str, Any]:
    validate_references(
        connection,
        provider_id,
        category_id,
    )

    original_name = Path(
        upload.filename or "documento"
    ).name[:255]

    suffix = Path(original_name).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise UploadValidationError(
            "Formato no permitido. Utilice PDF, JPG, JPEG o PNG"
        )

    upload_directory = Path(settings.upload_dir)
    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = (
        upload_directory
        / f".tmp-{uuid4().hex}"
    )

    maximum_bytes = (
        settings.max_upload_size_mb
        * 1024
        * 1024
    )

    digest = hashlib.sha256()
    total_size = 0
    header = b""

    final_path: Path | None = None
    created_final_file = False

    try:
        with temporary_path.open("wb") as output:
            while True:
                chunk = await upload.read(CHUNK_SIZE)

                if not chunk:
                    break

                if len(header) < 16:
                    missing = 16 - len(header)
                    header += chunk[:missing]

                total_size += len(chunk)

                if total_size > maximum_bytes:
                    raise UploadValidationError(
                        "El archivo supera el tamaño máximo "
                        f"de {settings.max_upload_size_mb} MB"
                    )

                digest.update(chunk)
                output.write(chunk)

        if total_size == 0:
            raise UploadValidationError(
                "El archivo está vacío"
            )

        detected_mime = detect_mime_type(header)
        expected_mime = ALLOWED_EXTENSIONS[suffix]

        if detected_mime is None:
            raise UploadValidationError(
                "No fue posible reconocer el contenido del archivo"
            )

        if detected_mime != expected_mime:
            raise UploadValidationError(
                "La extensión no coincide con el contenido real "
                "del archivo"
            )

        file_sha256 = digest.hexdigest()

        original_invoice = find_original_by_hash(
            connection,
            file_sha256,
        )

        is_duplicate = (
            original_invoice is not None
        )

        if is_duplicate:
            temporary_path.unlink(
                missing_ok=True
            )

            stored_path = str(
                original_invoice["file_path"]
            )

            duplicate_of_invoice_id = int(
                original_invoice["id"]
            )

            invoice_status = "DUPLICATE"
            log_status = "WARNING"
            log_message = (
                "Documento duplicado detectado durante la carga"
            )
        else:
            final_path = (
                upload_directory
                / f"{file_sha256}{suffix}"
            )

            if final_path.exists():
                temporary_path.unlink(
                    missing_ok=True
                )
            else:
                os.replace(
                    temporary_path,
                    final_path,
                )
                created_final_file = True

            stored_path = str(final_path)
            duplicate_of_invoice_id = None
            invoice_status = "PENDING"
            log_status = "SUCCESS"
            log_message = (
                "Documento almacenado y pendiente de procesamiento"
            )

        invoice_id = create_invoice_record(
            connection,
            {
                "provider_id": provider_id,
                "category_id": category_id,
                "original_file_name": original_name,
                "file_path": stored_path,
                "file_sha256": file_sha256,
                "mime_type": detected_mime,
                "file_size_bytes": total_size,
                "status": invoice_status,
                "duplicate_of_invoice_id": (
                    duplicate_of_invoice_id
                ),
                "created_by": user_id,
            },
        )

        create_processing_log(
            connection=connection,
            invoice_id=invoice_id,
            user_id=user_id,
            status=log_status,
            message=log_message,
            details={
                "original_file_name": original_name,
                "file_sha256": file_sha256,
                "file_size_bytes": total_size,
                "mime_type": detected_mime,
                "duplicate": is_duplicate,
                "duplicate_of_invoice_id": (
                    duplicate_of_invoice_id
                ),
            },
        )

        connection.commit()

        invoice = find_invoice_by_id(
            connection,
            invoice_id,
        )

        if invoice is None:
            raise RuntimeError(
                "No fue posible recuperar la factura almacenada"
            )

        return {
            "message": log_message,
            "is_duplicate": is_duplicate,
            "invoice": invoice,
        }

    except Exception:
        connection.rollback()

        temporary_path.unlink(
            missing_ok=True
        )

        if (
            created_final_file
            and final_path is not None
        ):
            final_path.unlink(
                missing_ok=True
            )

        raise

    finally:
        await upload.close()
