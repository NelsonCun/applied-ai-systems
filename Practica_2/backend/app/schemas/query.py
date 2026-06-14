from pydantic import BaseModel, Field, field_validator


class QueryResolveRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=500,
    )

    telegram_user_id: int | None = None
    telegram_username: str | None = Field(
        default=None,
        max_length=150,
    )
    telegram_first_name: str | None = Field(
        default=None,
        max_length=150,
    )
    telegram_chat_id: int | None = None

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        clean_value = " ".join(value.split())

        if not clean_value:
            raise ValueError("La consulta es obligatoria.")

        return clean_value


class QueryResolveResponse(BaseModel):
    answer: str
    matched: bool
    question_id: int | None
    category_id: int | None
    category_name: str | None
    confidence: float = Field(
        ge=0,
        le=1,
    )
