from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class QuestionSummary(BaseModel):
    id: int
    question_text: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AnswerCreate(BaseModel):
    question_id: int = Field(gt=0)

    answer_text: str = Field(
        min_length=2,
        max_length=4000,
    )

    is_active: bool = True

    @field_validator("answer_text")
    @classmethod
    def validate_answer_text(cls, value: str) -> str:
        clean_value = " ".join(value.split())

        if not clean_value:
            raise ValueError("La respuesta es obligatoria.")

        return clean_value


class AnswerUpdate(BaseModel):
    question_id: int | None = Field(
        default=None,
        gt=0,
    )

    answer_text: str | None = Field(
        default=None,
        min_length=2,
        max_length=4000,
    )

    is_active: bool | None = None

    @field_validator("answer_text")
    @classmethod
    def validate_answer_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        clean_value = " ".join(value.split())

        if not clean_value:
            raise ValueError("La respuesta es obligatoria.")

        return clean_value

    @model_validator(mode="after")
    def validate_changes(self) -> "AnswerUpdate":
        if not self.model_fields_set:
            raise ValueError(
                "Debe proporcionar al menos un campo para actualizar."
            )

        if (
            "question_id" in self.model_fields_set
            and self.question_id is None
        ):
            raise ValueError(
                "La pregunta no puede ser nula."
            )

        if (
            "answer_text" in self.model_fields_set
            and self.answer_text is None
        ):
            raise ValueError(
                "La respuesta no puede ser nula."
            )

        return self


class AnswerResponse(BaseModel):
    id: int
    question_id: int
    answer_text: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    question: QuestionSummary

    model_config = ConfigDict(from_attributes=True)
