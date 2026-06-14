from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Answer


class AnswerRepository:
    @staticmethod
    def list_all(
        database: Session,
        is_active: bool | None = None,
    ) -> list[Answer]:
        statement = select(Answer).options(
            selectinload(Answer.question)
        )

        if is_active is not None:
            statement = statement.where(
                Answer.is_active.is_(is_active)
            )

        statement = statement.order_by(
            Answer.id.desc()
        )

        return list(database.scalars(statement).all())

    @staticmethod
    def get_by_id(
        database: Session,
        answer_id: int,
    ) -> Answer | None:
        statement = (
            select(Answer)
            .options(selectinload(Answer.question))
            .where(Answer.id == answer_id)
        )

        return database.scalar(statement)

    @staticmethod
    def get_by_question_id(
        database: Session,
        question_id: int,
    ) -> Answer | None:
        statement = select(Answer).where(
            Answer.question_id == question_id
        )

        return database.scalar(statement)

    @staticmethod
    def create(
        database: Session,
        question_id: int,
        answer_text: str,
        is_active: bool,
    ) -> Answer:
        answer = Answer(
            question_id=question_id,
            answer_text=answer_text,
            is_active=is_active,
        )

        database.add(answer)
        database.commit()
        database.refresh(answer)
        database.expire_all()

        created_answer = AnswerRepository.get_by_id(
            database=database,
            answer_id=answer.id,
        )

        if created_answer is None:
            raise RuntimeError(
                "No fue posible recuperar la respuesta creada."
            )

        return created_answer

    @staticmethod
    def update(
        database: Session,
        answer: Answer,
        changes: dict,
    ) -> Answer:
        for field, value in changes.items():
            setattr(answer, field, value)

        database.commit()
        database.refresh(answer)
        database.expire_all()

        updated_answer = AnswerRepository.get_by_id(
            database=database,
            answer_id=answer.id,
        )

        if updated_answer is None:
            raise RuntimeError(
                "No fue posible recuperar la respuesta actualizada."
            )

        return updated_answer

    @staticmethod
    def delete(
        database: Session,
        answer: Answer,
    ) -> None:
        database.delete(answer)
        database.commit()
