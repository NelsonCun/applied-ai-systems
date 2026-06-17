import time
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row
from rapidfuzz import fuzz

from app.computer_vision.document_loader import (
    load_document_pages,
)
from app.computer_vision.preprocessor import (
    preprocess_image,
    save_processed_image,
)
from app.core.config import settings
from app.ocr.engine import extract_text
from app.ocr.parser import (
    parse_invoice_text,
    validate_extracted_data,
)
from app.repositories.processing_repository import (
    complete_invoice_processing,
    fail_invoice_processing,
    find_duplicate_invoice,
    find_provider_by_nit,
    get_invoice_for_processing,
    insert_processing_log,
    list_provider_candidates,
    mark_invoice_processing,
)


def json_safe(
    value: Any,
) -> Any:
    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            json_safe(item)
            for item in value
        ]

    return value


def match_provider(
    connection: psycopg.Connection,
    extracted_nit: str | None,
    extracted_text: str,
) -> tuple[dict[str, Any] | None, float]:
    if extracted_nit:
        exact_match = find_provider_by_nit(
            connection,
            extracted_nit,
        )

        if exact_match is not None:
            return exact_match, 100.0

    normalized_text = extracted_text.upper()

    best_provider: dict[str, Any] | None = None
    best_score = 0.0

    for provider in list_provider_candidates(
        connection
    ):
        score = float(
            fuzz.partial_ratio(
                provider["name"].upper(),
                normalized_text,
            )
        )

        if score > best_score:
            best_score = score
            best_provider = provider

    if best_score < 75:
        return None, best_score

    return best_provider, best_score


