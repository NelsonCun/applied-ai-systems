import re

from pydantic import BaseModel, Field, field_validator


IDENTIFICADOR_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*$"
)

CHAT_ID_PATTERN = re.compile(
    r"^-?[0-9]+$"
)


class DiagnosticoRequest(BaseModel):
    sintomas: list[str] = Field(
        min_length=1,
        max_length=100
    )

    telegram_chat_id: str | None = None

    @field_validator("sintomas")
    @classmethod
    def validar_sintomas(
        cls,
        sintomas: list[str]
    ) -> list[str]:
        sintomas_limpios: list[str] = []

        for sintoma in sintomas:
            sintoma_limpio = sintoma.strip()

            if not IDENTIFICADOR_PATTERN.fullmatch(
                sintoma_limpio
            ):
                raise ValueError(
                    f"El síntoma '{sintoma}' tiene un formato inválido."
                )

            if sintoma_limpio not in sintomas_limpios:
                sintomas_limpios.append(
                    sintoma_limpio
                )

        if not sintomas_limpios:
            raise ValueError(
                "Debe seleccionar al menos un síntoma."
            )

        return sintomas_limpios

    @field_validator("telegram_chat_id")
    @classmethod
    def validar_telegram_chat_id(
        cls,
        chat_id: str | None
    ) -> str | None:
        if chat_id is None:
            return None

        chat_id_limpio = chat_id.strip()

        if not chat_id_limpio:
            return None

        if not CHAT_ID_PATTERN.fullmatch(
            chat_id_limpio
        ):
            raise ValueError(
                "El ID de Telegram debe ser numérico."
            )

        return chat_id_limpio


class DiagnosticoResponse(BaseModel):
    falla: str
    falla_texto: str
    recomendacion: str
    coincidencias: int
    sintomas: list[str]
    telegram_enviado: bool