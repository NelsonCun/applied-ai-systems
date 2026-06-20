from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings


def verify_password(
    plain_password: str,
    password_hash: str,
) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (TypeError, ValueError):
        return False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12),
    ).decode("utf-8")


def create_access_token(
    subject: str,
    role: str,
) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={
                "require": [
                    "sub",
                    "iat",
                    "exp",
                    "type",
                ]
            },
        )
    except InvalidTokenError as error:
        raise ValueError(
            "Token inválido o expirado"
        ) from error

    if payload.get("type") != "access":
        raise ValueError("Tipo de token inválido")

    return payload
