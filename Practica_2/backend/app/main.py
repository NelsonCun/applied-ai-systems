import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.answers import router as answers_router
from app.api.routes.auth import router as auth_router
from app.api.routes.bot import router as bot_router
from app.api.routes.categories import router as categories_router
from app.api.routes.health import router as health_router
from app.api.routes.queries import router as queries_router
from app.api.routes.query_logs import router as query_logs_router
from app.api.routes.questions import router as questions_router
from app.api.routes.settings import router as settings_router
from app.api.routes.statistics import router as statistics_router
from app.core.config import settings


logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


app = FastAPI(
    title=settings.app_name,
    description=(
        "API REST para la administración de preguntas frecuentes, "
        "respuestas, categorías y consultas recibidas desde Telegram."
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

app.include_router(
    auth_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    categories_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    questions_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    answers_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    queries_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    settings_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    query_logs_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    statistics_router,
    prefix=settings.api_v1_prefix,
)

app.include_router(
    bot_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "documentation": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
