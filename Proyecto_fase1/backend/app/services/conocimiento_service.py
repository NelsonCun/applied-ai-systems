import os
import tempfile
import threading
from pathlib import Path
from typing import Any

from app.services.prolog_service import (
    obtener_fallas_disponibles,
    obtener_recomendaciones_disponibles,
    obtener_reglas_disponibles,
    obtener_sintomas_disponibles,
    validar_identificador,
)


CONOCIMIENTO_FILE = (
    Path(__file__).resolve().parents[3]
    / "prolog"
    / "conocimiento.pl"
)

MIN_SINTOMAS = 15
MIN_FALLAS = 10
MIN_RECOMENDACIONES = 10
MIN_REGLAS = 10

_WRITE_LOCK = threading.Lock()


class RecursoNoEncontradoError(LookupError):
    """El recurso solicitado no existe."""


class ConflictoConocimientoError(RuntimeError):
    """La operación viola una regla de integridad del conocimiento."""


class PersistenciaConocimientoError(RuntimeError):
    """No fue posible guardar la base de conocimiento."""


def listar_sintomas() -> list[dict]:
    return obtener_sintomas_disponibles()


def listar_fallas() -> list[dict]:
    return obtener_fallas_disponibles()


def listar_recomendaciones() -> list[dict]:
    return obtener_recomendaciones_disponibles()


def listar_reglas() -> list[dict]:
    return obtener_reglas_disponibles()


def _cargar_conocimiento() -> dict[str, list[dict]]:
    return {
        "sintomas": listar_sintomas(),
        "fallas": listar_fallas(),
        "recomendaciones": listar_recomendaciones(),
        "reglas": listar_reglas(),
    }


def _buscar_indice(
    elementos: list[dict],
    identificador: str,
) -> int:
    for indice, elemento in enumerate(elementos):
        if elemento["id"] == identificador:
            return indice

    raise RecursoNoEncontradoError(
        f"No existe un recurso con identificador '{identificador}'."
    )


def _escapar_texto_prolog(texto: str) -> str:
    return (
        texto
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def _texto_prolog(texto: str) -> str:
    return f'"{_escapar_texto_prolog(texto)}"'


def _serializar_conocimiento(
    conocimiento: dict[str, list[dict]],
) -> str:
    lineas = [
        ":- encoding(utf8).",
        "",
        ":- dynamic sintoma/3.",
        ":- dynamic falla/3.",
        ":- dynamic recomendacion/3.",
        ":- dynamic regla/3.",
        "",
        "% ============================================================",
        "% SÍNTOMAS",
        "% sintoma(Id, NombreVisible, Categoria).",
        "% ============================================================",
        "",
    ]

    for sintoma in conocimiento["sintomas"]:
        identificador = validar_identificador(sintoma["id"])

        lineas.append(
            "sintoma("
            f"{identificador}, "
            f"{_texto_prolog(sintoma['nombre'])}, "
            f"{_texto_prolog(sintoma['categoria'])}"
            ")."
        )

    lineas.extend([
        "",
        "% ============================================================",
        "% FALLAS",
        "% falla(Id, NombreVisible, Descripcion).",
        "% ============================================================",
        "",
    ])

    for falla in conocimiento["fallas"]:
        identificador = validar_identificador(falla["id"])

        lineas.append(
            "falla("
            f"{identificador}, "
            f"{_texto_prolog(falla['nombre'])}, "
            f"{_texto_prolog(falla['descripcion'])}"
            ")."
        )

    lineas.extend([
        "",
        "% ============================================================",
        "% RECOMENDACIONES",
        "% recomendacion(Id, FallaId, Texto).",
        "% ============================================================",
        "",
    ])

    for recomendacion in conocimiento["recomendaciones"]:
        identificador = validar_identificador(recomendacion["id"])
        falla_id = validar_identificador(recomendacion["falla_id"])

        lineas.append(
            "recomendacion("
            f"{identificador}, "
            f"{falla_id}, "
            f"{_texto_prolog(recomendacion['texto'])}"
            ")."
        )

    lineas.extend([
        "",
        "% ============================================================",
        "% REGLAS",
        "% regla(Id, FallaId, ListaSintomas).",
        "% ============================================================",
        "",
    ])

    for regla in conocimiento["reglas"]:
        identificador = validar_identificador(regla["id"])
        falla_id = validar_identificador(regla["falla_id"])

        sintomas = [
            validar_identificador(sintoma)
            for sintoma in regla["sintomas"]
        ]

        lista_sintomas = "[" + ", ".join(sintomas) + "]"

        lineas.append(
            "regla("
            f"{identificador}, "
            f"{falla_id}, "
            f"{lista_sintomas}"
            ")."
        )

    lineas.append("")

    return "\n".join(lineas)


def _guardar_conocimiento(
    conocimiento: dict[str, list[dict]],
) -> None:
    contenido = _serializar_conocimiento(conocimiento)
    archivo_temporal: str | None = None

    try:
        CONOCIMIENTO_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=CONOCIMIENTO_FILE.parent,
            prefix="conocimiento_",
            suffix=".tmp",
            delete=False,
        ) as temporal:
            archivo_temporal = temporal.name
            temporal.write(contenido)
            temporal.flush()
            os.fsync(temporal.fileno())

        os.replace(
            archivo_temporal,
            CONOCIMIENTO_FILE,
        )

    except OSError as exc:
        raise PersistenciaConocimientoError(
            "No fue posible actualizar el archivo de conocimiento."
        ) from exc

    finally:
        if (
            archivo_temporal
            and os.path.exists(archivo_temporal)
        ):
            os.remove(archivo_temporal)


