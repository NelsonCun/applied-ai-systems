from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.text_utils import (
    calculate_similarity,
    normalize_text,
)
from app.models import Question
from app.repositories.bot_setting_repository import (
    BotSettingRepository,
)
from app.repositories.query_log_repository import (
    QueryLogRepository,
)
from app.repositories.question_repository import (
    QuestionRepository,
)
from app.schemas.query import (
    QueryResolveRequest,
    QueryResolveResponse,
)


FUZZY_MATCH_THRESHOLD = 0.74


class QueryService:
    @staticmethod
    def find_best_match(
        database: Session,
        normalized_query: str,
    ) -> tuple[Question | None, float]:
        exact_match = QuestionRepository.find_exact_answer(
            database=database,
            normalized_query=normalized_query,
        )

        if exact_match is not None:
            return exact_match, 1.0

        best_question: Question | None = None
        best_score = 0.0

        for candidate in QuestionRepository.list_answerable(
            database=database
        ):
            score = calculate_similarity(
                normalized_query,
                candidate.normalized_text,
            )

            if score > best_score:
                best_question = candidate
                best_score = score

        if best_score < FUZZY_MATCH_THRESHOLD:
            return None, best_score

        return best_question, best_score

    @staticmethod
    def resolve(
        database: Session,
        data: QueryResolveRequest,
    ) -> QueryResolveResponse:
        settings = BotSettingRepository.get_settings(
            database=database
        )

        if settings is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "No existe configuración general para el bot."
                ),
            )

        normalized_query = normalize_text(data.query)

        question, confidence = QueryService.find_best_match(
            database=database,
            normalized_query=normalized_query,
        )

        if question is not None and question.answer is not None:
            response_text = question.answer.answer_text
            was_answered = True
            question_id = question.id
            category_id = question.category_id
            category_name = question.category.name
        else:
            response_text = settings.unknown_question_message
            was_answered = False
            question_id = None
            category_id = None
            category_name = None

        QueryLogRepository.create(
            database=database,
            telegram_user_id=data.telegram_user_id,
            telegram_username=data.telegram_username,
            telegram_first_name=data.telegram_first_name,
            telegram_chat_id=data.telegram_chat_id,
            original_query=data.query,
            normalized_query=normalized_query,
            question_id=question_id,
            category_id=category_id,
            response_text=response_text,
            was_answered=was_answered,
        )

        return QueryResolveResponse(
            answer=response_text,
            matched=was_answered,
            question_id=question_id,
            category_id=category_id,
            category_name=category_name,
            confidence=round(confidence, 4),
        )
