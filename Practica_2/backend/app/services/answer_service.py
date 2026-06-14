from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Answer
from app.repositories.answer_repository import (
    AnswerRepository,
)
from app.repositories.question_repository import (
    QuestionRepository,
)
from app.schemas.answer import AnswerCreate, AnswerUpdate


class AnswerService:
    @staticmethod
    def list_all(
        database: Session,
        is_active: bool | None,
    ) -> list[Answer]:
        return AnswerRepository.list_all(
            database=database,
            is_active=is_active,
        )

    @staticmethod
    def get_by_id(
        database: Session,
        answer_id: int,
    ) -> Answer:
        answer = AnswerRepository.get_by_id(
            database=database,
            answer_id=answer_id,
        )

        if answer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La respuesta solicitada no existe.",
            )

        return answer

    @staticmethod
    def validate_question(
        database: Session,
        question_id: int,
    ) -> None:
        question = QuestionRepository.get_by_id(
            database=database,
            question_id=question_id,
        )

        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La pregunta seleccionada no existe.",
            )

    @staticmethod
    def create(
        database: Session,
        data: AnswerCreate,
    ) -> Answer:
        AnswerService.validate_question(
            database=database,
            question_id=data.question_id,
        )

        duplicate = AnswerRepository.get_by_question_id(
            database=database,
            question_id=data.question_id,
        )

        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "La pregunta ya tiene una respuesta asociada."
                ),
            )

        try:
            return AnswerRepository.create(
                database=database,
                question_id=data.question_id,
                answer_text=data.answer_text,
                is_active=data.is_active,
            )
        except IntegrityError as error:
            database.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible crear la respuesta.",
            ) from error

    @staticmethod
    def update(
        database: Session,
        answer_id: int,
        data: AnswerUpdate,
    ) -> Answer:
        answer = AnswerService.get_by_id(
            database=database,
            answer_id=answer_id,
        )

        changes = data.model_dump(
            exclude_unset=True,
        )

        if "question_id" in changes:
            new_question_id = changes["question_id"]

            AnswerService.validate_question(
                database=database,
                question_id=new_question_id,
            )

            duplicate = AnswerRepository.get_by_question_id(
                database=database,
                question_id=new_question_id,
            )

            if (
                duplicate is not None
                and duplicate.id != answer.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "La pregunta ya tiene una respuesta asociada."
                    ),
                )

        try:
            return AnswerRepository.update(
                database=database,
                answer=answer,
                changes=changes,
            )
        except IntegrityError as error:
            database.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible actualizar la respuesta.",
            ) from error

    @staticmethod
    def delete(
        database: Session,
        answer_id: int,
    ) -> None:
        answer = AnswerService.get_by_id(
            database=database,
            answer_id=answer_id,
        )

        AnswerRepository.delete(
            database=database,
            answer=answer,
        )
