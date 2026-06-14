from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.text_utils import normalize_text
from app.models import Question
from app.repositories.category_repository import (
    CategoryRepository,
)
from app.repositories.question_repository import (
    QuestionRepository,
)
from app.schemas.question import QuestionCreate, QuestionUpdate


class QuestionService:
    @staticmethod
    def list_all(
        database: Session,
        search: str | None,
        category_id: int | None,
        is_active: bool | None,
    ) -> list[Question]:
        return QuestionRepository.list_all(
            database=database,
            search=search,
            category_id=category_id,
            is_active=is_active,
        )

    @staticmethod
    def get_by_id(
        database: Session,
        question_id: int,
    ) -> Question:
        question = QuestionRepository.get_by_id(
            database=database,
            question_id=question_id,
        )

        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La pregunta solicitada no existe.",
            )

        return question

    @staticmethod
    def validate_category(
        database: Session,
        category_id: int,
    ) -> None:
        category = CategoryRepository.get_by_id(
            database=database,
            category_id=category_id,
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría seleccionada no existe.",
            )

        if not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No se puede utilizar una categoría inactiva."
                ),
            )

    @staticmethod
    def create(
        database: Session,
        data: QuestionCreate,
    ) -> Question:
        QuestionService.validate_category(
            database=database,
            category_id=data.category_id,
        )

        normalized_text = normalize_text(
            data.question_text
        )

        duplicate = QuestionRepository.get_by_normalized_text(
            database=database,
            normalized_text=normalized_text,
        )

        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una pregunta equivalente.",
            )

        try:
            return QuestionRepository.create(
                database=database,
                category_id=data.category_id,
                question_text=data.question_text,
                normalized_text=normalized_text,
                is_active=data.is_active,
            )
        except IntegrityError as error:
            database.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible crear la pregunta.",
            ) from error

    @staticmethod
    def update(
        database: Session,
        question_id: int,
        data: QuestionUpdate,
    ) -> Question:
        question = QuestionService.get_by_id(
            database=database,
            question_id=question_id,
        )

        changes = data.model_dump(
            exclude_unset=True,
        )

        if "category_id" in changes:
            QuestionService.validate_category(
                database=database,
                category_id=changes["category_id"],
            )

        if "question_text" in changes:
            normalized_text = normalize_text(
                changes["question_text"]
            )

            duplicate = (
                QuestionRepository.get_by_normalized_text(
                    database=database,
                    normalized_text=normalized_text,
                )
            )

            if (
                duplicate is not None
                and duplicate.id != question.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe una pregunta equivalente.",
                )

            changes["normalized_text"] = normalized_text

        try:
            return QuestionRepository.update(
                database=database,
                question=question,
                changes=changes,
            )
        except IntegrityError as error:
            database.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible actualizar la pregunta.",
            ) from error

    @staticmethod
    def delete(
        database: Session,
        question_id: int,
    ) -> None:
        question = QuestionService.get_by_id(
            database=database,
            question_id=question_id,
        )

        QuestionRepository.delete(
            database=database,
            question=question,
        )
