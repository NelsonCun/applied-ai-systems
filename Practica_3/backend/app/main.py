from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis

from app.core.config import settings
from app.db.connection import close_pool, open_pool, pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()
    yield
    close_pool()


app = FastAPI(
    title=settings.project_name,
    description="API REST para procesamiento inteligente de facturas.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {
        "application": settings.project_name,
        "message": "SmartInvoice API",
        "documentation": "/docs",
    }


@app.get(f"{settings.api_v1_prefix}/health")
def health() -> dict:
    services = {
        "database": "unavailable",
        "redis": "unavailable",
    }

    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS result")
                cursor.fetchone()

        services["database"] = "available"
    except Exception:
        pass

    try:
        redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
        redis_client.ping()
        services["redis"] = "available"
    except Exception:
        pass

    healthy = all(
        service_status == "available"
        for service_status in services.values()
    )

    response = {
        "status": "healthy" if healthy else "degraded",
        "application": settings.project_name,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services,
    }

    if not healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response,
        )

    return response
