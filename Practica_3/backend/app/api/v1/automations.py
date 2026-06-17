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
from app.core.config import settings
from app.db.connection import get_connection
from app.repositories.automation_repository import (
    create_rpa_run,
    find_rpa_run_by_id,
    list_rpa_runs,
)
from app.repositories.invoice_repository import (
    find_invoice_by_id,
)
from app.schemas.automation import (
    AutomationListResponse,
    AutomationQueuedResponse,
    AutomationRunResponse,
)
from app.tasks.rpa_tasks import (
    register_invoice_rpa_task,
)


router = APIRouter(
    prefix="/automations",
    tags=["Automatizaciones"],
)


@router.post(
    "/rpa/invoices/{invoice_id}",
    response_model=AutomationQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Registrar factura mediante RPA",
)
def queue_invoice_rpa(
    invoice_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> AutomationQueuedResponse:
    invoice = find_invoice_by_id(
        connection,
        invoice_id,
    )

    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura no encontrada",
        )

    if invoice["status"] != "PROCESSED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Solo se pueden automatizar "
                "facturas procesadas"
            ),
        )

    automation = create_rpa_run(
        connection=connection,
        invoice_id=invoice_id,
        triggered_by=current_user["id"],
        target_url=settings.rpa_target_url,
    )

    task = register_invoice_rpa_task.delay(
        automation["id"]
    )

    return AutomationQueuedResponse(
        message=(
            "La automatización fue enviada "
            "a la cola de ejecución"
        ),
        task_id=task.id,
        automation=AutomationRunResponse(
            **automation
        ),
    )


@router.get(
    "/rpa",
    response_model=AutomationListResponse,
    summary="Listar automatizaciones RPA",
)
def get_rpa_runs(
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
) -> AutomationListResponse:
    del current_user

    items, total = list_rpa_runs(
        connection,
        page,
        page_size,
    )

    return AutomationListResponse(
        items=[
            AutomationRunResponse(**item)
            for item in items
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
    "/rpa/{run_id}",
    response_model=AutomationRunResponse,
    summary="Consultar automatización RPA",
)
def get_rpa_run(
    run_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> AutomationRunResponse:
    del current_user

    automation = find_rpa_run_by_id(
        connection,
        run_id,
    )

    if automation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automatización no encontrada",
        )

    return AutomationRunResponse(
        **automation
    )


@router.get(
    "/rpa/{run_id}/evidence",
    response_class=FileResponse,
    summary="Descargar evidencia RPA",
)
def get_rpa_evidence(
    run_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> FileResponse:
    del current_user

    automation = find_rpa_run_by_id(
        connection,
        run_id,
    )

    if automation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automatización no encontrada",
        )

    evidence_path = automation[
        "evidence_path"
    ]

    if not evidence_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "La automatización todavía no "
                "posee evidencia"
            ),
        )

    path = Path(evidence_path)

    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "El archivo de evidencia "
                "no está disponible"
            ),
        )

    return FileResponse(
        path=str(path),
        media_type="image/png",
        filename=path.name,
    )
