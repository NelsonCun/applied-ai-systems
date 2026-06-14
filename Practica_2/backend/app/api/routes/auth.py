from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.auth import (
    AdminUserResponse,
    LoginRequest,
    LoginResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    credentials: LoginRequest,
    database: Session = Depends(get_db),
) -> LoginResponse:
    return AuthService.login(
        database=database,
        credentials=credentials,
    )


@router.get(
    "/me",
    response_model=AdminUserResponse,
)
def get_authenticated_user(
    current_user: AdminUser = Depends(get_current_admin),
) -> AdminUser:
    return current_user
