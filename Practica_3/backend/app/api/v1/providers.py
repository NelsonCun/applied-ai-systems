from math import ceil
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from psycopg import Connection
from psycopg.errors import UniqueViolation

from app.api.dependencies import (
    get_current_user,
    require_admin,
)
from app.db.connection import get_connection
from app.repositories.provider_repository import (
    category_exists,
    change_provider_status,
    create_provider,
    find_provider_by_id,
    find_provider_by_nit,
    list_providers,
    update_provider,
)
from app.schemas.provider import (
    ProviderCreate,
    ProviderListResponse,
    ProviderResponse,
    ProviderStatusUpdate,
    ProviderUpdate,
)


router = APIRouter(
    prefix="/providers",
    tags=["Proveedores"],
)


def validate_category(
    connection: Connection,
    category_id: int | None,
) -> None:
    if category_id is None:
        return

    if not category_exists(connection, category_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La categoría indicada no existe o está inactiva",
        )


@router.get(
    "",
    response_model=ProviderListResponse,
    summary="Listar proveedores",
)
def get_providers(
    connection: Annotated[
        Connection,
        Depends(get_connection),
    ],
    current_user: Annotated[
        dict[str, Any],
        Depends(get_current_user),
    ],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[
        str | None,
        Query(max_length=180),
    ] = None,
    is_active: bool | None = None,
    category_id: Annotated[
        int | None,
        Query(gt=0),
    ] = None,
) -> ProviderListResponse:
    del current_user

    providers, total = list_providers(
        connection=connection,
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
        category_id=category_id,
    )

    total_pages = (
        ceil(total / page_size)
        if total > 0
        else 0
    )

    return ProviderListResponse(
        items=[
            ProviderResponse(**provider)
            for provider in providers
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{provider_id}",
    response_model=ProviderResponse,
    summary="Consultar un proveedor",
)
def get_provider(
    provider_id: int,
    connection: Annotated[
        Connection,
        Depends(get_connection),
    ],
    current_user: Annotated[
        dict[str, Any],
        Depends(get_current_user),
    ],
) -> ProviderResponse:
    del current_user

    provider = find_provider_by_id(
        connection,
        provider_id,
    )

    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado",
        )

    return ProviderResponse(**provider)


@router.post(
    "",
    response_model=ProviderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear proveedor",
)
def post_provider(
    request: ProviderCreate,
    connection: Annotated[
        Connection,
        Depends(get_connection),
    ],
    current_user: Annotated[
        dict[str, Any],
        Depends(require_admin),
    ],
) -> ProviderResponse:
    validate_category(
        connection,
        request.category_id,
    )

    existing_provider = find_provider_by_nit(
        connection,
        request.nit,
    )

    if existing_provider is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un proveedor con ese NIT",
        )

    try:
        provider = create_provider(
            connection=connection,
            data=request.model_dump(),
            created_by=current_user["id"],
        )
    except UniqueViolation as error:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un proveedor con esos datos",
        ) from error

    return ProviderResponse(**provider)


@router.put(
    "/{provider_id}",
    response_model=ProviderResponse,
    summary="Actualizar proveedor",
)
def put_provider(
    provider_id: int,
    request: ProviderUpdate,
    connection: Annotated[
        Connection,
        Depends(get_connection),
    ],
    current_user: Annotated[
        dict[str, Any],
        Depends(require_admin),
    ],
) -> ProviderResponse:
    del current_user

    current_provider = find_provider_by_id(
        connection,
        provider_id,
    )

    if current_provider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado",
        )

    validate_category(
        connection,
        request.category_id,
    )

    duplicate = find_provider_by_nit(
        connection,
        request.nit,
        excluded_id=provider_id,
    )

    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Otro proveedor ya utiliza ese NIT",
        )

    try:
        provider = update_provider(
            connection,
            provider_id,
            request.model_dump(),
        )
    except UniqueViolation as error:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Otro proveedor ya utiliza esos datos",
        ) from error

    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado",
        )

    return ProviderResponse(**provider)


@router.patch(
    "/{provider_id}/status",
    response_model=ProviderResponse,
    summary="Activar o desactivar proveedor",
)
def patch_provider_status(
    provider_id: int,
    request: ProviderStatusUpdate,
    connection: Annotated[
        Connection,
        Depends(get_connection),
    ],
    current_user: Annotated[
        dict[str, Any],
        Depends(require_admin),
    ],
) -> ProviderResponse:
    del current_user

    provider = change_provider_status(
        connection,
        provider_id,
        request.is_active,
    )

    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado",
        )

    return ProviderResponse(**provider)


@router.delete(
    "/{provider_id}",
    response_model=ProviderResponse,
    summary="Desactivar proveedor",
)
def delete_provider(
    provider_id: int,
    connection: Annotated[
        Connection,
        Depends(get_connection),
    ],
    current_user: Annotated[
        dict[str, Any],
        Depends(require_admin),
    ],
) -> ProviderResponse:
    del current_user

    provider = change_provider_status(
        connection,
        provider_id,
        False,
    )

    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado",
        )

    return ProviderResponse(**provider)