def _existe_id(
    elementos: list[dict],
    identificador: str,
) -> bool:
    return any(
        elemento["id"] == identificador
        for elemento in elementos
    )


def crear_sintoma(datos: dict[str, Any]) -> dict:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()

        if _existe_id(conocimiento["sintomas"], datos["id"]):
            raise ConflictoConocimientoError(
                f"Ya existe el síntoma '{datos['id']}'."
            )

        nuevo = {
            "id": datos["id"],
            "nombre": datos["nombre"],
            "categoria": datos["categoria"],
        }

        conocimiento["sintomas"].append(nuevo)
        _guardar_conocimiento(conocimiento)

        return nuevo


def actualizar_sintoma(
    identificador: str,
    datos: dict[str, Any],
) -> dict:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()
        indice = _buscar_indice(
            conocimiento["sintomas"],
            identificador,
        )

        actualizado = {
            "id": identificador,
            "nombre": datos["nombre"],
            "categoria": datos["categoria"],
        }

        conocimiento["sintomas"][indice] = actualizado
        _guardar_conocimiento(conocimiento)

        return actualizado


def eliminar_sintoma(identificador: str) -> None:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()

        if len(conocimiento["sintomas"]) <= MIN_SINTOMAS:
            raise ConflictoConocimientoError(
                "No se puede reducir la cantidad de síntomas "
                f"por debajo de {MIN_SINTOMAS}."
            )

        indice = _buscar_indice(
            conocimiento["sintomas"],
            identificador,
        )

        reglas_relacionadas = [
            regla["id"]
            for regla in conocimiento["reglas"]
            if identificador in regla["sintomas"]
        ]

        if reglas_relacionadas:
            raise ConflictoConocimientoError(
                "El síntoma está asociado a las reglas: "
                + ", ".join(reglas_relacionadas)
            )

        conocimiento["sintomas"].pop(indice)
        _guardar_conocimiento(conocimiento)


def crear_falla(datos: dict[str, Any]) -> dict:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()

        if _existe_id(conocimiento["fallas"], datos["id"]):
            raise ConflictoConocimientoError(
                f"Ya existe la falla '{datos['id']}'."
            )

        nueva = {
            "id": datos["id"],
            "nombre": datos["nombre"],
            "descripcion": datos["descripcion"],
        }

        conocimiento["fallas"].append(nueva)
        _guardar_conocimiento(conocimiento)

        return nueva


