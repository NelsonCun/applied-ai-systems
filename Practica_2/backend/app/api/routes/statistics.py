from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.db.session import get_db
from app.models import AdminUser
from app.schemas.statistics import (
    CategoryStatisticsItem,
    StatisticsSummaryResponse,
    TopQueryItem,
    TopQuestionItem,
)
from app.services.statistics_service import (
    StatisticsService,
)


router = APIRouter(
    prefix="/statistics",
    tags=["Estadísticas"],
)


@router.get(
    "/summary",
    response_model=StatisticsSummaryResponse,
)
def get_statistics_summary(
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(
        get_current_admin
    ),
):
    del current_user

    return StatisticsService.get_summary(
        database=database
    )


@router.get(
    "/top-questions",
    response_model=list[TopQuestionItem],
)
def get_top_questions(
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(
        get_current_admin
    ),
):
    del current_user

    return StatisticsService.get_top_questions(
        database=database,
        limit=limit,
    )


@router.get(
    "/top-queries",
    response_model=list[TopQueryItem],
)
def get_top_queries(
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(
        get_current_admin
    ),
):
    del current_user

    return StatisticsService.get_top_queries(
        database=database,
        limit=limit,
    )


@router.get(
    "/by-category",
    response_model=list[CategoryStatisticsItem],
)
def get_statistics_by_category(
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(
        get_current_admin
    ),
):
    del current_user

    return StatisticsService.get_by_category(
        database=database
    )
