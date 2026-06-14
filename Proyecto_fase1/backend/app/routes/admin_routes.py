from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.models.admin_schemas import (
    FallaCreate,
    FallaUpdate,
    RecomendacionCreate,
    RecomendacionUpdate,
    ReglaCreate,
    ReglaUpdate,
    SintomaCreate,
    SintomaUpdate,
)

from app.models.config_schemas import TelegramConfigUpdate

from app.services.configuracion_service import (
    ConfiguracionError,
    actualizar_configuracion_telegram,
    obtener_configuracion_telegram,
)

from app.services.conocimiento_service import (
    ConflictoConocimientoError,
    PersistenciaConocimientoError,
    RecursoNoEncontradoError,
    actualizar_falla,
    actualizar_recomendacion,
    actualizar_regla,
    actualizar_sintoma,
    crear_falla,
    crear_recomendacion,
    crear_regla,
    crear_sintoma,
    eliminar_falla,
    eliminar_recomendacion,
    eliminar_regla,
    eliminar_sintoma,
    listar_fallas,
    listar_recomendaciones,
    listar_reglas,
    listar_sintomas,
)

from app.services.prolog_service import PrologServiceError


router = APIRouter(
    prefix="/api/admin",
    tags=["Administración"],
)


def ejecutar_operacion(
    funcion: Callable[..., Any],
    *args: Any,
) -> Any:
    try:
        return funcion(*args)

    except RecursoNoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ConflictoConocimientoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except PrologServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El motor de conocimiento no está disponible.",
        ) from exc

    except PersistenciaConocimientoError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except ConfiguracionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/sintomas")
def obtener_sintomas_admin():
    return {
        "sintomas": ejecutar_operacion(listar_sintomas)
    }


@router.post(
    "/sintomas",
    status_code=status.HTTP_201_CREATED,
)
def registrar_sintoma(datos: SintomaCreate):
    return ejecutar_operacion(
        crear_sintoma,
        datos.model_dump(),
    )


@router.put("/sintomas/{identificador}")
def modificar_sintoma(
    identificador: str,
    datos: SintomaUpdate,
):
    return ejecutar_operacion(
        actualizar_sintoma,
        identificador,
        datos.model_dump(),
    )


@router.delete("/sintomas/{identificador}")
def borrar_sintoma(identificador: str):
    ejecutar_operacion(
        eliminar_sintoma,
        identificador,
    )

    return {
        "mensaje": "Síntoma eliminado correctamente."
    }


@router.get("/fallas")
def obtener_fallas_admin():
    return {
        "fallas": ejecutar_operacion(listar_fallas)
    }


@router.post(
    "/fallas",
    status_code=status.HTTP_201_CREATED,
)
def registrar_falla(datos: FallaCreate):
    return ejecutar_operacion(
        crear_falla,
        datos.model_dump(),
    )


@router.put("/fallas/{identificador}")
def modificar_falla(
    identificador: str,
    datos: FallaUpdate,
):
    return ejecutar_operacion(
        actualizar_falla,
        identificador,
        datos.model_dump(),
    )


@router.delete("/fallas/{identificador}")
def borrar_falla(identificador: str):
    ejecutar_operacion(
        eliminar_falla,
        identificador,
    )

    return {
        "mensaje": "Falla eliminada correctamente."
    }


@router.get("/recomendaciones")
def obtener_recomendaciones_admin():
    return {
        "recomendaciones": ejecutar_operacion(
            listar_recomendaciones
        )
    }


@router.post(
    "/recomendaciones",
    status_code=status.HTTP_201_CREATED,
)
def registrar_recomendacion(
    datos: RecomendacionCreate,
):
    return ejecutar_operacion(
        crear_recomendacion,
        datos.model_dump(),
    )


@router.put("/recomendaciones/{identificador}")
def modificar_recomendacion(
    identificador: str,
    datos: RecomendacionUpdate,
):
    return ejecutar_operacion(
        actualizar_recomendacion,
        identificador,
        datos.model_dump(),
    )


@router.delete("/recomendaciones/{identificador}")
def borrar_recomendacion(identificador: str):
    ejecutar_operacion(
        eliminar_recomendacion,
        identificador,
    )

    return {
        "mensaje": "Recomendación eliminada correctamente."
    }


@router.get("/reglas")
def obtener_reglas_admin():
    return {
        "reglas": ejecutar_operacion(listar_reglas)
    }


@router.post(
    "/reglas",
    status_code=status.HTTP_201_CREATED,
)
def registrar_regla(datos: ReglaCreate):
    return ejecutar_operacion(
        crear_regla,
        datos.model_dump(),
    )


@router.put("/reglas/{identificador}")
def modificar_regla(
    identificador: str,
    datos: ReglaUpdate,
):
    return ejecutar_operacion(
        actualizar_regla,
        identificador,
        datos.model_dump(),
    )


@router.delete("/reglas/{identificador}")
def borrar_regla(identificador: str):
    ejecutar_operacion(
        eliminar_regla,
        identificador,
    )

    return {
        "mensaje": "Regla eliminada correctamente."
    }


@router.get("/configuracion/telegram")
def consultar_configuracion_telegram():
    return ejecutar_operacion(obtener_configuracion_telegram)


@router.put("/configuracion/telegram")
def modificar_configuracion_telegram(datos: TelegramConfigUpdate):
    return ejecutar_operacion(
        actualizar_configuracion_telegram,
        datos.model_dump(),
    )
