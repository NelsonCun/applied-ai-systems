from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description=(
        "API REST para la administración de preguntas frecuentes "
        "y la integración con Telegram."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "documentation": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
