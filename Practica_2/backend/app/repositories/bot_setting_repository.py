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
