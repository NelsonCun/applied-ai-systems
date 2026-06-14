from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import (
    CategoryRepository,
)
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    @staticmethod
    def list_all(
        database: Session,
        search: str | None,
        is_active: bool | None,
    ) -> list[Category]:
        return CategoryRepository.list_all(
            database=database,
            search=search,
            is_active=is_active,
        )

    @staticmethod
    def get_by_id(
        database: Session,
        category_id: int,
    ) -> Category:
        category = CategoryRepository.get_by_id(
            database=database,
            category_id=category_id,
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría solicitada no existe.",
            )

        return category

    @staticmethod
    def create(
        database: Session,
        data: CategoryCreate,
    ) -> Category:
        duplicate = CategoryRepository.get_by_name(
            database=database,
            name=data.name,
        )

        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una categoría con ese nombre.",
            )

        try:
            return CategoryRepository.create(
                database=database,
                data=data,
            )
        except IntegrityError as error:
            database.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible crear la categoría.",
            ) from error

    @staticmethod
    def update(
        database: Session,
        category_id: int,
        data: CategoryUpdate,
    ) -> Category:
        category = CategoryService.get_by_id(
            database=database,
            category_id=category_id,
        )

        if data.name is not None:
            duplicate = CategoryRepository.get_by_name(
                database=database,
                name=data.name,
            )

            if (
                duplicate is not None
                and duplicate.id != category.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        "Ya existe una categoría con ese nombre."
                    ),
                )

        try:
            return CategoryRepository.update(
                database=database,
                category=category,
                data=data,
            )
        except IntegrityError as error:
            database.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No fue posible actualizar la categoría.",
            ) from error

    @staticmethod
    def delete(
        database: Session,
        category_id: int,
    ) -> None:
        category = CategoryService.get_by_id(
            database=database,
            category_id=category_id,
        )

        try:
            CategoryRepository.delete(
                database=database,
                category=category,
            )
        except IntegrityError as error:
            database.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "No se puede eliminar la categoría porque "
                    "tiene preguntas asociadas."
                ),
            ) from error
