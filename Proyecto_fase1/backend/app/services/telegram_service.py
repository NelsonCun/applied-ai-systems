import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from app.services.configuracion_service import (
    ConfiguracionError,
    obtener_configuracion_telegram,
)
from app.services.prolog_service import obtener_sintomas_disponibles


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_FILE)

TELEGRAM_API_BASE_URL = "https://api.telegram.org"
TELEGRAM_REQUEST_TIMEOUT = 10


class TelegramServiceError(RuntimeError):
    """Error al comunicarse con la API de Telegram."""


def obtener_token_telegram() -> str:
    return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


def token_telegram_configurado() -> bool:
    return bool(obtener_token_telegram())


def ejecutar_metodo_telegram(
    metodo: str,
    datos: dict[str, Any] | None = None,
    timeout: int | float = TELEGRAM_REQUEST_TIMEOUT,
) -> Any:
    token = obtener_token_telegram()

    if not token:
        raise TelegramServiceError(
            "El token de Telegram no está configurado."
        )

    url = f"{TELEGRAM_API_BASE_URL}/bot{token}/{metodo}"

    try:
        respuesta = requests.post(
            url,
            json=datos or {},
            timeout=timeout,
        )
        respuesta.raise_for_status()
        contenido = respuesta.json()

    except requests.RequestException as exc:
        raise TelegramServiceError(
            "No fue posible comunicarse con Telegram."
        ) from exc

    except ValueError as exc:
        raise TelegramServiceError(
            "Telegram devolvió una respuesta que no es JSON válido."
        ) from exc

    if not contenido.get("ok"):
        descripcion = contenido.get(
            "description",
            "Telegram rechazó la solicitud.",
        )
        raise TelegramServiceError(descripcion)

    return contenido.get("result")


def obtener_actualizaciones(
    offset: int | None = None,
    timeout: int = 25,
) -> list[dict[str, Any]]:
    datos: dict[str, Any] = {
        "timeout": timeout,
        "allowed_updates": ["message"],
    }

    if offset is not None:
        datos["offset"] = offset

    resultado = ejecutar_metodo_telegram(
        "getUpdates",
        datos=datos,
        timeout=timeout + 5,
    )

    if not isinstance(resultado, list):
        raise TelegramServiceError(
            "Telegram no devolvió una lista de actualizaciones."
        )

    return resultado


def enviar_mensaje_telegram(
    chat_id: str | int,
    texto: str,
) -> bool:
    if not str(chat_id).strip() or not texto.strip():
        return False

    try:
        ejecutar_metodo_telegram(
            "sendMessage",
            datos={
                "chat_id": str(chat_id),
                "text": texto,
            },
        )
        return True

    except TelegramServiceError:
        return False


def _nombres_sintomas(sintomas: list[str]) -> list[str]:
    try:
        disponibles = obtener_sintomas_disponibles()

        nombres = {
            item["id"]: item["nombre"]
            for item in disponibles
        }

    except (KeyError, TypeError, RuntimeError):
        nombres = {}

    return [
        nombres.get(sintoma, sintoma)
        for sintoma in sintomas
    ]


def construir_mensaje_diagnostico(
    sintomas: list[str],
    falla_texto: str,
    recomendacion: str,
    coincidencias: int,
    encabezado: str,
    despedida: str,
) -> str:
    sintomas_texto = "\n".join(
        f"• {nombre}"
        for nombre in _nombres_sintomas(sintomas)
    )

    return f"""
{encabezado}

Síntomas seleccionados:
{sintomas_texto}

Diagnóstico probable:
{falla_texto}

Coincidencias:
{coincidencias}

Recomendación:
{recomendacion}

{despedida}
""".strip()


def enviar_diagnostico_telegram(
    sintomas: list[str],
    falla_texto: str,
    recomendacion: str,
    coincidencias: int,
    chat_id: str | None = None,
) -> bool:
    try:
        configuracion = obtener_configuracion_telegram()

    except ConfiguracionError:
        return False

    if not configuracion["activo"]:
        return False

    chat_id_final = chat_id or configuracion["chat_id"]

    if not token_telegram_configurado() or not chat_id_final:
        return False

    mensaje = construir_mensaje_diagnostico(
        sintomas=sintomas,
        falla_texto=falla_texto,
        recomendacion=recomendacion,
        coincidencias=coincidencias,
        encabezado=configuracion["encabezado_diagnostico"],
        despedida=configuracion["mensaje_despedida"],
    )

    return enviar_mensaje_telegram(
        chat_id=chat_id_final,
        texto=mensaje,
    )