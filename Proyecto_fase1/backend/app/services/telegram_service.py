import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from app.services.configuracion_service import (
    ConfiguracionError,
    obtener_configuracion_telegram,
)


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_FILE)


def enviar_diagnostico_telegram(
    sintomas: list[str],
    falla_texto: str,
    recomendacion: str,
    coincidencias: int,
    chat_id: str | None = None,
) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    try:
        configuracion = obtener_configuracion_telegram()
    except ConfiguracionError:
        return False

    if not configuracion["activo"]:
        return False

    chat_id_final = chat_id or configuracion["chat_id"]

    if not token or not chat_id_final:
        return False

    sintomas_texto = "\n".join([f"- {sintoma}" for sintoma in sintomas])

    mensaje = f"""
{configuracion['encabezado_diagnostico']}

Síntomas seleccionados:
{sintomas_texto}

Diagnóstico probable:
{falla_texto}

Coincidencias:
{coincidencias}

Recomendación:
{recomendacion}

{configuracion['mensaje_despedida']}
""".strip()

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id_final,
                "text": mensaje,
            },
            timeout=10,
        )

        return response.status_code == 200

    except requests.RequestException:
        return False
