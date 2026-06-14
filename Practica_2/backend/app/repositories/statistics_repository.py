from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import (
    Answer,
    Category,
    QueryLog,
    Question,
)


class StatisticsRepository:
    @staticmethod
    def get_summary(
        database: Session,
    ) -> dict[str, int | float]:
        query_statistics = database.execute(
            select(
                func.count(QueryLog.id).label(
                    "total_queries"
                ),
                func.count(QueryLog.id)
                .filter(
                    QueryLog.was_answered.is_(True)
                )
                .label("answered_queries"),
                func.count(QueryLog.id)
                .filter(
                    QueryLog.was_answered.is_(False)
                )
                .label("unanswered_queries"),
                func.count(
                    func.distinct(
                        QueryLog.telegram_user_id
                    )
                )
                .filter(
                    QueryLog.telegram_user_id.is_not(None)
                )
                .label("unique_users"),
                func.count(
                    func.distinct(
                        QueryLog.telegram_chat_id
                    )
                )
                .filter(
                    QueryLog.telegram_chat_id.is_not(None)
                )
                .label("unique_chats"),
            )
        ).one()

        total_categories = int(
            database.scalar(
                select(func.count(Category.id))
            )
            or 0
        )

        total_questions = int(
            database.scalar(
                select(func.count(Question.id))
            )
            or 0
        )

        total_answers = int(
            database.scalar(
                select(func.count(Answer.id))
            )
            or 0
        )

        total_queries = int(
            query_statistics.total_queries or 0
        )

        answered_queries = int(
            query_statistics.answered_queries or 0
        )

        answer_rate = (
            answered_queries / total_queries * 100
            if total_queries
            else 0.0
        )

        return {
            "total_queries": total_queries,
            "answered_queries": answered_queries,
            "unanswered_queries": int(
                query_statistics.unanswered_queries or 0
            ),
            "unique_users": int(
                query_statistics.unique_users or 0
            ),
            "unique_chats": int(
                query_statistics.unique_chats or 0
            ),
            "total_categories": total_categories,
            "total_questions": total_questions,
            "total_answers": total_answers,
            "answer_rate": round(answer_rate, 2),
        }

    @staticmethod
    def get_top_questions(
        database: Session,
        limit: int,
    ) -> list[dict]:
        query_count = func.count(
            QueryLog.id
        ).label("query_count")

        statement = (
            select(
                Question.id.label("question_id"),
                Question.question_text,
                Category.name.label(
                    "category_name"
                ),
                query_count,
            )
            .join(
                Category,
                Category.id == Question.category_id,
            )
            .join(
                QueryLog,
                QueryLog.question_id == Question.id,
            )
            .group_by(
                Question.id,
                Question.question_text,
                Category.name,
            )
            .order_by(
                query_count.desc(),
                Question.id.asc(),
            )
            .limit(limit)
        )

        return [
            dict(row._mapping)
            for row in database.execute(statement)
        ]

    @staticmethod
    def get_top_queries(
        database: Session,
        limit: int,
    ) -> list[dict]:
        query_count = func.count(
            QueryLog.id
        ).label("query_count")

        answered_count = func.sum(
            case(
                (
                    QueryLog.was_answered.is_(True),
                    1,
                ),
                else_=0,
            )
        ).label("answered_count")

        unanswered_count = func.sum(
            case(
                (
                    QueryLog.was_answered.is_(False),
                    1,
                ),
                else_=0,
            )
        ).label("unanswered_count")

        statement = (
            select(
                QueryLog.normalized_query,
                func.min(
                    QueryLog.original_query
                ).label("sample_query"),
                query_count,
                answered_count,
                unanswered_count,
            )
            .group_by(QueryLog.normalized_query)
            .order_by(
                query_count.desc(),
                QueryLog.normalized_query.asc(),
            )
            .limit(limit)
        )

        return [
            dict(row._mapping)
            for row in database.execute(statement)
        ]

    @staticmethod
    def get_statistics_by_category(
        database: Session,
    ) -> list[dict]:
        query_count = func.count(
            QueryLog.id
        ).label("query_count")

        statement = (
            select(
                Category.id.label("category_id"),
                Category.name.label(
                    "category_name"
                ),
                query_count,
            )
            .outerjoin(
                QueryLog,
                QueryLog.category_id == Category.id,
            )
            .group_by(
                Category.id,
                Category.name,
            )
            .order_by(
                query_count.desc(),
                Category.name.asc(),
            )
        )

        return [
            dict(row._mapping)
            for row in database.execute(statement)
        ]
