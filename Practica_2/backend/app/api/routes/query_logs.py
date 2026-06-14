from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.db.session import get_db
from app.models import AdminUser
from app.schemas.query_log import (
    QueryLogListResponse,
    QueryLogResponse,
)
from app.services.query_log_service import (
    QueryLogService,
)


router = APIRouter(
    prefix="/query-logs",
    tags=["Historial de consultas"],
)


@router.get(
    "",
    response_model=QueryLogListResponse,
)
def list_query_logs(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        default=None,
        max_length=200,
    ),
    was_answered: bool | None = Query(
        default=None
    ),
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(
        get_current_admin
    ),
):
    del current_user

    return QueryLogService.list_paginated(
        database=database,
        page=page,
        page_size=page_size,
        search=search,
        was_answered=was_answered,
    )


@router.get(
    "/{query_log_id}",
    response_model=QueryLogResponse,
)
def get_query_log(
    query_log_id: int,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(
        get_current_admin
    ),
):
    del current_user

    return QueryLogService.get_by_id(
        database=database,
        query_log_id=query_log_id,
    )
