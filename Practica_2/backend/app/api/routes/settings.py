from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin
from app.db.session import get_db
from app.models import AdminUser
from app.schemas.bot_setting import (
    BotSettingResponse,
    BotSettingUpdate,
    TelegramTestRequest,
    TelegramTestResponse,
)
from app.services.bot_setting_service import (
    BotSettingService,
)


router = APIRouter(
    prefix="/settings",
    tags=["Configuración"],
)


@router.get(
    "/telegram",
    response_model=BotSettingResponse,
)
def get_telegram_settings(
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(
        get_current_admin
    ),
):
    del current_user

    return BotSettingService.get_settings(
        database=database
    )


@router.put(
    "/telegram",
    response_model=BotSettingResponse,
)
def update_telegram_settings(
    data: BotSettingUpdate,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(
        get_current_admin
    ),
):
    del current_user

    return BotSettingService.update(
        database=database,
        data=data,
    )


@router.post(
    "/telegram/test-message",
    response_model=TelegramTestResponse,
)
def send_test_message(
    data: TelegramTestRequest,
    database: Session = Depends(get_db),
    current_user: AdminUser = Depends(
        get_current_admin
    ),
):
    del current_user

    return BotSettingService.send_test_message(
        database=database,
        data=data,
    )
