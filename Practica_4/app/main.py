from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="RoboMaze API",
    description=(
        "API REST para ejecutar algoritmos de búsqueda dentro de "
        "laberintos bidimensionales."
    ),
    version="1.0.0",
)

app.include_router(api_router, prefix="/api/v1", tags=["Sistema"])

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.get("/", include_in_schema=False)
def serve_frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
