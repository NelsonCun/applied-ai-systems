from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=100,
        examples=["IA1-User"],
    )

    password: str = Field(
        min_length=1,
        max_length=200,
        examples=["IA1-password@_new"],
    )


class AdminUserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: AdminUserResponse
