from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import QueryLog
from app.repositories.query_log_repository import (
    QueryLogRepository,
)
from app.schemas.query_log import QueryLogListResponse


class QueryLogService:
    @staticmethod
    def list_paginated(
        database: Session,
        *,
        page: int,
        page_size: int,
        search: str | None,
        was_answered: bool | None,
    ) -> QueryLogListResponse:
        items, total = (
            QueryLogRepository.list_paginated(
                database=database,
                page=page,
                page_size=page_size,
                search=search,
                was_answered=was_answered,
            )
        )

        return QueryLogListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    def get_by_id(
        database: Session,
        query_log_id: int,
    ) -> QueryLog:
        query_log = QueryLogRepository.get_by_id(
            database=database,
            query_log_id=query_log_id,
        )

        if query_log is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "El registro de consulta no existe."
                ),
            )

        return query_log
