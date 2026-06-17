from collections.abc import Generator

from psycopg import Connection
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import settings


pool = ConnectionPool(
    conninfo=settings.database_url,
    min_size=1,
    max_size=10,
    kwargs={
        "autocommit": False,
        "row_factory": dict_row,
    },
    open=False,
)


def open_pool() -> None:
    if pool.closed:
        pool.open(wait=True)


def close_pool() -> None:
    if not pool.closed:
        pool.close()


def get_connection() -> Generator[Connection, None, None]:
    with pool.connection() as connection:
        yield connection
