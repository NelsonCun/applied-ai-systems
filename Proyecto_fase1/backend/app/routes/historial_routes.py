from fastapi import APIRouter
from app.services.historial_service import leer_historial, limpiar_historial


router = APIRouter(prefix="/api", tags=["Historial"])


@router.get("/historial")
def obtener_historial():
    return {
        "historial": leer_historial()
    }


@router.delete("/historial")
def eliminar_historial():
    limpiar_historial()
    return {
        "mensaje": "Historial eliminado correctamente"
    }
