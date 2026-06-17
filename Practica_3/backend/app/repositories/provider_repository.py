from typing import Any

from psycopg import Connection


PROVIDER_COLUMNS = """
    provider.id,
    provider.name,
    provider.nit::TEXT AS nit,
    provider.email::TEXT AS email,
    provider.phone,
    provider.address,
    provider.category_id,
    category.name::TEXT AS category_name,
    provider.is_active,
    provider.created_by,
    provider.created_at,
    provider.updated_at
"""


def list_categories(
    connection: Connection,
) -> list[dict[str, Any]]:
    query = """
        SELECT
            id,
            name::TEXT AS name,
            description,
            is_active
        FROM invoice_categories
        WHERE is_active = TRUE
        ORDER BY name
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def category_exists(
    connection: Connection,
    category_id: int,
) -> bool:
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM invoice_categories
            WHERE id = %s
              AND is_active = TRUE
        ) AS exists
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (category_id,))
        row = cursor.fetchone()

    return bool(row["exists"])


def find_provider_by_id(
    connection: Connection,
    provider_id: int,
) -> dict[str, Any] | None:
    query = f"""
        SELECT {PROVIDER_COLUMNS}
        FROM providers provider
        LEFT JOIN invoice_categories category
            ON category.id = provider.category_id
        WHERE provider.id = %s
        LIMIT 1
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (provider_id,))
        return cursor.fetchone()


def find_provider_by_nit(
    connection: Connection,
    nit: str,
    excluded_id: int | None = None,
) -> dict[str, Any] | None:
    parameters: list[Any] = [nit]

    query = """
        SELECT id, name, nit::TEXT AS nit
        FROM providers
        WHERE nit = %s
    """

    if excluded_id is not None:
        query += " AND id <> %s"
        parameters.append(excluded_id)

    query += " LIMIT 1"

    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        return cursor.fetchone()


def list_providers(
    connection: Connection,
    page: int,
    page_size: int,
    search: str | None,
    is_active: bool | None,
    category_id: int | None,
) -> tuple[list[dict[str, Any]], int]:
    conditions: list[str] = []
    parameters: list[Any] = []

    if search:
        search_value = f"%{search.strip()}%"
        conditions.append(
            """
            (
                provider.name ILIKE %s
                OR provider.nit::TEXT ILIKE %s
                OR COALESCE(provider.email::TEXT, '') ILIKE %s
            )
            """
        )
        parameters.extend(
            [search_value, search_value, search_value]
        )

    if is_active is not None:
        conditions.append("provider.is_active = %s")
        parameters.append(is_active)

    if category_id is not None:
        conditions.append("provider.category_id = %s")
        parameters.append(category_id)

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    count_query = f"""
        SELECT COUNT(*) AS total
        FROM providers provider
        {where_clause}
    """

    with connection.cursor() as cursor:
        cursor.execute(count_query, parameters)
        total = int(cursor.fetchone()["total"])

    offset = (page - 1) * page_size

    list_query = f"""
        SELECT {PROVIDER_COLUMNS}
        FROM providers provider
        LEFT JOIN invoice_categories category
            ON category.id = provider.category_id
        {where_clause}
        ORDER BY provider.created_at DESC, provider.id DESC
        LIMIT %s
        OFFSET %s
    """

    list_parameters = [
        *parameters,
        page_size,
        offset,
    ]

    with connection.cursor() as cursor:
        cursor.execute(
            list_query,
            list_parameters,
        )
        providers = cursor.fetchall()

    return providers, total


def create_provider(
    connection: Connection,
    data: dict[str, Any],
    created_by: int,
) -> dict[str, Any]:
    query = """
        INSERT INTO providers (
            name,
            nit,
            email,
            phone,
            address,
            category_id,
            created_by
        )
        VALUES (
            %(name)s,
            %(nit)s,
            %(email)s,
            %(phone)s,
            %(address)s,
            %(category_id)s,
            %(created_by)s
        )
        RETURNING id
    """

    parameters = {
        **data,
        "created_by": created_by,
    }

    with connection.cursor() as cursor:
        cursor.execute(query, parameters)
        provider_id = cursor.fetchone()["id"]

    connection.commit()

    provider = find_provider_by_id(
        connection,
        provider_id,
    )

    if provider is None:
        raise RuntimeError(
            "No fue posible recuperar el proveedor creado"
        )

    return provider


def update_provider(
    connection: Connection,
    provider_id: int,
    data: dict[str, Any],
) -> dict[str, Any] | None:
    query = """
        UPDATE providers
        SET
            name = %(name)s,
            nit = %(nit)s,
            email = %(email)s,
            phone = %(phone)s,
            address = %(address)s,
            category_id = %(category_id)s
        WHERE id = %(provider_id)s
    """

    parameters = {
        **data,
        "provider_id": provider_id,
    }

    with connection.cursor() as cursor:
        cursor.execute(query, parameters)

        if cursor.rowcount == 0:
            connection.rollback()
            return None

    connection.commit()

    return find_provider_by_id(
        connection,
        provider_id,
    )


def change_provider_status(
    connection: Connection,
    provider_id: int,
    is_active: bool,
) -> dict[str, Any] | None:
    query = """
        UPDATE providers
        SET is_active = %s
        WHERE id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (is_active, provider_id),
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return None

    connection.commit()

    return find_provider_by_id(
        connection,
        provider_id,
    )
