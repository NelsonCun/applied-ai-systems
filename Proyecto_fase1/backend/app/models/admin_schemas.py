import re

from pydantic import BaseModel, Field, field_validator


IDENTIFICADOR_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def validar_identificador(valor: str) -> str:
    valor_limpio = valor.strip()

    if not IDENTIFICADOR_PATTERN.fullmatch(valor_limpio):
        raise ValueError(
            "El identificador debe iniciar con una letra minúscula "
            "y contener únicamente letras minúsculas, números o guion bajo."
        )

    return valor_limpio


def validar_texto(valor: str) -> str:
    valor_limpio = valor.strip()

    if not valor_limpio:
        raise ValueError("El texto no puede estar vacío.")

    return valor_limpio


class SintomaCreate(BaseModel):
    id: str
    nombre: str = Field(min_length=2, max_length=150)
    categoria: str = Field(min_length=2, max_length=100)

    @field_validator("id")
    @classmethod
    def validar_id(cls, valor: str) -> str:
        return validar_identificador(valor)

    @field_validator("nombre", "categoria")
    @classmethod
    def limpiar_textos(cls, valor: str) -> str:
        return validar_texto(valor)


class SintomaUpdate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    categoria: str = Field(min_length=2, max_length=100)

    @field_validator("nombre", "categoria")
    @classmethod
    def limpiar_textos(cls, valor: str) -> str:
        return validar_texto(valor)


class FallaCreate(BaseModel):
    id: str
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: str = Field(min_length=5, max_length=500)

    @field_validator("id")
    @classmethod
    def validar_id(cls, valor: str) -> str:
        return validar_identificador(valor)

    @field_validator("nombre", "descripcion")
    @classmethod
    def limpiar_textos(cls, valor: str) -> str:
        return validar_texto(valor)


class FallaUpdate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: str = Field(min_length=5, max_length=500)

    @field_validator("nombre", "descripcion")
    @classmethod
    def limpiar_textos(cls, valor: str) -> str:
        return validar_texto(valor)


class RecomendacionCreate(BaseModel):
    id: str
    falla_id: str
    texto: str = Field(min_length=5, max_length=1000)

    @field_validator("id", "falla_id")
    @classmethod
    def validar_ids(cls, valor: str) -> str:
        return validar_identificador(valor)

    @field_validator("texto")
    @classmethod
    def limpiar_texto(cls, valor: str) -> str:
        return validar_texto(valor)


class RecomendacionUpdate(BaseModel):
    falla_id: str
    texto: str = Field(min_length=5, max_length=1000)

    @field_validator("falla_id")
    @classmethod
    def validar_falla(cls, valor: str) -> str:
        return validar_identificador(valor)

    @field_validator("texto")
    @classmethod
    def limpiar_texto(cls, valor: str) -> str:
        return validar_texto(valor)


class ReglaCreate(BaseModel):
    id: str
    falla_id: str
    sintomas: list[str] = Field(min_length=1, max_length=50)

    @field_validator("id", "falla_id")
    @classmethod
    def validar_ids(cls, valor: str) -> str:
        return validar_identificador(valor)

    @field_validator("sintomas")
    @classmethod
    def validar_sintomas(cls, valores: list[str]) -> list[str]:
        resultado: list[str] = []

        for valor in valores:
            identificador = validar_identificador(valor)

            if identificador not in resultado:
                resultado.append(identificador)

        return resultado


class ReglaUpdate(BaseModel):
    falla_id: str
    sintomas: list[str] = Field(min_length=1, max_length=50)

    @field_validator("falla_id")
    @classmethod
    def validar_falla(cls, valor: str) -> str:
        return validar_identificador(valor)

    @field_validator("sintomas")
    @classmethod
    def validar_sintomas(cls, valores: list[str]) -> list[str]:
        resultado: list[str] = []

        for valor in valores:
            identificador = validar_identificador(valor)

            if identificador not in resultado:
                resultado.append(identificador)

        return resultado
