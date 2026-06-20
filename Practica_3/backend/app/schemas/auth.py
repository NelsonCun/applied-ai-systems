from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    identifier: str = Field(
        min_length=3,
        max_length=255,
        description="Nombre de usuario o correo electrónico",
    )
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    id: int
    full_name: str
    username: str
    email: EmailStr
    role: str
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
