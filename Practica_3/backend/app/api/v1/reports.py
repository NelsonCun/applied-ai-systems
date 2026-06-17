from math import ceil
from pathlib import Path
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import FileResponse
from psycopg import Connection

from app.api.dependencies import get_current_user
from app.db.connection import get_connection
from app.repositories.provider_repository import (
    find_provider_by_id,
)
from app.repositories.report_repository import (
    create_report,
    find_report_by_id,
    get_report_internal,
    list_reports,
)
from app.schemas.report import (
    ReportGenerateRequest,
    ReportListResponse,
    ReportQueuedResponse,
    ReportResponse,
)
from app.tasks.report_tasks import (
    generate_report_task,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reportes"],
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
    "",
    response_model=ReportQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generar reporte",
)
def generate_report_endpoint(
    request: ReportGenerateRequest,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> ReportQueuedResponse:
    status_filter = (
        request.status.upper()
        if request.status
        else None
    )

    if (
        status_filter is not None
        and status_filter
        not in VALID_STATUSES
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail="Estado de factura no válido",
        )

    if request.provider_id is not None:
        provider = find_provider_by_id(
            connection,
            request.provider_id,
        )

        if provider is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                ),
                detail="El proveedor no existe",
            )

    filters = {
        "date_from": (
            request.date_from.isoformat()
            if request.date_from
            else None
        ),
        "date_to": (
            request.date_to.isoformat()
            if request.date_to
            else None
        ),
        "provider_id": request.provider_id,
        "status": status_filter,
    }

    report = create_report(
        connection=connection,
        report_type=request.report_type,
        report_format=request.format,
        filters=filters,
        generated_by=current_user["id"],
    )

    task = generate_report_task.delay(
        report["id"]
    )

    return ReportQueuedResponse(
        message=(
            "El reporte fue enviado a la cola "
            "de generación"
        ),
        task_id=task.id,
        report=ReportResponse(**report),
    )


@router.get(
    "",
    response_model=ReportListResponse,
    summary="Listar reportes",
)
def get_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> ReportListResponse:
    del current_user

    reports, total = list_reports(
        connection,
        page,
        page_size,
    )

    return ReportListResponse(
        items=[
            ReportResponse(**report)
            for report in reports
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(
            ceil(total / page_size)
            if total > 0
            else 0
        ),
    )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Consultar un reporte",
)
def get_report(
    report_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> ReportResponse:
    del current_user

    report = find_report_by_id(
        connection,
        report_id,
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado",
        )

    return ReportResponse(**report)


@router.get(
    "/{report_id}/download",
    response_class=FileResponse,
    summary="Descargar reporte",
)
def download_report(
    report_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> FileResponse:
    del current_user

    report = get_report_internal(
        connection,
        report_id,
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado",
        )

    if report["status"] != "SUCCESS":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El reporte todavía no está disponible"
            ),
        )

    if not report["file_path"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El reporte no posee archivo",
        )

    path = Path(report["file_path"])

    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "El archivo físico del reporte "
                "no está disponible"
            ),
        )

    media_types = {
        "PDF": "application/pdf",
        "XLSX": (
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        "CSV": "text/csv",
    }

    return FileResponse(
        path=str(path),
        filename=report["file_name"],
        media_type=media_types[
            report["format"]
        ],
    )
