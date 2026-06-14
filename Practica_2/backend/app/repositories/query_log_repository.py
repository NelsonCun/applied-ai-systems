from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import QueryLog


class QueryLogRepository:
    @staticmethod
    def create(
        database: Session,
        *,
        telegram_user_id: int | None,
        telegram_username: str | None,
        telegram_first_name: str | None,
        telegram_chat_id: int | None,
        original_query: str,
        normalized_query: str,
        question_id: int | None,
        category_id: int | None,
        response_text: str,
        was_answered: bool,
    ) -> QueryLog:
        query_log = QueryLog(
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            telegram_first_name=telegram_first_name,
            telegram_chat_id=telegram_chat_id,
            original_query=original_query,
            normalized_query=normalized_query,
            question_id=question_id,
            category_id=category_id,
            response_text=response_text,
            was_answered=was_answered,
        )

        database.add(query_log)
        database.commit()
        database.refresh(query_log)

        return query_log

    @staticmethod
    def list_paginated(
        database: Session,
        *,
        page: int,
        page_size: int,
        search: str | None,
        was_answered: bool | None,
    ) -> tuple[list[QueryLog], int]:
        filters = []

        if search:
            pattern = f"%{search.strip()}%"

            filters.append(
                or_(
                    QueryLog.original_query.ilike(pattern),
                    QueryLog.normalized_query.ilike(pattern),
                    func.coalesce(
                        QueryLog.telegram_username,
                        "",
                    ).ilike(pattern),
                    func.coalesce(
                        QueryLog.telegram_first_name,
                        "",
                    ).ilike(pattern),
                )
            )

        if was_answered is not None:
            filters.append(
                QueryLog.was_answered.is_(was_answered)
            )

        count_statement = select(
            func.count(QueryLog.id)
        ).where(*filters)

        total = int(
            database.scalar(count_statement) or 0
        )

        statement = (
            select(QueryLog)
            .where(*filters)
            .order_by(QueryLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        items = list(
            database.scalars(statement).all()
        )

        return items, total

    @staticmethod
    def get_by_id(
        database: Session,
        query_log_id: int,
    ) -> QueryLog | None:
        return database.get(QueryLog, query_log_id)
