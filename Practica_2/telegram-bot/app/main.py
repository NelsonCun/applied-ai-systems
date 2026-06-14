import logging
import os
import time

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://backend:8000/api/v1",
).rstrip("/")


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    if update.message:
        await update.message.reply_text(
            "Bienvenido a SmartBot. Escriba su consulta para buscar "
            "información registrada en el sistema."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    if update.message:
        await update.message.reply_text(
            "Envíe una pregunta en un mensaje de texto. "
            "SmartBot consultará la información disponible."
        )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    del context

    if not update.message or not update.message.text:
        return

    user = update.effective_user
    chat = update.effective_chat

    payload = {
        "query": update.message.text,
        "telegram_user_id": user.id if user else None,
        "telegram_username": user.username if user else None,
        "telegram_first_name": user.first_name if user else None,
        "telegram_chat_id": chat.id if chat else None,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{BACKEND_URL}/queries/resolve",
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

        answer = result.get(
            "answer",
            "No fue posible obtener una respuesta.",
        )
    except (httpx.HTTPError, ValueError) as error:
        logger.exception("Error consultando la API: %s", error)
        answer = (
            "El servicio de consultas no está disponible en este momento. "
            "Intente nuevamente más tarde."
        )

    await update.message.reply_text(answer)


def wait_without_token() -> None:
    logger.warning(
        "TELEGRAM_BOT_TOKEN no está configurado. "
        "El contenedor permanecerá activo a la espera de configuración."
    )

    while True:
        time.sleep(3600)


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        wait_without_token()
        return

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    logger.info("SmartBot iniciado mediante long polling.")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()