def process_invoice(
    invoice_id: int,
) -> dict[str, Any]:
    connection = psycopg.connect(
        settings.database_url,
        row_factory=dict_row,
    )

    try:
        invoice = get_invoice_for_processing(
            connection,
            invoice_id,
        )

        if invoice is None:
            raise ValueError(
                "La factura no existe"
            )

        if invoice["status"] == "DUPLICATE":
            raise ValueError(
                "Las facturas duplicadas no se procesan"
            )

        mark_invoice_processing(
            connection,
            invoice_id,
        )

        insert_processing_log(
            connection=connection,
            invoice_id=invoice_id,
            stage="COMPUTER_VISION",
            status="RUNNING",
            message="Inició el preprocesamiento del documento",
            details={},
        )

        connection.commit()

        computer_vision_started = (
            time.perf_counter()
        )

        pages = load_document_pages(
            file_path=invoice["file_path"],
            mime_type=invoice["mime_type"],
        )

        processed_directory = Path(
            settings.processed_dir
        )

        processed_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        processed_paths: list[str] = []
        preprocessing_metadata: list[dict] = []
        page_ocr_results: list[dict] = []

        for page_index, page in enumerate(
            pages,
            start=1,
        ):
            processed_image, metadata = (
                preprocess_image(page)
            )

            processed_path = (
                processed_directory
                / (
                    f"invoice_{invoice_id}"
                    f"_page_{page_index}.png"
                )
            )

            save_processed_image(
                processed_image,
                str(processed_path),
            )

            processed_paths.append(
                str(processed_path)
            )

            preprocessing_metadata.append(
                {
                    "page": page_index,
                    **metadata,
                }
            )

            ocr_result = extract_text(
                processed_image,
                settings.tesseract_language,
            )

            page_ocr_results.append(
                {
                    "page": page_index,
                    **ocr_result,
                }
            )

        computer_vision_duration = int(
            (
                time.perf_counter()
                - computer_vision_started
            )
            * 1000
        )

        insert_processing_log(
            connection=connection,
            invoice_id=invoice_id,
            stage="COMPUTER_VISION",
            status="SUCCESS",
            message=(
                "Preprocesamiento de imágenes completado"
            ),
            details={
                "page_count": len(pages),
                "pages": preprocessing_metadata,
            },
            duration_ms=computer_vision_duration,
        )

        combined_text = "\n\n".join(
            result["text"]
            for result in page_ocr_results
        )

        confidence_values = [
            float(result["confidence"])
            for result in page_ocr_results
        ]

        average_confidence = (
            sum(confidence_values)
            / len(confidence_values)
            if confidence_values
            else 0.0
        )

        insert_processing_log(
            connection=connection,
            invoice_id=invoice_id,
            stage="OCR",
            status="SUCCESS",
            message="Extracción OCR completada",
            details={
                "page_count": len(
                    page_ocr_results
                ),
                "recognized_words": sum(
                    int(
                        result[
                            "recognized_words"
                        ]
                    )
                    for result
                    in page_ocr_results
                ),
                "confidence": round(
                    average_confidence,
                    2,
                ),
            },
        )

        extracted = parse_invoice_text(
            combined_text
        )

        matched_provider, match_score = (
            match_provider(
                connection,
                extracted.get("nit"),
                combined_text,
            )
        )

        if (
            matched_provider is not None
            and not extracted.get(
                "provider_name"
            )
        ):
            extracted["provider_name"] = (
                matched_provider["name"]
            )

        provider_id = (
            invoice["provider_id"]
            or (
                matched_provider["id"]
                if matched_provider
                else None
            )
        )

        category_id = (
            invoice["category_id"]
            or (
                matched_provider["category_id"]
                if matched_provider
                else None
            )
        )

        validation_errors = (
            validate_extracted_data(
                data=extracted,
                confidence=average_confidence,
                minimum_confidence=(
                    settings.ocr_min_confidence
                ),
            )
        )

        if (
            invoice["provider_nit"]
            and extracted.get("nit")
            and invoice["provider_nit"].upper()
            != extracted["nit"].upper()
        ):
            validation_errors.append(
                {
                    "field": "nit",
                    "message": (
                        "El NIT extraído no coincide con "
                        "el proveedor seleccionado"
                    ),
                }
            )

        duplicate_invoice = (
            find_duplicate_invoice(
                connection=connection,
                invoice_id=invoice_id,
                provider_id=provider_id,
                invoice_number=extracted.get(
                    "invoice_number"
                ),
            )
        )

        if duplicate_invoice is not None:
            validation_errors.append(
                {
                    "field": "invoice_number",
                    "message": (
                        "La factura ya fue registrada "
                        "anteriormente"
                    ),
                    "duplicate_of_invoice_id": (
                        duplicate_invoice["id"]
                    ),
                    "duplicate_invoice_number": (
                        duplicate_invoice[
                            "invoice_number"
                        ]
                    ),
                }
            )

            final_status = "DUPLICATE"

        else:
            final_status = (
                "REJECTED"
                if validation_errors
                else "PROCESSED"
            )

        extracted_data = {
            "fields": {
                key: json_safe(value)
                for key, value in extracted.items()
                if key != "normalized_text"
            },
            "provider_match": {
                "provider_id": (
                    matched_provider["id"]
                    if matched_provider
                    else None
                ),
                "provider_name": (
                    matched_provider["name"]
                    if matched_provider
                    else None
                ),
                "score": round(
                    match_score,
                    2,
                ),
            },
            "pages": preprocessing_metadata,
            "processed_files": processed_paths,
        }

        complete_invoice_processing(
            connection=connection,
            invoice_id=invoice_id,
            data={
                "invoice_number": extracted.get(
                    "invoice_number"
                ),
                "invoice_date": extracted.get(
                    "invoice_date"
                ),
                "provider_id": provider_id,
                "category_id": category_id,
                "duplicate_of_invoice_id": (
                    duplicate_invoice["id"]
                    if duplicate_invoice
                    else None
                ),
                "detected_provider_name": (
                    matched_provider["name"]
                    if matched_provider
                    else extracted.get(
                        "provider_name"
                    )
                ),
                "detected_nit": extracted.get(
                    "nit"
                ),
                "subtotal": extracted.get(
                    "subtotal"
                ),
                "tax": extracted.get("tax"),
                "total": extracted.get("total"),
                "currency": extracted.get(
                    "currency",
                    "GTQ",
                ),
                "processed_file_path": (
                    processed_paths[0]
                    if processed_paths
                    else None
                ),
                "ocr_text": combined_text,
                "ocr_confidence": round(
                    average_confidence,
                    2,
                ),
                "extracted_data": (
                    extracted_data
                ),
                "validation_errors": (
                    validation_errors
                ),
                "status": final_status,
            },
        )

        insert_processing_log(
            connection=connection,
            invoice_id=invoice_id,
            stage="EXTRACTION",
            status="SUCCESS",
            message=(
                "Extracción estructurada de campos completada"
            ),
            details={
                "fields": extracted_data["fields"],
                "provider_match": (
                    extracted_data[
                        "provider_match"
                    ]
                ),
            },
        )

        insert_processing_log(
            connection=connection,
            invoice_id=invoice_id,
            stage="VALIDATION",
            status=(
                "WARNING"
                if validation_errors
                else "SUCCESS"
            ),
            message=(
                "Documento identificado como duplicado"
                if final_status == "DUPLICATE"
                else (
                    "Documento rechazado por validaciones"
                    if validation_errors
                    else (
                        "Documento validado "
                        "correctamente"
                    )
                )
            ),
            details={
                "errors": validation_errors,
                "final_status": final_status,
                "duplicate_of_invoice_id": (
                    duplicate_invoice["id"]
                    if duplicate_invoice
                    else None
                ),
            },
        )

        connection.commit()

        return {
            "invoice_id": invoice_id,
            "status": final_status,
            "confidence": round(
                average_confidence,
                2,
            ),
            "validation_errors": (
                validation_errors
            ),
            "duplicate_of_invoice_id": (
                duplicate_invoice["id"]
                if duplicate_invoice
                else None
            ),
        }

    except Exception as error:
        connection.rollback()

        try:
            fail_invoice_processing(
                connection,
                invoice_id,
                str(error),
            )

            insert_processing_log(
                connection=connection,
                invoice_id=invoice_id,
                stage="OCR",
                status="ERROR",
                message=(
                    "Falló el procesamiento del documento"
                ),
                details={
                    "error": str(error),
                },
            )

            connection.commit()

        except Exception:
            connection.rollback()

        raise

    finally:
        connection.close()
