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
