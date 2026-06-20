from math import ceil
from pathlib import Path
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    Response,
    status,
)
from psycopg import Connection
from psycopg.errors import UniqueViolation
from fastapi.responses import FileResponse

from app.api.dependencies import get_current_user
from app.db.connection import get_connection
from app.repositories.invoice_repository import (
    confirm_invoice_review,
    find_invoice_by_id,
    get_invoice_ocr_data,
    list_invoice_processing_logs,
    list_invoices,
)
from app.schemas.invoice import (
    BatchUploadError,
    BatchUploadResponse,
    InvoiceListResponse,
    InvoiceOcrResponse,
    InvoiceResponse,
    InvoiceReviewRequest,
    InvoiceReviewResponse,
    ProcessingLogResponse,
    InvoiceUploadResponse,
    ProcessingQueuedResponse,
)
from app.repositories.provider_repository import (
    find_provider_by_id,
)
from app.services.invoice_review_service import (
    InvoiceReviewValidationError,
    validate_invoice_review,
)
from app.services.invoice_upload_service import (
    UploadValidationError,
    store_uploaded_invoice,
)
from app.tasks.invoice_tasks import (
    process_invoice_task,
)


router = APIRouter(
    prefix="/invoices",
    tags=["Facturas"],
)


VALID_STATUSES = {
    "PENDING",
    "PROCESSING",
    "PROCESSED",
    "REJECTED",
    "ERROR",
    "DUPLICATE",
}


@router.post(
    "/upload",
    response_model=InvoiceUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cargar y procesar una factura",
)
async def upload_invoice(
    file: UploadFile = File(...),
    provider_id: int | None = Form(None),
    category_id: int | None = Form(None),
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> InvoiceUploadResponse:
    try:
        result = await store_uploaded_invoice(
            connection=connection,
            upload=file,
            user_id=current_user["id"],
            provider_id=provider_id,
            category_id=category_id,
        )
    except UploadValidationError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(error),
        ) from error

    task_id: str | None = None

    if not result["is_duplicate"]:
        task = process_invoice_task.delay(
            result["invoice"]["id"]
        )
        task_id = task.id

    return InvoiceUploadResponse(
        message=result["message"],
        is_duplicate=result["is_duplicate"],
        task_id=task_id,
        invoice=InvoiceResponse(
            **result["invoice"]
        ),
    )


@router.post(
    "/batch",
    response_model=BatchUploadResponse,
    summary="Cargar múltiples facturas",
)
async def upload_invoice_batch(
    files: list[UploadFile] = File(...),
    provider_id: int | None = Form(None),
    category_id: int | None = Form(None),
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> BatchUploadResponse:
    if len(files) > 20:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=(
                "Solo se permiten hasta 20 archivos "
                "por carga masiva"
            ),
        )

    items: list[InvoiceUploadResponse] = []
    errors: list[BatchUploadError] = []
    duplicate_count = 0

    for file in files:
        file_name = file.filename or "documento"

        try:
            result = await store_uploaded_invoice(
                connection=connection,
                upload=file,
                user_id=current_user["id"],
                provider_id=provider_id,
                category_id=category_id,
            )

            task_id: str | None = None

            if result["is_duplicate"]:
                duplicate_count += 1
            else:
                task = process_invoice_task.delay(
                    result["invoice"]["id"]
                )
                task_id = task.id

            items.append(
                InvoiceUploadResponse(
                    message=result["message"],
                    is_duplicate=(
                        result["is_duplicate"]
                    ),
                    task_id=task_id,
                    invoice=InvoiceResponse(
                        **result["invoice"]
                    ),
                )
            )

        except UploadValidationError as error:
            errors.append(
                BatchUploadError(
                    file_name=file_name,
                    error=str(error),
                )
            )

        except Exception:
            errors.append(
                BatchUploadError(
                    file_name=file_name,
                    error=(
                        "No fue posible almacenar "
                        "el documento"
                    ),
                )
            )

    return BatchUploadResponse(
        received=len(files),
        successful=len(items),
        duplicates=duplicate_count,
        failed=len(errors),
        items=items,
        errors=errors,
    )


@router.post(
    "/{invoice_id}/process",
    response_model=ProcessingQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Procesar o reprocesar una factura",
)
def queue_invoice_processing(
    invoice_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> ProcessingQueuedResponse:
    del current_user

    invoice = find_invoice_by_id(
        connection,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada",
        )

    if invoice["status"] == "DUPLICATE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Una factura duplicada no puede procesarse"
            ),
        )

    if invoice["status"] == "PROCESSING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "La factura ya está siendo procesada"
            ),
        )

    task = process_invoice_task.delay(
        invoice_id
    )

    return ProcessingQueuedResponse(
        invoice_id=invoice_id,
        task_id=task.id,
        message=(
            "La factura fue enviada a la cola de procesamiento"
        ),
    )