def actualizar_falla(
    identificador: str,
    datos: dict[str, Any],
) -> dict:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()
        indice = _buscar_indice(
            conocimiento["fallas"],
            identificador,
        )

        actualizada = {
            "id": identificador,
            "nombre": datos["nombre"],
            "descripcion": datos["descripcion"],
        }

        conocimiento["fallas"][indice] = actualizada
        _guardar_conocimiento(conocimiento)

        return actualizada


def eliminar_falla(identificador: str) -> None:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()

        if len(conocimiento["fallas"]) <= MIN_FALLAS:
            raise ConflictoConocimientoError(
                "No se puede reducir la cantidad de fallas "
                f"por debajo de {MIN_FALLAS}."
            )

        indice = _buscar_indice(
            conocimiento["fallas"],
            identificador,
        )

        recomendaciones = [
            item["id"]
            for item in conocimiento["recomendaciones"]
            if item["falla_id"] == identificador
        ]

        reglas = [
            item["id"]
            for item in conocimiento["reglas"]
            if item["falla_id"] == identificador
        ]

        if recomendaciones or reglas:
            relaciones = recomendaciones + reglas

            raise ConflictoConocimientoError(
                "La falla tiene asociaciones activas: "
                + ", ".join(relaciones)
            )

        conocimiento["fallas"].pop(indice)
        _guardar_conocimiento(conocimiento)


def crear_recomendacion(datos: dict[str, Any]) -> dict:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()

        if _existe_id(
            conocimiento["recomendaciones"],
            datos["id"],
        ):
            raise ConflictoConocimientoError(
                f"Ya existe la recomendación '{datos['id']}'."
            )

        if not _existe_id(
            conocimiento["fallas"],
            datos["falla_id"],
        ):
            raise RecursoNoEncontradoError(
                f"No existe la falla '{datos['falla_id']}'."
            )

        recomendacion_existente = next(
            (
                item
                for item in conocimiento["recomendaciones"]
                if item["falla_id"] == datos["falla_id"]
            ),
            None,
        )

        if recomendacion_existente:
            raise ConflictoConocimientoError(
                "La falla ya tiene asociada la recomendación "
                f"'{recomendacion_existente['id']}'."
            )

        nueva = {
            "id": datos["id"],
            "falla_id": datos["falla_id"],
            "texto": datos["texto"],
        }

        conocimiento["recomendaciones"].append(nueva)
        _guardar_conocimiento(conocimiento)

        return nueva


def actualizar_recomendacion(
    identificador: str,
    datos: dict[str, Any],
) -> dict:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()
        indice = _buscar_indice(
            conocimiento["recomendaciones"],
            identificador,
        )

        if not _existe_id(
            conocimiento["fallas"],
            datos["falla_id"],
        ):
            raise RecursoNoEncontradoError(
                f"No existe la falla '{datos['falla_id']}'."
            )

        recomendacion_existente = next(
            (
                item
                for item in conocimiento["recomendaciones"]
                if (
                    item["falla_id"] == datos["falla_id"]
                    and item["id"] != identificador
                )
            ),
            None,
        )

        if recomendacion_existente:
            raise ConflictoConocimientoError(
                "La falla ya tiene asociada la recomendación "
                f"'{recomendacion_existente['id']}'."
            )

        actualizada = {
            "id": identificador,
            "falla_id": datos["falla_id"],
            "texto": datos["texto"],
        }

        conocimiento["recomendaciones"][indice] = actualizada
        _guardar_conocimiento(conocimiento)

        return actualizada


