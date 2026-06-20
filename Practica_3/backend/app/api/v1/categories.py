from typing import Annotated, Any

from fastapi import APIRouter, Depends
from psycopg import Connection

from app.api.dependencies import get_current_user
from app.db.connection import get_connection
from app.repositories.provider_repository import (
    list_categories,
)
from app.schemas.provider import CategoryResponse


router = APIRouter(
    prefix="/categories",
    tags=["Categorías"],
)


@router.get(
    "",
    response_model=list[CategoryResponse],
    summary="Listar categorías activas",
)
def get_categories(
    connection: Annotated[
        Connection,
        Depends(get_connection),
    ],
    current_user: Annotated[
        dict[str, Any],
        Depends(get_current_user),
    ],
) -> list[CategoryResponse]:
    del current_user

    return [
        CategoryResponse(**category)
        for category in list_categories(connection)
    ]
