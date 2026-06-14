from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Answer, Category, Question


class QuestionRepository:
    @staticmethod
    def list_all(
        database: Session,
        search: str | None = None,
        category_id: int | None = None,
        is_active: bool | None = None,
    ) -> list[Question]:
        statement = (
            select(Question)
            .options(
                selectinload(Question.category),
                selectinload(Question.answer),
            )
        )

        if search:
            pattern = f"%{search.strip()}%"

            statement = statement.where(
                or_(
                    Question.question_text.ilike(pattern),
                    Question.normalized_text.ilike(pattern),
                )
            )

        if category_id is not None:
            statement = statement.where(
                Question.category_id == category_id
            )

        if is_active is not None:
            statement = statement.where(
                Question.is_active.is_(is_active)
            )

        statement = statement.order_by(
            Question.id.desc()
        )

        return list(database.scalars(statement).all())

    @staticmethod
    def get_by_id(
        database: Session,
        question_id: int,
    ) -> Question | None:
        statement = (
            select(Question)
            .options(
                selectinload(Question.category),
                selectinload(Question.answer),
            )
            .where(Question.id == question_id)
        )

        return database.scalar(statement)

    @staticmethod
    def get_by_normalized_text(
        database: Session,
        normalized_text: str,
    ) -> Question | None:
        statement = select(Question).where(
            Question.normalized_text == normalized_text
        )

        return database.scalar(statement)

    @staticmethod
    def create(
        database: Session,
        category_id: int,
        question_text: str,
        normalized_text: str,
        is_active: bool,
    ) -> Question:
        question = Question(
            category_id=category_id,
            question_text=question_text,
            normalized_text=normalized_text,
            is_active=is_active,
        )

        database.add(question)
        database.commit()
        database.refresh(question)
        database.expire_all()

        created_question = QuestionRepository.get_by_id(
            database=database,
            question_id=question.id,
        )

        if created_question is None:
            raise RuntimeError(
                "No fue posible recuperar la pregunta creada."
            )

        return created_question

    @staticmethod
    def update(
        database: Session,
        question: Question,
        changes: dict,
    ) -> Question:
        for field, value in changes.items():
            setattr(question, field, value)

        database.commit()
        database.refresh(question)
        database.expire_all()

        updated_question = QuestionRepository.get_by_id(
            database=database,
            question_id=question.id,
        )

        if updated_question is None:
            raise RuntimeError(
                "No fue posible recuperar la pregunta actualizada."
            )

        return updated_question

    @staticmethod
    def delete(
        database: Session,
        question: Question,
    ) -> None:
        database.delete(question)
        database.commit()

    @staticmethod
    def find_exact_answer(
        database: Session,
        normalized_query: str,
    ) -> Question | None:
        statement = (
            select(Question)
            .join(Question.category)
            .join(Question.answer)
            .options(
                selectinload(Question.category),
                selectinload(Question.answer),
            )
            .where(
                Question.normalized_text == normalized_query,
                Question.is_active.is_(True),
                Category.is_active.is_(True),
                Answer.is_active.is_(True),
            )
        )

        return database.scalar(statement)

    @staticmethod
    def list_answerable(
        database: Session,
    ) -> list[Question]:
        statement = (
            select(Question)
            .join(Question.category)
            .join(Question.answer)
            .options(
                selectinload(Question.category),
                selectinload(Question.answer),
            )
            .where(
                Question.is_active.is_(True),
                Category.is_active.is_(True),
                Answer.is_active.is_(True),
            )
            .order_by(Question.id.asc())
        )

        return list(database.scalars(statement).all())
