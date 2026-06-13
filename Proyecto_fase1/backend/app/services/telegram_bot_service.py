import logging
import os
import re
import threading
from typing import Any

from app.services.configuracion_service import (
    ConfiguracionError,
    obtener_configuracion_telegram,
)
from app.services.historial_service import (
    HistorialError,
    guardar_diagnostico,
)
from app.services.prolog_service import (
    ConocimientoValidationError,
    PrologServiceError,
    diagnosticar_con_prolog,
    obtener_sintomas_disponibles,
)
from app.services.telegram_service import (
    TelegramServiceError,
    construir_mensaje_diagnostico,
    enviar_mensaje_telegram,
    obtener_actualizaciones,
    token_telegram_configurado,
)


logger = logging.getLogger(__name__)

POLLING_TIMEOUT = int(
    os.getenv("TELEGRAM_POLLING_TIMEOUT", "25")
)

REINTENTO_SEGUNDOS = 3

_STOP_EVENT = threading.Event()
_BOT_THREAD: threading.Thread | None = None

_CONVERSACIONES: dict[str, str] = {}


def iniciar_bot_telegram() -> None:
    global _BOT_THREAD

    if _BOT_THREAD and _BOT_THREAD.is_alive():
        return

    _STOP_EVENT.clear()

    _BOT_THREAD = threading.Thread(
        target=_bucle_polling,
        name="doctor-byte-telegram-bot",
        daemon=True,
    )

    _BOT_THREAD.start()


def detener_bot_telegram() -> None:
    _STOP_EVENT.set()

    if _BOT_THREAD and _BOT_THREAD.is_alive():
        _BOT_THREAD.join(timeout=2)


def _bucle_polling() -> None:
    offset: int | None = None

    logger.info(
        "Listener de Telegram iniciado."
    )

    try:
        while not _STOP_EVENT.is_set():
            if not token_telegram_configurado():
                logger.warning(
                    "TELEGRAM_BOT_TOKEN no está configurado."
                )

                _STOP_EVENT.wait(
                    REINTENTO_SEGUNDOS
                )

                continue

            try:
                actualizaciones = obtener_actualizaciones(
                    offset=offset,
                    timeout=POLLING_TIMEOUT,
                )

                for actualizacion in actualizaciones:
                    update_id = actualizacion.get(
                        "update_id"
                    )

                    if isinstance(update_id, int):
                        offset = update_id + 1

                    _procesar_actualizacion(
                        actualizacion
                    )

            except TelegramServiceError as exc:
                logger.warning(
                    "Error de Telegram: %s",
                    exc,
                )

                _STOP_EVENT.wait(
                    REINTENTO_SEGUNDOS
                )

            except Exception:
                logger.exception(
                    "Error inesperado en el listener de Telegram."
                )

                _STOP_EVENT.wait(
                    REINTENTO_SEGUNDOS
                )

    finally:
        logger.info(
            "Listener de Telegram detenido."
        )


