from math import ceil
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from psycopg import Connection

from app.api.dependencies import get_current_user
from app.db.connection import get_connection
from app.repositories.email_repository import (
    create_email_log,
    find_email_log_by_id,
    list_email_logs,
)
from app.repositories.report_repository import (
    get_report_internal,
)
from app.schemas.email import (
    EmailListResponse,
    EmailLogResponse,
    EmailQueuedResponse,
    ReportEmailRequest,
)
from app.tasks.email_tasks import (
    send_report_email_task,
)


router = APIRouter(
    prefix="/emails",
    tags=["Correos"],
)


@router.post(
    "/reports/{report_id}",
    response_model=EmailQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enviar reporte por correo",
)
def queue_report_email(
    report_id: int,
    request: ReportEmailRequest,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> EmailQueuedResponse:
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

    if not report["file_name"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El reporte no posee archivo generado"
            ),
        )

    subject = (
        request.subject
        or (
            "SmartInvoice - Reporte "
            f"{report['report_type']} "
            f"#{report_id}"
        )
    )

    body = (
        request.message
        or (
            "Estimado usuario:\n\n"
            "Se adjunta el reporte generado "
            "por la plataforma SmartInvoice.\n\n"
            f"Tipo: {report['report_type']}\n"
            f"Formato: {report['format']}\n"
            f"Reporte: #{report_id}\n\n"
            "Este mensaje fue generado automáticamente."
        )
    )

    email_log = create_email_log(
        connection=connection,
        report_id=report_id,
        requested_by=current_user["id"],
        recipient_email=str(
            request.recipient
        ),
        subject=subject,
        body=body,
        attachment_name=report["file_name"],
    )

    task = send_report_email_task.delay(
        email_log["id"]
    )

    return EmailQueuedResponse(
        message=(
            "El correo fue enviado a la cola "
            "de entrega"
        ),
        task_id=task.id,
        email=EmailLogResponse(
            **email_log
        ),
    )


@router.get(
    "",
    response_model=EmailListResponse,
    summary="Listar correos enviados",
)
def get_email_logs(
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
) -> EmailListResponse:
    del current_user

    items, total = list_email_logs(
        connection,
        page,
        page_size,
    )

    return EmailListResponse(
        items=[
            EmailLogResponse(**item)
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
    "/{email_id}",
    response_model=EmailLogResponse,
    summary="Consultar envío de correo",
)
def get_email_log(
    email_id: int,
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> EmailLogResponse:
    del current_user

    email_log = find_email_log_by_id(
        connection,
        email_id,
    )

    if email_log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correo no encontrado",
        )

    return EmailLogResponse(
        **email_log
    )
