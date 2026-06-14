import json
import re
import subprocess
from pathlib import Path
from typing import Any


PROLOG_FILE = (
    Path(__file__).resolve().parents[3]
    / "prolog"
    / "doctor_byte.pl"
)

IDENTIFICADOR_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*$"
)

PROLOG_TIMEOUT_SECONDS = 10


class PrologServiceError(RuntimeError):
    """Error al ejecutar o interpretar una consulta de SWI-Prolog."""


class ConocimientoValidationError(ValueError):
    """Error de validación relacionado con la base de conocimiento."""


def ejecutar_consulta_json(
    objetivo: str
) -> dict[str, Any]:
    try:
        resultado = subprocess.run(
            [
                "swipl",
                "-q",
                "-s",
                str(PROLOG_FILE),
                "-g",
                objetivo,
                "-t",
                "halt"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=PROLOG_TIMEOUT_SECONDS,
            check=False
        )

    except FileNotFoundError as exc:
        raise PrologServiceError(
            "SWI-Prolog no está instalado o no está disponible en PATH."
        ) from exc

    except subprocess.TimeoutExpired as exc:
        raise PrologServiceError(
            "La consulta a Prolog excedió el tiempo permitido."
        ) from exc

    if resultado.returncode != 0:
        detalle = resultado.stderr.strip()

        raise PrologServiceError(
            detalle
            or "SWI-Prolog terminó con un código de error."
        )

    salida = resultado.stdout.strip()

    if not salida:
        raise PrologServiceError(
            "SWI-Prolog no devolvió información."
        )

    try:
        return json.loads(salida)

    except json.JSONDecodeError as exc:
        raise PrologServiceError(
            "La respuesta de Prolog no contiene JSON válido."
        ) from exc


def validar_identificador(
    identificador: str
) -> str:
    identificador_limpio = identificador.strip()

    if not IDENTIFICADOR_PATTERN.fullmatch(
        identificador_limpio
    ):
        raise ConocimientoValidationError(
            f"El identificador '{identificador}' no es válido."
        )

    return identificador_limpio


def convertir_lista_a_prolog(
    sintomas: list[str]
) -> str:
    sintomas_validados = [
        validar_identificador(sintoma)
        for sintoma in sintomas
    ]

    return "[" + ",".join(sintomas_validados) + "]"


def obtener_sintomas_disponibles() -> list[dict]:
    data = ejecutar_consulta_json(
        "listar_sintomas_json"
    )

    return data.get("sintomas", [])


def obtener_fallas_disponibles() -> list[dict]:
    data = ejecutar_consulta_json(
        "listar_fallas_json"
    )

    return data.get("fallas", [])


def obtener_recomendaciones_disponibles() -> list[dict]:
    data = ejecutar_consulta_json(
        "listar_recomendaciones_json"
    )

    return data.get("recomendaciones", [])


def obtener_reglas_disponibles() -> list[dict]:
    data = ejecutar_consulta_json(
        "listar_reglas_json"
    )

    return data.get("reglas", [])


def validar_sintomas_existentes(
    sintomas: list[str]
) -> None:
    sintomas_disponibles = {
        item["id"]
        for item in obtener_sintomas_disponibles()
    }

    sintomas_inexistentes = [
        sintoma
        for sintoma in sintomas
        if sintoma not in sintomas_disponibles
    ]

    if sintomas_inexistentes:
        raise ConocimientoValidationError(
            "Los siguientes síntomas no existen: "
            + ", ".join(sintomas_inexistentes)
        )


def diagnosticar_con_prolog(
    sintomas: list[str]
) -> dict:
    if not sintomas:
        raise ConocimientoValidationError(
            "Debe seleccionar al menos un síntoma."
        )

    validar_sintomas_existentes(sintomas)

    sintomas_prolog = convertir_lista_a_prolog(
        sintomas
    )

    data = ejecutar_consulta_json(
        f"diagnostico_json({sintomas_prolog})"
    )

    return {
        "falla": data["falla"],
        "falla_texto": data["falla_texto"],
        "recomendacion": data["recomendacion"],
        "coincidencias": int(data["coincidencias"])
    }