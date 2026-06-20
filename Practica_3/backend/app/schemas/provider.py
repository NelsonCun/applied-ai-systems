from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

from app.core.nit import (
    normalize_nit,
    validate_nit_format,
)


class ProviderBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=180,
    )
    nit: str = Field(
        min_length=2,
        max_length=30,
    )
    email: EmailStr | None = None
    phone: str | None = Field(
        default=None,
        max_length=30,
    )
    address: str | None = Field(
        default=None,
        max_length=500,
    )
    category_id: int | None = Field(
        default=None,
        gt=0,
    )

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("nit")
    @classmethod
    def validate_nit(cls, value: str) -> str:
        normalized = normalize_nit(value)

        if not validate_nit_format(normalized):
            raise ValueError(
                "El NIT debe ser CF, nueve dígitos o utilizar "
                "el formato histórico con guion"
            )

        return normalized

    @field_validator(
        "phone",
        "address",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None

    @field_validator(
        "email",
        mode="before",
    )
    @classmethod
    def empty_email_to_none(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(ProviderBase):
    pass


class ProviderStatusUpdate(BaseModel):
    is_active: bool


class ProviderResponse(BaseModel):
    id: int
    name: str
    nit: str
    email: EmailStr | None
    phone: str | None
    address: str | None
    category_id: int | None
    category_name: str | None
    is_active: bool
    created_by: int | None
    created_at: datetime
    updated_at: datetime


class ProviderListResponse(BaseModel):
    items: list[ProviderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
