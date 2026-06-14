from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )

    telegram_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
    )

    telegram_username: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    telegram_first_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    telegram_chat_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
    )

    original_query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    normalized_query: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )

    question_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "questions.id",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "categories.id",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    response_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    was_answered: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
