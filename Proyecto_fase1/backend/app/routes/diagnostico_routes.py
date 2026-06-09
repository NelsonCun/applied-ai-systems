from fastapi import APIRouter
from app.models.schemas import DiagnosticoRequest
from app.services.prolog_service import diagnosticar_con_prolog, obtener_sintomas_disponibles
from app.services.telegram_service import enviar_diagnostico_telegram
from app.services.historial_service import guardar_diagnostico


router = APIRouter(prefix="/api", tags=["Diagnóstico"])


@router.get("/sintomas")
def listar_sintomas():
    return {
        "sintomas": obtener_sintomas_disponibles()
    }


@router.post("/diagnosticar")
def diagnosticar(request: DiagnosticoRequest):
    resultado = diagnosticar_con_prolog(request.sintomas)

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

    guardar_diagnostico(respuesta)

    return respuesta
