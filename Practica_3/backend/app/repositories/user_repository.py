from typing import Any

from psycopg import Connection


USER_COLUMNS = """
    id,
    full_name,
    username::TEXT AS username,
    email::TEXT AS email,
    password_hash,
    role::TEXT AS role,
    is_active,
    last_login_at,
    created_at,
    updated_at
"""


def find_user_by_identifier(
    connection: Connection,
    identifier: str,
) -> dict[str, Any] | None:
    query = f"""
        SELECT {USER_COLUMNS}
        FROM users
        WHERE username = %s
           OR email = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (identifier, identifier),
        )
        return cursor.fetchone()


def find_user_by_id(
    connection: Connection,
    user_id: int,
) -> dict[str, Any] | None:
    query = f"""
        SELECT {USER_COLUMNS}
        FROM users
        WHERE id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (user_id,))
        return cursor.fetchone()


def update_last_login(
    connection: Connection,
    user_id: int,
) -> None:
    query = """
        UPDATE users
        SET last_login_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (user_id,))

    connection.commit()
