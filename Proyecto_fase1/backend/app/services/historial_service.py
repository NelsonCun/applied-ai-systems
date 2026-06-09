import json
from datetime import datetime
from pathlib import Path


HISTORIAL_FILE = Path(__file__).resolve().parents[1] / "data" / "historial.json"


def inicializar_historial() -> None:
    HISTORIAL_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not HISTORIAL_FILE.exists():
        HISTORIAL_FILE.write_text("[]", encoding="utf-8")


def leer_historial() -> list[dict]:
    inicializar_historial()

    with open(HISTORIAL_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def guardar_diagnostico(registro: dict) -> dict:
    historial = leer_historial()

    nuevo_registro = {
        "id": len(historial) + 1,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sintomas": registro["sintomas"],
        "falla": registro["falla"],
        "falla_texto": registro["falla_texto"],
        "recomendacion": registro["recomendacion"],
        "coincidencias": registro["coincidencias"],
        "telegram_enviado": registro["telegram_enviado"]
    }

    historial.append(nuevo_registro)

    with open(HISTORIAL_FILE, "w", encoding="utf-8") as file:
        json.dump(historial, file, indent=4, ensure_ascii=False)

    return nuevo_registro


def limpiar_historial() -> None:
    inicializar_historial()
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as file:
        json.dump([], file, indent=4, ensure_ascii=False)
