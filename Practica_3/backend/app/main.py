from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine


app = FastAPI(
    title=settings.project_name,
    description="API REST para procesamiento inteligente de facturas.",
    version="1.0.0",
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
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
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

    healthy = all(value == "available" for value in services.values())

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
