from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.repositories.admin_user_repository import (
    AdminUserRepository,
)
from app.schemas.auth import LoginRequest, LoginResponse


class AuthService:
    @staticmethod
    def login(
        database: Session,
        credentials: LoginRequest,
    ) -> LoginResponse:
        username = credentials.username.strip()

        user = AdminUserRepository.authenticate(
            database=database,
            username=username,
            password=credentials.password,
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos.",
                headers={
                    "WWW-Authenticate": "Bearer",
                },
            )

        token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "username": user.username,
            },
        )

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            expires_in_minutes=(
                settings.access_token_expire_minutes
            ),
            user=user,
        )
