import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.repositories.admin_user_repository import (
    AdminUserRepository,
)


bearer_scheme = HTTPBearer(
    auto_error=False,
)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    database: Session = Depends(get_db),
) -> AdminUser:
    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la sesión.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    if credentials is None:
        raise authentication_error

    if credentials.scheme.lower() != "bearer":
        raise authentication_error

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        subject = payload.get("sub")

        if subject is None:
            raise authentication_error

        user_id = int(subject)
    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        TypeError,
        ValueError,
    ) as error:
        raise authentication_error from error

    user = AdminUserRepository.get_by_id(
        database=database,
        user_id=user_id,
    )

    if user is None:
        raise authentication_error

    return user
