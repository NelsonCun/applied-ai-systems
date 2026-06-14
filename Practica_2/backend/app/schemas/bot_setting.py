from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class BotSettingUpdate(BaseModel):
    hospital_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    telegram_chat_id: str | None = Field(
        default=None,
        max_length=100,
    )

    bot_username: str | None = Field(
        default=None,
        max_length=100,
    )

    welcome_message: str | None = Field(
        default=None,
        min_length=2,
        max_length=2000,
    )

    unknown_question_message: str | None = Field(
        default=None,
        min_length=2,
        max_length=2000,
    )

    is_active: bool | None = None

    @field_validator(
        "hospital_name",
        "welcome_message",
        "unknown_question_message",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        clean_value = " ".join(value.split())

        if not clean_value:
            raise ValueError("El campo no puede estar vacío.")

        return clean_value

    @field_validator(
        "telegram_chat_id",
        "bot_username",
    )
    @classmethod
    def validate_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        clean_value = value.strip()

        return clean_value or None

    @model_validator(mode="after")
    def validate_changes(self) -> "BotSettingUpdate":
        if not self.model_fields_set:
            raise ValueError(
                "Debe proporcionar al menos un campo para actualizar."
            )

        required_fields = {
            "hospital_name",
            "welcome_message",
            "unknown_question_message",
            "is_active",
        }

        for field_name in required_fields:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(
                    f"El campo {field_name} no puede ser nulo."
                )

        return self


class BotSettingResponse(BaseModel):
    id: int
    hospital_name: str
    telegram_chat_id: str | None
    bot_username: str | None
    welcome_message: str
    unknown_question_message: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicBotConfigResponse(BaseModel):
    hospital_name: str
    welcome_message: str
    is_active: bool


class TelegramTestRequest(BaseModel):
    chat_id: str | None = Field(
        default=None,
        max_length=100,
    )

    message: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("chat_id", "message")
    @classmethod
    def clean_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        clean_value = value.strip()

        return clean_value or None


class TelegramTestResponse(BaseModel):
    success: bool
    chat_id: str
    message_id: int | None
    detail: str
