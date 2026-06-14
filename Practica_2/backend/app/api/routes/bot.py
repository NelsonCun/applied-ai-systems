from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.bot_setting import (
    PublicBotConfigResponse,
)
from app.services.bot_setting_service import (
    BotSettingService,
)


router = APIRouter(
    prefix="/bot",
    tags=["Bot de Telegram"],
)


@router.get(
    "/config",
    response_model=PublicBotConfigResponse,
)
def get_public_bot_config(
    database: Session = Depends(get_db),
):
    return BotSettingService.get_settings(
        database=database
    )
