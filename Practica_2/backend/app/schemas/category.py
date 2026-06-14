from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class CategoryBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Citas y admisiones"],
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
        examples=[
            "Información relacionada con citas, registro y admisión."
        ],
    )

    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        clean_value = " ".join(value.split())

        if not clean_value:
            raise ValueError("El nombre de la categoría es obligatorio.")

        return clean_value

    @field_validator("description")
    @classmethod
    def validate_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        clean_value = value.strip()

        return clean_value or None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        clean_value = " ".join(value.split())

        if not clean_value:
            raise ValueError("El nombre de la categoría es obligatorio.")

        return clean_value

    @field_validator("description")
    @classmethod
    def validate_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        clean_value = value.strip()

        return clean_value or None

    @model_validator(mode="after")
    def validate_changes(self) -> "CategoryUpdate":
        fields_received = self.model_fields_set

        if not fields_received:
            raise ValueError(
                "Debe proporcionar al menos un campo para actualizar."
            )

        return self


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
