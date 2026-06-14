import json
import os
import tempfile
import threading
from pathlib import Path

from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
CONFIG_FILE = Path(__file__).resolve().parents[1] / "data" / "configuracion.json"

load_dotenv(dotenv_path=ENV_FILE)

_WRITE_LOCK = threading.Lock()

CONFIGURACION_PREDETERMINADA = {
    "telegram": {
        "activo": True,
        "chat_id": "",
        "mensaje_bienvenida": "Bienvenido a Doctor Byte.",
        "encabezado_diagnostico": "Doctor Byte - Diagnóstico realizado",
        "mensaje_despedida": (
            "Este diagnóstico es preliminar. Si el problema continúa, "
            "consulte a un técnico especializado."
        ),
    }
}


class ConfiguracionError(RuntimeError):
    """Error al leer o guardar la configuración operativa."""


def _crear_configuracion_inicial() -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    if CONFIG_FILE.exists():
        return

    configuracion = json.loads(json.dumps(CONFIGURACION_PREDETERMINADA))
    configuracion["telegram"]["chat_id"] = os.getenv("TELEGRAM_CHAT_ID", "")
    _guardar_archivo(configuracion)


def _guardar_archivo(configuracion: dict) -> None:
    archivo_temporal: str | None = None

    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=CONFIG_FILE.parent,
            prefix="configuracion_",
            suffix=".tmp",
            delete=False,
        ) as temporal:
            archivo_temporal = temporal.name
            json.dump(configuracion, temporal, ensure_ascii=False, indent=2)
            temporal.write("\n")
            temporal.flush()
            os.fsync(temporal.fileno())

        os.replace(archivo_temporal, CONFIG_FILE)

    except OSError as exc:
        raise ConfiguracionError(
            "No fue posible guardar la configuración del sistema."
        ) from exc

    finally:
        if archivo_temporal and os.path.exists(archivo_temporal):
            os.remove(archivo_temporal)


def leer_configuracion() -> dict:
    _crear_configuracion_inicial()

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as archivo:
            configuracion = json.load(archivo)
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfiguracionError(
            "No fue posible leer la configuración del sistema."
        ) from exc

    telegram = {
        **CONFIGURACION_PREDETERMINADA["telegram"],
        **configuracion.get("telegram", {}),
    }

    if not telegram["chat_id"]:
        telegram["chat_id"] = os.getenv("TELEGRAM_CHAT_ID", "")

    return {
        "telegram": telegram,
    }


def obtener_configuracion_telegram() -> dict:
    telegram = leer_configuracion()["telegram"]

    return {
        **telegram,
        "token_configurado": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
    }


def actualizar_configuracion_telegram(datos: dict) -> dict:
    with _WRITE_LOCK:
        configuracion = leer_configuracion()
        configuracion["telegram"] = {
            "activo": datos["activo"],
            "chat_id": datos["chat_id"],
            "mensaje_bienvenida": datos["mensaje_bienvenida"],
            "encabezado_diagnostico": datos["encabezado_diagnostico"],
            "mensaje_despedida": datos["mensaje_despedida"],
        }
        _guardar_archivo(configuracion)

    return obtener_configuracion_telegram()
