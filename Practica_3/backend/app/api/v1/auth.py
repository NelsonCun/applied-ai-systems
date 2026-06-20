from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_password,
)
from app.db.connection import get_connection
from app.repositories.user_repository import (
    find_user_by_id,
    find_user_by_identifier,
    update_last_login,
)
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
)
def login(
    request: LoginRequest,
    connection: Annotated[
        Connection,
        Depends(get_connection),
    ],
) -> TokenResponse:
    identifier = request.identifier.strip()

    user = find_user_by_identifier(
        connection,
        identifier,
    )

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuario o contraseña incorrectos",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if user is None:
        raise invalid_credentials

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario se encuentra desactivado",
        )

    if not verify_password(
        request.password,
        user["password_hash"],
    ):
        raise invalid_credentials

    update_last_login(
        connection,
        user["id"],
    )

    updated_user = find_user_by_id(
        connection,
        user["id"],
    )

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible recuperar el usuario",
        )

    access_token = create_access_token(
        subject=str(updated_user["id"]),
        role=updated_user["role"],
    )

    updated_user.pop("password_hash", None)

    return TokenResponse(
        access_token=access_token,
        expires_in=(
            settings.access_token_expire_minutes * 60
        ),
        user=UserResponse(**updated_user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario autenticado",
)
def get_me(
    current_user: Annotated[
        dict[str, Any],
        Depends(get_current_user),
    ],
) -> UserResponse:
    return UserResponse(**current_user)
