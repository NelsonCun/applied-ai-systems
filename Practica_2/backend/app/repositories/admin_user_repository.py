from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.admin_user import AdminUser


class AdminUserRepository:
    @staticmethod
    def authenticate(
        database: Session,
        username: str,
        password: str,
    ) -> AdminUser | None:
        statement = select(AdminUser).where(
            AdminUser.username == username,
            AdminUser.is_active.is_(True),
            AdminUser.password_hash
            == func.crypt(password, AdminUser.password_hash),
        )

        return database.scalar(statement)

    @staticmethod
    def get_by_id(
        database: Session,
        user_id: int,
    ) -> AdminUser | None:
        statement = select(AdminUser).where(
            AdminUser.id == user_id,
            AdminUser.is_active.is_(True),
        )

        return database.scalar(statement)
