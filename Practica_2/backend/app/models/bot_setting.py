from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    FetchedValue,
    SmallInteger,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BotSetting(Base):
    __tablename__ = "bot_settings"

    id: Mapped[int] = mapped_column(
        SmallInteger,
        primary_key=True,
        server_default=text("1"),
    )

    hospital_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    telegram_chat_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    bot_username: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    welcome_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    unknown_question_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        server_onupdate=FetchedValue(),
    )
