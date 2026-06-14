import logging

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    DiagnosticoRequest,
    DiagnosticoResponse
)

from app.services.historial_service import (
    guardar_diagnostico
)

from app.services.prolog_service import (
    ConocimientoValidationError,
    PrologServiceError,
    diagnosticar_con_prolog,
    obtener_sintomas_disponibles
)

from app.services.telegram_service import (
    enviar_diagnostico_telegram
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Diagnóstico"]
)


@router.get("/sintomas")
def listar_sintomas():
    try:
        return {
            "sintomas": obtener_sintomas_disponibles()
        }

    except PrologServiceError as exc:
        logger.exception(
            "No fue posible obtener los síntomas desde Prolog."
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El motor de diagnóstico no está disponible."
        ) from exc


@router.post(
    "/diagnosticar",
    response_model=DiagnosticoResponse
)
def diagnosticar(
    request: DiagnosticoRequest
):
    try:
        resultado = diagnosticar_con_prolog(
            request.sintomas
        )

    except ConocimientoValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
        ) from exc

    except PrologServiceError as exc:
        logger.exception(
            "Error al ejecutar el diagnóstico en Prolog."
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El motor de diagnóstico no está disponible."
        ) from exc

    telegram_enviado = enviar_diagnostico_telegram(
        sintomas=request.sintomas,
        falla_texto=resultado["falla_texto"],
        recomendacion=resultado["recomendacion"],
        coincidencias=resultado["coincidencias"],
        chat_id=request.telegram_chat_id
    )

    respuesta = {
        "sintomas": request.sintomas,
        "falla": resultado["falla"],
        "falla_texto": resultado["falla_texto"],
        "recomendacion": resultado["recomendacion"],
        "coincidencias": resultado["coincidencias"],
        "telegram_enviado": telegram_enviado
    }

    try:
        guardar_diagnostico(
            respuesta
        )

    except (OSError, ValueError) as exc:
        logger.exception(
            "No fue posible guardar el diagnóstico."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El diagnóstico fue generado, pero no pudo guardarse."
        ) from exc

    return respuesta