def _procesar_actualizacion(
    actualizacion: dict[str, Any],
) -> None:
    mensaje = actualizacion.get("message")

    if not isinstance(mensaje, dict):
        return

    texto = mensaje.get("text")
    chat = mensaje.get("chat")

    if not isinstance(texto, str):
        return

    if not isinstance(chat, dict):
        return

    chat_id = str(
        chat.get("id", "")
    ).strip()

    if not chat_id:
        return

    try:
        configuracion = obtener_configuracion_telegram()

    except ConfiguracionError:
        logger.exception(
            "No fue posible leer la configuración de Telegram."
        )

        return

    if not configuracion["activo"]:
        return

    comando, argumentos = _separar_comando(
        texto
    )

    if comando == "/id":
        enviar_mensaje_telegram(
            chat_id,
            f"El ID de este chat es: {chat_id}",
        )

        return

    chat_autorizado = configuracion[
        "chat_id"
    ].strip()

    if (
        chat_autorizado
        and chat_id != chat_autorizado
    ):
        enviar_mensaje_telegram(
            chat_id,
            (
                "Este chat no está autorizado para "
                "utilizar Doctor Byte."
            ),
        )

        return

    if comando == "/start":
        _CONVERSACIONES.pop(
            chat_id,
            None,
        )

        enviar_mensaje_telegram(
            chat_id,
            _mensaje_inicio(
                configuracion[
                    "mensaje_bienvenida"
                ]
            ),
        )

        return

    if comando == "/ayuda":
        enviar_mensaje_telegram(
            chat_id,
            _mensaje_ayuda(),
        )

        return

    if comando == "/sintomas":
        _enviar_lista_sintomas(
            chat_id
        )

        return

    if comando == "/cancelar":
        _CONVERSACIONES.pop(
            chat_id,
            None,
        )

        enviar_mensaje_telegram(
            chat_id,
            (
                "La selección de síntomas "
                "fue cancelada."
            ),
        )

        return

    if comando == "/diagnosticar":
        if argumentos:
            _diagnosticar_desde_texto(
                chat_id=chat_id,
                texto=argumentos,
                configuracion=configuracion,
            )

        else:
            _CONVERSACIONES[
                chat_id
            ] = "esperando_sintomas"

            enviar_mensaje_telegram(
                chat_id,
                (
                    "Envíe los números o identificadores "
                    "de los síntomas separados por comas."
                    "\n\n"
                    + _texto_lista_sintomas()
                    + "\n\n"
                    "Ejemplo: 4, 8, 9\n"
                    "Use /cancelar para salir."
                ),
            )

        return

    if comando:
        enviar_mensaje_telegram(
            chat_id,
            (
                "No reconozco ese comando."
                "\n\n"
                + _mensaje_ayuda()
            ),
        )

        return

    if (
        _CONVERSACIONES.get(chat_id)
        == "esperando_sintomas"
    ):
        _diagnosticar_desde_texto(
            chat_id=chat_id,
            texto=texto,
            configuracion=configuracion,
        )

        return

    enviar_mensaje_telegram(
        chat_id,
        (
            "Use /diagnosticar para iniciar una "
            "consulta o /ayuda para ver los "
            "comandos disponibles."
        ),
    )


def _separar_comando(
    texto: str,
) -> tuple[str, str]:
    texto_limpio = texto.strip()

    if not texto_limpio.startswith("/"):
        return "", texto_limpio

    partes = texto_limpio.split(
        maxsplit=1
    )

    comando = partes[0].split(
        "@",
        maxsplit=1,
    )[0].lower()

    argumentos = (
        partes[1].strip()
        if len(partes) > 1
        else ""
    )

    return comando, argumentos


def _mensaje_inicio(
    mensaje_bienvenida: str,
) -> str:
    return (
        f"{mensaje_bienvenida}\n\n"
        "Puedo consultar el motor experto de "
        "Doctor Byte y generar un diagnóstico "
        "preliminar.\n\n"
        + _mensaje_ayuda()
    )


def _mensaje_ayuda() -> str:
    return (
        "Comandos disponibles:\n"
        "/start - Mostrar bienvenida\n"
        "/sintomas - Ver síntomas disponibles\n"
        "/diagnosticar - Iniciar un diagnóstico\n"
        "/diagnosticar 4,8,9 - Diagnosticar directamente\n"
        "/cancelar - Cancelar la selección actual\n"
        "/id - Mostrar el ID del chat\n"
        "/ayuda - Mostrar esta ayuda"
    )


def _obtener_sintomas() -> list[dict[str, str]]:
    sintomas = obtener_sintomas_disponibles()

    return [
        {
            "id": str(item["id"]),
            "nombre": str(item["nombre"]),
            "categoria": str(
                item.get(
                    "categoria",
                    "Otros",
                )
            ),
        }
        for item in sintomas
    ]


def _texto_lista_sintomas() -> str:
    try:
        sintomas = _obtener_sintomas()

    except (
        PrologServiceError,
        KeyError,
        TypeError,
    ):
        return (
            "No fue posible cargar los "
            "síntomas disponibles."
        )

    lineas = [
        "Síntomas disponibles:"
    ]

    categoria_actual: str | None = None

    for indice, sintoma in enumerate(
        sintomas,
        start=1,
    ):
        categoria = sintoma["categoria"]

        if categoria != categoria_actual:
            categoria_actual = categoria

            lineas.append(
                f"\n{categoria}:"
            )

        lineas.append(
            f"{indice}. "
            f"{sintoma['nombre']} "
            f"({sintoma['id']})"
        )

    return "\n".join(lineas)


