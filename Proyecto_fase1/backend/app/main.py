from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    admin_routes,
    diagnostico_routes,
    historial_routes,
)
from app.services.telegram_bot_service import (
    detener_bot_telegram,
    iniciar_bot_telegram,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    iniciar_bot_telegram()

    try:
        yield

    finally:
        detener_bot_telegram()


app = FastAPI(
    title="Doctor Byte API",
    description=(
        "Backend para sistema experto de diagnóstico "
        "de fallas en computadoras"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    diagnostico_routes.router
)

app.include_router(
    historial_routes.router
)

app.include_router(
    admin_routes.router
)


@app.get("/")
def home():
    return {
        "mensaje": (
            "Doctor Byte API funcionando correctamente"
        )
    }