from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Coordinate(BaseModel):
    """Representa una posición dentro del laberinto."""

    model_config = ConfigDict(frozen=True)

    row: int = Field(
        ge=0,
        description="Índice de la fila, comenzando en cero.",
    )
    column: int = Field(
        ge=0,
        description="Índice de la columna, comenzando en cero.",
    )


class MazeConfiguration(BaseModel):
    """Configuración completa de un laberinto bidimensional."""

    rows: int = Field(
        ge=2,
        le=50,
        description="Cantidad de filas del laberinto.",
    )
    columns: int = Field(
        ge=2,
        le=50,
        description="Cantidad de columnas del laberinto.",
    )
    start: Coordinate
    goal: Coordinate
    obstacles: list[Coordinate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_maze(self) -> Self:
        points = [self.start, self.goal, *self.obstacles]

        for point in points:
            if point.row >= self.rows or point.column >= self.columns:
                raise ValueError(
                    "Todas las coordenadas deben encontrarse dentro "
                    "de los límites del laberinto."
                )

        if self.start == self.goal:
            raise ValueError(
                "La posición inicial y la posición objetivo "
                "deben ser diferentes."
            )

        obstacle_positions = {
            (obstacle.row, obstacle.column)
            for obstacle in self.obstacles
        }

        if len(obstacle_positions) != len(self.obstacles):
            raise ValueError(
                "La lista de obstáculos contiene posiciones repetidas."
            )

        start_position = (
            self.start.row,
            self.start.column,
        )
        goal_position = (
            self.goal.row,
            self.goal.column,
        )

        if start_position in obstacle_positions:
            raise ValueError(
                "La posición inicial no puede contener un obstáculo."
            )

        if goal_position in obstacle_positions:
            raise ValueError(
                "La posición objetivo no puede contener un obstáculo."
            )

        return self


class SearchRequest(MazeConfiguration):
    """Solicitud para ejecutar un algoritmo específico."""

    algorithm: Literal["bfs", "dfs", "astar"]


class SearchResponse(BaseModel):
    """Resultado producido por un algoritmo de búsqueda."""

    algorithm: Literal["bfs", "dfs", "astar"]
    algorithm_name: str
    found: bool
    path: list[Coordinate]
    explored_order: list[Coordinate]
    path_length: int
    explored_nodes: int
    execution_time_ms: float
    message: str


class ComparisonResponse(BaseModel):
    """Resultados comparativos de los algoritmos disponibles."""

    bfs: SearchResponse
    dfs: SearchResponse
    astar: SearchResponse


class PdfReportRequest(BaseModel):
    """Información necesaria para generar el reporte PDF."""

    maze: MazeConfiguration
    result: SearchResponse | None = None
    comparison: ComparisonResponse | None = None

    @model_validator(mode="after")
    def validate_report_content(self) -> Self:
        if self.result is None and self.comparison is None:
            raise ValueError(
                "El reporte requiere al menos un resultado "
                "individual o una comparación."
            )

        return self


class MazeSummary(BaseModel):
    """Información resumida de un laberinto predefinido."""

    id: str
    name: str
    description: str
    rows: int
    columns: int
    has_solution: bool


class PredefinedMaze(MazeConfiguration):
    """Laberinto completo disponible en el catálogo."""

    id: str
    name: str
    description: str
    has_solution: bool


class GenerateMazeRequest(BaseModel):
    """Parámetros para generar automáticamente un laberinto."""

    rows: int = Field(
        default=15,
        ge=5,
        le=40,
    )
    columns: int = Field(
        default=15,
        ge=5,
        le=40,
    )
    obstacle_density: float = Field(
        default=0.25,
        ge=0.05,
        le=0.45,
        description="Proporción aproximada de celdas bloqueadas.",
    )
    seed: int | None = Field(
        default=None,
        description=(
            "Semilla opcional para reproducir exactamente "
            "el mismo laberinto."
        ),
    )