@router.get(
    "",
    response_model=InvoiceListResponse,
    summary="Listar facturas",
)
def get_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        None,
        max_length=180,
    ),
    status_filter: str | None = Query(
        None,
        alias="status",
    ),
    provider_id: int | None = Query(
        None,
        gt=0,
    ),
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> InvoiceListResponse:
    del current_user

    if status_filter is not None:
        status_filter = status_filter.upper()

        if status_filter not in VALID_STATUSES:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail="Estado de factura no válido",
            )

    invoices, total = list_invoices(
        connection=connection,
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status_filter,
        provider_id=provider_id,
    )

    total_pages = (
        ceil(total / page_size)
        if total > 0
        else 0
    )

    return InvoiceListResponse(
        items=[
            InvoiceResponse(**invoice)
            for invoice in invoices
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )



@router.get(
    "/{invoice_id}/ocr",
    response_model=InvoiceOcrResponse,
    summary="Consultar resultado OCR",
)
def get_invoice_ocr(
    invoice_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> InvoiceOcrResponse:
    del current_user

    result = get_invoice_ocr_data(
        connection,
        invoice_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada",
        )

    return InvoiceOcrResponse(**result)


@router.get(
    "/{invoice_id}/logs",
    response_model=list[ProcessingLogResponse],
    summary="Consultar bitácora de procesamiento",
)
def get_invoice_logs(
    invoice_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> list[ProcessingLogResponse]:
    del current_user

    invoice = find_invoice_by_id(
        connection,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada",
        )

    return [
        ProcessingLogResponse(**log)
        for log in list_invoice_processing_logs(
            connection,
            invoice_id,
        )
    ]


@router.get(
    "/{invoice_id}/file",
    response_class=FileResponse,
    summary="Visualizar documento original",
)
def get_invoice_file(
    invoice_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> Response:
    del current_user

    invoice = find_invoice_by_id(
        connection,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada",
        )

    path = Path(invoice["file_path"])

    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El archivo físico no está disponible",
        )

    return FileResponse(
        path=str(path),
        media_type=invoice["mime_type"],
        filename=invoice["original_file_name"],
        content_disposition_type="inline",
    )


@router.get(
    "/{invoice_id}/processed-file",
    response_class=FileResponse,
    summary="Visualizar imagen preprocesada",
)
def get_processed_invoice_file(
    invoice_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> Response:
    del current_user

    invoice = find_invoice_by_id(
        connection,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada",
        )

    processed_path = invoice[
        "processed_file_path"
    ]

    if not processed_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La factura todavía no posee una imagen procesada",
        )

    path = Path(processed_path)

    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La imagen procesada no está disponible",
        )

    return FileResponse(
        path=str(path),
        media_type="image/png",
        filename=path.name,
        content_disposition_type="inline",
    )


@router.put(
    "/{invoice_id}/review",
    response_model=InvoiceReviewResponse,
    summary="Corregir y confirmar factura",
)
def review_invoice(
    invoice_id: int,
    request: InvoiceReviewRequest,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> InvoiceReviewResponse:
    invoice = find_invoice_by_id(
        connection,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada",
        )

    if invoice["status"] == "DUPLICATE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Una factura duplicada no puede confirmarse",
        )

    provider = find_provider_by_id(
        connection,
        request.provider_id,
    )

    if provider is None or not provider["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El proveedor no existe o está inactivo",
        )

    try:
        validated = validate_invoice_review(
            request.model_dump(),
            provider,
        )

        reviewed = confirm_invoice_review(
            connection=connection,
            invoice_id=invoice_id,
            data=validated,
            confirmed_by=current_user["id"],
        )

    except InvoiceReviewValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    except UniqueViolation as error:
        connection.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Ya existe una factura con ese número "
                "para el proveedor seleccionado"
            ),
        ) from error

    if reviewed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada",
        )

    return InvoiceReviewResponse(
        message="Factura revisada y confirmada correctamente",
        invoice=InvoiceResponse(**reviewed),
    )


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Consultar una factura",
)
def get_invoice(
    invoice_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> InvoiceResponse:
    del current_user

    invoice = find_invoice_by_id(
        connection,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada",
        )

    return InvoiceResponse(**invoice)