def eliminar_recomendacion(identificador: str) -> None:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()

        if len(conocimiento["recomendaciones"]) <= MIN_RECOMENDACIONES:
            raise ConflictoConocimientoError(
                "No se puede reducir la cantidad de recomendaciones "
                f"por debajo de {MIN_RECOMENDACIONES}."
            )

        indice = _buscar_indice(
            conocimiento["recomendaciones"],
            identificador,
        )

        recomendacion = conocimiento["recomendaciones"][indice]

        reglas_relacionadas = [
            regla["id"]
            for regla in conocimiento["reglas"]
            if regla["falla_id"] == recomendacion["falla_id"]
        ]

        if reglas_relacionadas:
            raise ConflictoConocimientoError(
                "La recomendación pertenece a una falla utilizada "
                "por las reglas: "
                + ", ".join(reglas_relacionadas)
            )

        conocimiento["recomendaciones"].pop(indice)
        _guardar_conocimiento(conocimiento)


def crear_regla(datos: dict[str, Any]) -> dict:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()

        if _existe_id(conocimiento["reglas"], datos["id"]):
            raise ConflictoConocimientoError(
                f"Ya existe la regla '{datos['id']}'."
            )

        if not _existe_id(
            conocimiento["fallas"],
            datos["falla_id"],
        ):
            raise RecursoNoEncontradoError(
                f"No existe la falla '{datos['falla_id']}'."
            )

        tiene_recomendacion = any(
            item["falla_id"] == datos["falla_id"]
            for item in conocimiento["recomendaciones"]
        )

        if not tiene_recomendacion:
            raise ConflictoConocimientoError(
                "La falla debe tener una recomendación antes "
                "de asociarla con una regla."
            )

        sintomas_existentes = {
            item["id"]
            for item in conocimiento["sintomas"]
        }

        sintomas_inexistentes = [
            sintoma
            for sintoma in datos["sintomas"]
            if sintoma not in sintomas_existentes
        ]

        if sintomas_inexistentes:
            raise RecursoNoEncontradoError(
                "No existen los síntomas: "
                + ", ".join(sintomas_inexistentes)
            )

        nueva = {
            "id": datos["id"],
            "falla_id": datos["falla_id"],
            "sintomas": datos["sintomas"],
        }

        conocimiento["reglas"].append(nueva)
        _guardar_conocimiento(conocimiento)

        return nueva


def actualizar_regla(
    identificador: str,
    datos: dict[str, Any],
) -> dict:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()
        indice = _buscar_indice(
            conocimiento["reglas"],
            identificador,
        )

        if not _existe_id(
            conocimiento["fallas"],
            datos["falla_id"],
        ):
            raise RecursoNoEncontradoError(
                f"No existe la falla '{datos['falla_id']}'."
            )

        tiene_recomendacion = any(
            item["falla_id"] == datos["falla_id"]
            for item in conocimiento["recomendaciones"]
        )

        if not tiene_recomendacion:
            raise ConflictoConocimientoError(
                "La falla seleccionada no tiene una recomendación."
            )

        sintomas_existentes = {
            item["id"]
            for item in conocimiento["sintomas"]
        }

        sintomas_inexistentes = [
            sintoma
            for sintoma in datos["sintomas"]
            if sintoma not in sintomas_existentes
        ]

        if sintomas_inexistentes:
            raise RecursoNoEncontradoError(
                "No existen los síntomas: "
                + ", ".join(sintomas_inexistentes)
            )

        actualizada = {
            "id": identificador,
            "falla_id": datos["falla_id"],
            "sintomas": datos["sintomas"],
        }

        conocimiento["reglas"][indice] = actualizada
        _guardar_conocimiento(conocimiento)

        return actualizada


def eliminar_regla(identificador: str) -> None:
    with _WRITE_LOCK:
        conocimiento = _cargar_conocimiento()

        if len(conocimiento["reglas"]) <= MIN_REGLAS:
            raise ConflictoConocimientoError(
                "No se puede reducir la cantidad de reglas "
                f"por debajo de {MIN_REGLAS}."
            )

        indice = _buscar_indice(
            conocimiento["reglas"],
            identificador,
        )

        conocimiento["reglas"].pop(indice)
        _guardar_conocimiento(conocimiento)
