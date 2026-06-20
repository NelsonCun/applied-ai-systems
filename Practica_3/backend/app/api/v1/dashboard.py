from typing import Any

from fastapi import APIRouter, Depends
from psycopg import Connection

from app.api.dependencies import get_current_user
from app.db.connection import get_connection
from app.repositories.dashboard_repository import (
    get_dashboard_summary,
    get_monthly_metrics,
    get_provider_metrics,
    get_status_metrics,
)
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardSummary,
    MonthlyMetric,
    ProviderMetric,
    StatusMetric,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardResponse,
    summary="Consultar métricas administrativas",
)
def dashboard_summary(
    connection: Connection = Depends(
        get_connection
    ),
    current_user: dict[str, Any] = Depends(
        get_current_user
    ),
) -> DashboardResponse:
    del current_user

    summary = get_dashboard_summary(
        connection
    )

    return DashboardResponse(
        summary=DashboardSummary(**summary),
        by_status=[
            StatusMetric(**row)
            for row in get_status_metrics(
                connection
            )
        ],
        by_provider=[
            ProviderMetric(**row)
            for row in get_provider_metrics(
                connection
            )
        ],
        monthly=[
            MonthlyMetric(**row)
            for row in get_monthly_metrics(
                connection
            )
        ],
    )
