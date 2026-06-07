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
        result = service.add_city(request.name)
        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/connections")
def add_connection(request: ConnectionRequest):
    try:
        result = service.add_connection(
            request.origin,
            request.destination,
            request.distance
        )
        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))