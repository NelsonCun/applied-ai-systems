import json
import subprocess
from pathlib import Path


PROLOG_FILE = Path(__file__).resolve().parents[3] / "prolog" / "doctor_byte.pl"


FALLAS_TEXTO = {
    "fuente_poder": "Falla en fuente de poder",
    "memoria_ram": "Falla de memoria RAM",
    "disco_duro": "Falla de disco duro",
    "sobrecalentamiento_cpu": "Sobrecalentamiento del procesador",
    "sistema_operativo_corrupto": "Sistema operativo corrupto",
    "malware": "Posible infección por malware",
    "tarjeta_red": "Falla en tarjeta o configuración de red",
    "bateria_danada": "Batería dañada",
    "puerto_usb_danado": "Puerto USB dañado",
    "controladores_audio": "Problema con controladores de audio",
    "bios_bateria_cmos": "Batería CMOS descargada",
    "periferico_danado": "Periférico dañado o desconectado",
    "sin_diagnostico": "Sin diagnóstico"
}


def convertir_lista_a_prolog(sintomas: list[str]) -> str:
    return "[" + ",".join(sintomas) + "]"


def diagnosticar_con_prolog(sintomas: list[str]) -> dict:
    if not sintomas:
        return {
            "falla": "sin_diagnostico",
            "falla_texto": FALLAS_TEXTO["sin_diagnostico"],
            "recomendacion": "Debe seleccionar al menos un síntoma para realizar el diagnóstico.",
            "coincidencias": 0
        }

    sintomas_prolog = convertir_lista_a_prolog(sintomas)

    query = (
        f"mejor_diagnostico({sintomas_prolog}, Falla, Recomendacion, Coincidencias), "
        f"format('{{\"falla\":\"~w\",\"recomendacion\":\"~w\",\"coincidencias\":~w}}', "
        f"[Falla, Recomendacion, Coincidencias]), halt."
    )

    resultado = subprocess.run(
        ["swipl", "-q", "-s", str(PROLOG_FILE), "-g", query],
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0 or not resultado.stdout.strip():
        return {
            "falla": "sin_diagnostico",
            "falla_texto": FALLAS_TEXTO["sin_diagnostico"],
            "recomendacion": "No se encontró una falla probable con los síntomas seleccionados.",
            "coincidencias": 0
        }

    data = json.loads(resultado.stdout)
    falla = data["falla"]

    return {
        "falla": falla,
        "falla_texto": FALLAS_TEXTO.get(falla, falla),
        "recomendacion": data["recomendacion"],
        "coincidencias": int(data["coincidencias"])
    }


def obtener_sintomas_disponibles() -> list[dict]:
    return [
        {"id": "no_enciende", "nombre": "El equipo no enciende"},
        {"id": "pantalla_negra", "nombre": "Pantalla negra"},
        {"id": "reinicio_inesperado", "nombre": "Se reinicia inesperadamente"},
        {"id": "pitidos_arranque", "nombre": "Emite pitidos al encender"},
        {"id": "lentitud_sistema", "nombre": "Sistema operativo muy lento"},
        {"id": "sin_internet", "nombre": "No hay conexión a internet"},
        {"id": "pantalla_azul", "nombre": "Pantalla azul"},
        {"id": "sobrecalentamiento", "nombre": "Sobrecalentamiento"},
        {"id": "teclado_no_responde", "nombre": "Teclado no responde"},
        {"id": "mouse_no_responde", "nombre": "Mouse no responde"},
        {"id": "ruido_disco", "nombre": "El disco duro hace ruidos"},
        {"id": "aplicaciones_se_cierran", "nombre": "Las aplicaciones se cierran solas"},
        {"id": "no_detecta_usb", "nombre": "No detecta dispositivos USB"},
        {"id": "sin_sonido", "nombre": "No hay sonido"},
        {"id": "bateria_no_carga", "nombre": "La batería no carga"},
        {"id": "ventilador_ruidoso", "nombre": "El ventilador hace ruido excesivo"},
        {"id": "fecha_hora_reinicia", "nombre": "La fecha y hora se reinician"},
        {"id": "ventanas_emergentes", "nombre": "Aparecen ventanas emergentes"}
    ]
