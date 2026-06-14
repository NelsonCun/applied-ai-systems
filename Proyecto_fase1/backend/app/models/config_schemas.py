import re

from pydantic import BaseModel, Field, field_validator


CHAT_ID_PATTERN = re.compile(r"^-?[0-9]+$")


class TelegramConfigUpdate(BaseModel):
    activo: bool
    chat_id: str = Field(max_length=32)
    mensaje_bienvenida: str = Field(min_length=2, max_length=300)
    encabezado_diagnostico: str = Field(min_length=2, max_length=300)
    mensaje_despedida: str = Field(min_length=2, max_length=500)

    @field_validator("chat_id")
    @classmethod
    def validar_chat_id(cls, valor: str) -> str:
        valor_limpio = valor.strip()

        if valor_limpio and not CHAT_ID_PATTERN.fullmatch(valor_limpio):
            raise ValueError("El ID de Telegram debe ser numérico.")

        return valor_limpio

    @field_validator(
        "mensaje_bienvenida",
        "encabezado_diagnostico",
        "mensaje_despedida",
    )
    @classmethod
    def limpiar_mensajes(cls, valor: str) -> str:
        valor_limpio = valor.strip()

        if not valor_limpio:
            raise ValueError("El mensaje no puede estar vacío.")

        return valor_limpio