def _enviar_lista_sintomas(
    chat_id: str,
) -> None:
    enviar_mensaje_telegram(
        chat_id,
        (
            _texto_lista_sintomas()
            + "\n\n"
            "Para diagnosticar use /diagnosticar."
        ),
    )


def _resolver_selecciones(
    texto: str,
    sintomas: list[dict[str, str]],
) -> tuple[list[str], list[str]]:
    texto_normalizado = re.sub(
        r"\s+y\s+",
        ",",
        texto.strip().lower(),
    )

    tokens = [
        token
        for token in re.split(
            r"[,;\s]+",
            texto_normalizado,
        )
        if token
    ]

    ids_disponibles = {
        sintoma["id"]
        for sintoma in sintomas
    }

    seleccionados: list[str] = []
    invalidos: list[str] = []

    for token in tokens:
        sintoma_id: str | None = None

        if token.isdigit():
            indice = int(token) - 1

            if 0 <= indice < len(sintomas):
                sintoma_id = sintomas[
                    indice
                ]["id"]

        elif token in ids_disponibles:
            sintoma_id = token

        if sintoma_id is None:
            invalidos.append(token)
            continue

        if sintoma_id not in seleccionados:
            seleccionados.append(
                sintoma_id
            )

    return seleccionados, invalidos


def _diagnosticar_desde_texto(
    chat_id: str,
    texto: str,
    configuracion: dict[str, Any],
) -> None:
    try:
        sintomas_disponibles = (
            _obtener_sintomas()
        )

        sintomas, invalidos = (
            _resolver_selecciones(
                texto,
                sintomas_disponibles,
            )
        )

        if invalidos:
            enviar_mensaje_telegram(
                chat_id,
                (
                    "No reconocí estas selecciones: "
                    + ", ".join(invalidos)
                    + ".\n\n"
                    "Use /sintomas para consultar "
                    "la lista."
                ),
            )

            return

        if not sintomas:
            enviar_mensaje_telegram(
                chat_id,
                (
                    "Debe seleccionar al menos un "
                    "síntoma. Use /sintomas para "
                    "consultar la lista."
                ),
            )

            return

        resultado = diagnosticar_con_prolog(
            sintomas
        )

        mensaje = construir_mensaje_diagnostico(
            sintomas=sintomas,
            falla_texto=resultado[
                "falla_texto"
            ],
            recomendacion=resultado[
                "recomendacion"
            ],
            coincidencias=resultado[
                "coincidencias"
            ],
            encabezado=configuracion[
                "encabezado_diagnostico"
            ],
            despedida=configuracion[
                "mensaje_despedida"
            ],
        )

        telegram_enviado = (
            enviar_mensaje_telegram(
                chat_id,
                mensaje,
            )
        )

        guardar_diagnostico({
            "sintomas": sintomas,
            "falla": resultado["falla"],
            "falla_texto": resultado[
                "falla_texto"
            ],
            "recomendacion": resultado[
                "recomendacion"
            ],
            "coincidencias": resultado[
                "coincidencias"
            ],
            "telegram_enviado": (
                telegram_enviado
            ),
        })

        if telegram_enviado:
            _CONVERSACIONES.pop(
                chat_id,
                None,
            )

    except ConocimientoValidationError as exc:
        enviar_mensaje_telegram(
            chat_id,
            str(exc),
        )

    except PrologServiceError:
        logger.exception(
            "No fue posible consultar Prolog "
            "desde Telegram."
        )

        enviar_mensaje_telegram(
            chat_id,
            (
                "El motor de diagnóstico "
                "no está disponible."
            ),
        )

    except HistorialError:
        logger.exception(
            "El diagnóstico de Telegram "
            "no pudo guardarse."
        )

        enviar_mensaje_telegram(
            chat_id,
            (
                "El diagnóstico fue generado, "
                "pero no pudo guardarse en "
                "el historial."
            ),
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        logger.exception(
            "Los datos de diagnóstico no tienen "
            "el formato esperado."
        )

        enviar_mensaje_telegram(
            chat_id,
            (
                "No fue posible procesar "
                "el diagnóstico."
            ),
        )