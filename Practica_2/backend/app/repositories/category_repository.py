from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository:
    @staticmethod
    def list_all(
        database: Session,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> list[Category]:
        statement = select(Category)

        if search:
            search_pattern = f"%{search.strip()}%"

            statement = statement.where(
                Category.name.ilike(search_pattern)
            )

        if is_active is not None:
            statement = statement.where(
                Category.is_active.is_(is_active)
            )

        statement = statement.order_by(
            Category.name.asc()
        )

        return list(database.scalars(statement).all())

    @staticmethod
    def get_by_id(
        database: Session,
        category_id: int,
    ) -> Category | None:
        return database.get(Category, category_id)

    @staticmethod
    def get_by_name(
        database: Session,
        name: str,
    ) -> Category | None:
        statement = select(Category).where(
            func.lower(Category.name) == name.lower()
        )

        return database.scalar(statement)

    @staticmethod
    def create(
        database: Session,
        data: CategoryCreate,
    ) -> Category:
        category = Category(
            name=data.name,
            description=data.description,
            is_active=data.is_active,
        )

        database.add(category)
        database.commit()
        database.refresh(category)

        return category

    @staticmethod
    def update(
        database: Session,
        category: Category,
        data: CategoryUpdate,
    ) -> Category:
        changes = data.model_dump(
            exclude_unset=True,
        )

        for field, value in changes.items():
            setattr(category, field, value)

        database.commit()
        database.refresh(category)

        return category

    @staticmethod
    def delete(
        database: Session,
        category: Category,
    ) -> None:
        database.delete(category)
        database.commit()
