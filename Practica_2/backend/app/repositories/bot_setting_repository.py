from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BotSetting


class BotSettingRepository:
    @staticmethod
    def get_settings(
        database: Session,
    ) -> BotSetting | None:
        statement = select(BotSetting).where(
            BotSetting.id == 1
        )

        return database.scalar(statement)

    @staticmethod
    def update(
        database: Session,
        bot_settings: BotSetting,
        changes: dict,
    ) -> BotSetting:
        for field, value in changes.items():
            setattr(bot_settings, field, value)

        database.commit()
        database.refresh(bot_settings)

        return bot_settings
