from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.routes_router import router as routes_router
from app.routers.cities_router import router as cities_router

app = FastAPI(
    title="Ruta Más Corta Entre Ciudades",
    description="Backend Python integrado con Prolog mediante PySwip.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_router)
app.include_router(cities_router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Backend FastAPI conectado con Prolog"
    }