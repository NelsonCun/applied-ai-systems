import json
import os
import tempfile
import threading
from datetime import datetime
from pathlib import Path


HISTORIAL_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "historial.json"
)

_HISTORIAL_LOCK = threading.RLock()


class HistorialError(OSError):
    """Error al leer o guardar el historial de diagnósticos."""


def inicializar_historial() -> None:
    HISTORIAL_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not HISTORIAL_FILE.exists():
        _guardar_archivo([])


def _guardar_archivo(
    historial: list[dict],
) -> None:
    archivo_temporal: str | None = None

    try:
        HISTORIAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=HISTORIAL_FILE.parent,
            prefix="historial_",
            suffix=".tmp",
            delete=False,
        ) as temporal:
            archivo_temporal = temporal.name

            json.dump(
                historial,
                temporal,
                indent=4,
                ensure_ascii=False,
            )

            temporal.write("\n")
            temporal.flush()
            os.fsync(
                temporal.fileno()
            )

        os.replace(
            archivo_temporal,
            HISTORIAL_FILE,
        )

    except OSError as exc:
        raise HistorialError(
            "No fue posible guardar el historial."
        ) from exc

    finally:
        if (
            archivo_temporal
            and os.path.exists(
                archivo_temporal
            )
        ):
            os.remove(
                archivo_temporal
            )


def leer_historial() -> list[dict]:
    with _HISTORIAL_LOCK:
        inicializar_historial()

        try:
            with HISTORIAL_FILE.open(
                "r",
                encoding="utf-8",
            ) as archivo:
                contenido = json.load(
                    archivo
                )

        except (
            OSError,
            json.JSONDecodeError,
        ) as exc:
            raise HistorialError(
                "No fue posible leer el historial."
            ) from exc

        if not isinstance(
            contenido,
            list,
        ):
            raise HistorialError(
                "El archivo de historial no "
                "contiene una lista válida."
            )

        return contenido


def guardar_diagnostico(
    registro: dict,
) -> dict:
    with _HISTORIAL_LOCK:
        historial = leer_historial()

        siguiente_id = max(
            (
                int(
                    item.get(
                        "id",
                        0,
                    )
                )
                for item in historial
            ),
            default=0,
        ) + 1

        nuevo_registro = {
            "id": siguiente_id,
            "fecha": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "sintomas": registro["sintomas"],
            "falla": registro["falla"],
            "falla_texto": registro[
                "falla_texto"
            ],
            "recomendacion": registro[
                "recomendacion"
            ],
            "coincidencias": registro[
                "coincidencias"
            ],
            "telegram_enviado": registro[
                "telegram_enviado"
            ],
        }

        historial.append(
            nuevo_registro
        )

        _guardar_archivo(
            historial
        )

        return nuevo_registro


def limpiar_historial() -> None:
    with _HISTORIAL_LOCK:
        _guardar_archivo([])