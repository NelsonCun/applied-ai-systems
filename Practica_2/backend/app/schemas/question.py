from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class CategorySummary(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class AnswerSummary(BaseModel):
    id: int
    answer_text: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseModel):
    category_id: int = Field(gt=0)

    question_text: str = Field(
        min_length=2,
        max_length=500,
    )

    is_active: bool = True

    @field_validator("question_text")
    @classmethod
    def validate_question_text(cls, value: str) -> str:
        clean_value = " ".join(value.split())

        if not clean_value:
            raise ValueError("La pregunta es obligatoria.")

        return clean_value


class QuestionUpdate(BaseModel):
    category_id: int | None = Field(
        default=None,
        gt=0,
    )

    question_text: str | None = Field(
        default=None,
        min_length=2,
        max_length=500,
    )

    is_active: bool | None = None

    @field_validator("question_text")
    @classmethod
    def validate_question_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        clean_value = " ".join(value.split())

        if not clean_value:
            raise ValueError("La pregunta es obligatoria.")

        return clean_value

    @model_validator(mode="after")
    def validate_changes(self) -> "QuestionUpdate":
        if not self.model_fields_set:
            raise ValueError(
                "Debe proporcionar al menos un campo para actualizar."
            )

        if (
            "category_id" in self.model_fields_set
            and self.category_id is None
        ):
            raise ValueError(
                "La categoría no puede ser nula."
            )

        if (
            "question_text" in self.model_fields_set
            and self.question_text is None
        ):
            raise ValueError(
                "La pregunta no puede ser nula."
            )

        return self


class QuestionResponse(BaseModel):
    id: int
    category_id: int
    question_text: str
    normalized_text: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: CategorySummary
    answer: AnswerSummary | None

    model_config = ConfigDict(from_attributes=True)
