from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from psycopg import Connection

from app.core.security import decode_access_token
from app.db.connection import get_connection
from app.repositories.user_repository import find_user_by_id


bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Token JWT obtenido en /api/v1/auth/login",
)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    connection: Annotated[
        Connection,
        Depends(get_connection),
    ],
) -> dict[str, Any]:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    if credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        payload = decode_access_token(
            credentials.credentials
        )
        user_id = int(payload["sub"])
    except (ValueError, TypeError, KeyError):
        raise unauthorized

    user = find_user_by_id(connection, user_id)

    if user is None or not user["is_active"]:
        raise unauthorized

    user.pop("password_hash", None)

    return user


def require_admin(
    current_user: Annotated[
        dict[str, Any],
        Depends(get_current_user),
    ],
) -> dict[str, Any]:
    if current_user["role"] != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador",
        )

    return current_user
