from fastapi import (
    APIRouter,
    Depends,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import CategoryService


router = APIRouter(
    prefix="/categories",
    tags=["Categorías"],
)


@router.get(
    "",
    response_model=list[CategoryResponse],
)
def list_categories(
    search: str | None = Query(
        default=None,
        max_length=100,
    ),
    is_active: bool | None = Query(default=None),
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return CategoryService.list_all(
        database=database,
        search=search,
        is_active=is_active,
    )


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: CategoryCreate,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return CategoryService.create(
        database=database,
        data=data,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return CategoryService.get_by_id(
        database=database,
        category_id=category_id,
    )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    del current_user

    return CategoryService.update(
        database=database,
        category_id=category_id,
        data=data,
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_category(
    category_id: int,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
) -> Response:
    del current_user

    CategoryService.delete(
        database=database,
        category_id=category_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
