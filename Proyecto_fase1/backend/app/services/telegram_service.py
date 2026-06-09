import os
import requests
from dotenv import load_dotenv


load_dotenv()


def enviar_diagnostico_telegram(
    sintomas: list[str],
    falla_texto: str,
    recomendacion: str,
    coincidencias: int,
    chat_id: str | None = None
) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    default_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    chat_id_final = chat_id or default_chat_id

    if not token or not chat_id_final:
        return False

    sintomas_texto = "\n".join([f"- {s}" for s in sintomas])

    mensaje = f"""
🧠 Doctor Byte - Diagnóstico realizado

Síntomas seleccionados:
{sintomas_texto}

Diagnóstico probable:
{falla_texto}

Coincidencias:
{coincidencias}

Recomendación:
{recomendacion}
""".strip()

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id_final,
            "text": mensaje
        },
        timeout=10
    )

    return response.status_code == 200
