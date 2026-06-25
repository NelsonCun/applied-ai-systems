from io import BytesIO

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    ComparisonResponse,
    GenerateMazeRequest,
    MazeConfiguration,
    MazeSummary,
    PdfReportRequest,
    PredefinedMaze,
    SearchRequest,
    SearchResponse,
)
from app.services.maze_service import (
    generate_maze,
    get_predefined_maze,
    list_predefined_mazes,
)
from app.services.report_service import build_pdf_report
from app.services.search_service import (
    compare_algorithms,
    execute_search,
)


router = APIRouter()


@router.get(
    "/health",
    summary="Verificar estado del servicio",
    description="Comprueba que el backend de RoboMaze está disponible.",
)
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "robomaze-backend",
        "message": "El servicio RoboMaze está funcionando correctamente.",
    }


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Ejecutar un algoritmo de búsqueda",
    description=(
        "Ejecuta BFS, DFS o A* sobre la configuración de laberinto "
        "proporcionada."
    ),
)
def search(request: SearchRequest) -> SearchResponse:
    return execute_search(request)


@router.post(
    "/search/compare",
    response_model=ComparisonResponse,
    summary="Comparar algoritmos",
    description=(
        "Ejecuta BFS, DFS y A* utilizando exactamente el mismo "
        "laberinto."
    ),
)
def compare(
    configuration: MazeConfiguration,
) -> ComparisonResponse:
    return compare_algorithms(configuration)


@router.get(
    "/mazes",
    response_model=list[MazeSummary],
    summary="Listar laberintos predefinidos",
)
def list_mazes() -> list[MazeSummary]:
    return list_predefined_mazes()


@router.post(
    "/mazes/generate",
    response_model=MazeConfiguration,
    summary="Generar un laberinto",
    description=(
        "Genera automáticamente un laberinto aleatorio con una "
        "ruta válida garantizada."
    ),
)
def generate(
    request: GenerateMazeRequest,
) -> MazeConfiguration:
    return generate_maze(request)


@router.get(
    "/mazes/{maze_id}",
    response_model=PredefinedMaze,
    summary="Obtener un laberinto predefinido",
)
def get_maze(maze_id: str) -> PredefinedMaze:
    maze = get_predefined_maze(maze_id)

    if maze is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El laberinto solicitado no existe.",
        )

    return maze


@router.post(
    "/reports/pdf",
    summary="Generar reporte PDF",
    description=(
        "Genera un documento PDF con el laberinto, métricas, "
        "comparación y ruta completa."
    ),
    response_class=StreamingResponse,
)
def generate_pdf_report(
    request: PdfReportRequest,
) -> StreamingResponse:
    pdf_content, filename = build_pdf_report(request)

    return StreamingResponse(
        BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )
