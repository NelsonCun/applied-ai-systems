from fastapi import APIRouter, HTTPException
from app.schemas.route_schema import CityRequest, ConnectionRequest
from app.services.route_service import RouteService

router = APIRouter(prefix="/api", tags=["Cities and Connections"])
service = RouteService()


@router.get("/cities")
def list_cities():
    return {
        "cities": service.list_cities()
    }


@router.post("/cities")
def add_city(request: CityRequest):
    try:
        ok = service.add_city(request.name)

        if not ok:
            raise HTTPException(status_code=400, detail="No se pudo agregar la ciudad.")

        return {
            "message": "Ciudad agregada correctamente."
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/connections")
def add_connection(request: ConnectionRequest):
    try:
        ok = service.add_connection(
            request.origin,
            request.destination,
            request.distance
        )

        if not ok:
            raise HTTPException(
                status_code=400,
                detail="No se pudo agregar la conexión. Puede que ya exista."
            )

        return {
            "message": "Conexión agregada correctamente."
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))