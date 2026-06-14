import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings as app_settings
from app.models import BotSetting
from app.repositories.bot_setting_repository import (
    BotSettingRepository,
)
from app.schemas.bot_setting import (
    BotSettingUpdate,
    TelegramTestRequest,
    TelegramTestResponse,
)


class BotSettingService:
    @staticmethod
    def get_settings(
        database: Session,
    ) -> BotSetting:
        bot_settings = (
            BotSettingRepository.get_settings(
                database=database
            )
        )

        if bot_settings is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                detail=(
                    "No existe configuración general "
                    "para el bot."
                ),
            )

        return bot_settings

    @staticmethod
    def update(
        database: Session,
        data: BotSettingUpdate,
    ) -> BotSetting:
        bot_settings = BotSettingService.get_settings(
            database=database
        )

        changes = data.model_dump(
            exclude_unset=True,
        )

        return BotSettingRepository.update(
            database=database,
            bot_settings=bot_settings,
            changes=changes,
        )

    @staticmethod
    def send_test_message(
        database: Session,
        data: TelegramTestRequest,
    ) -> TelegramTestResponse:
        token = (
            app_settings.telegram_bot_token.strip()
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El token del bot de Telegram "
                    "no está configurado."
                ),
            )

        bot_settings = BotSettingService.get_settings(
            database=database
        )

        chat_id = (
            data.chat_id
            or bot_settings.telegram_chat_id
        )

        if not chat_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Debe configurar el ID del chat "
                    "o grupo de Telegram."
                ),
            )

        message = (
            data.message
            or (
                f"Mensaje de prueba de "
                f"{bot_settings.hospital_name}. "
                "La integración con Telegram "
                "funciona correctamente."
            )
        )

        url = (
            f"{app_settings.telegram_api_base_url}"
            f"/bot{token}/sendMessage"
        )

        try:
            response = httpx.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": message,
                },
                timeout=15.0,
            )

            response_data = response.json()
        except (
            httpx.HTTPError,
            ValueError,
        ) as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "No fue posible comunicarse "
                    "con Telegram."
                ),
            ) from error

        if (
            not response.is_success
            or not response_data.get("ok")
        ):
            telegram_detail = response_data.get(
                "description",
                "Telegram rechazó la solicitud.",
            )

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=telegram_detail,
            )

        result = response_data.get("result", {})

        return TelegramTestResponse(
            success=True,
            chat_id=str(chat_id),
            message_id=result.get("message_id"),
            detail=(
                "Mensaje enviado correctamente "
                "mediante Telegram."
            ),
        )
