from fastapi import APIRouter, HTTPException
from app.schemas.route_schema import RouteRequest
from app.services.route_service import RouteService

router = APIRouter(prefix="/api/routes", tags=["Routes"])
service = RouteService()


@router.post("/shortest")
def shortest_route(request: RouteRequest):
    try:
        result = service.shortest_route(request.origin, request.destination)

        if result is None:
            raise HTTPException(status_code=404, detail="No existe una ruta disponible.")

        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/all")
def all_routes(request: RouteRequest):
    try:
        result = service.all_routes(request.origin, request.destination)

        if not result:
            raise HTTPException(status_code=404, detail="No existen rutas disponibles.")

        return {
            "total_routes": len(result),
            "routes": result
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))