from random import Random

from app.data.predefined_mazes import PREDEFINED_MAZES
from app.models.schemas import (
    Coordinate,
    GenerateMazeRequest,
    MazeConfiguration,
    MazeSummary,
    PredefinedMaze,
)


def list_predefined_mazes() -> list[MazeSummary]:
    """Devuelve el catálogo resumido de laberintos."""

    return [
        MazeSummary(
            id=maze.id,
            name=maze.name,
            description=maze.description,
            rows=maze.rows,
            columns=maze.columns,
            has_solution=maze.has_solution,
        )
        for maze in PREDEFINED_MAZES
    ]


def get_predefined_maze(
    maze_id: str,
) -> PredefinedMaze | None:
    """Busca un laberinto por su identificador."""

    return next(
        (
            maze.model_copy(deep=True)
            for maze in PREDEFINED_MAZES
            if maze.id == maze_id
        ),
        None,
    )


def build_protected_path(
    rows: int,
    columns: int,
) -> set[tuple[int, int]]:
    """
    Construye una ruta libre garantizada.

    La ruta recorre la primera fila y después desciende por
    la última columna.
    """

    protected = {
        (0, column)
        for column in range(columns)
    }

    protected.update(
        (row, columns - 1)
        for row in range(rows)
    )

    return protected


def generate_maze(
    request: GenerateMazeRequest,
) -> MazeConfiguration:
    """
    Genera un laberinto aleatorio con una ruta válida garantizada.

    No se utiliza una base de datos. El resultado existe únicamente
    en memoria y se devuelve al cliente.
    """

    random_generator = Random(request.seed)

    start = (0, 0)
    goal = (
        request.rows - 1,
        request.columns - 1,
    )

    protected_path = build_protected_path(
        request.rows,
        request.columns,
    )

    available_positions = [
        (row, column)
        for row in range(request.rows)
        for column in range(request.columns)
        if (
            (row, column) not in protected_path
            and (row, column) != start
            and (row, column) != goal
        )
    ]

    requested_obstacles = round(
        request.rows
        * request.columns
        * request.obstacle_density
    )

    obstacle_count = min(
        requested_obstacles,
        len(available_positions),
    )

    selected_obstacles = random_generator.sample(
        available_positions,
        obstacle_count,
    )

    return MazeConfiguration(
        rows=request.rows,
        columns=request.columns,
        start=Coordinate(
            row=start[0],
            column=start[1],
        ),
        goal=Coordinate(
            row=goal[0],
            column=goal[1],
        ),
        obstacles=[
            Coordinate(row=row, column=column)
            for row, column in sorted(selected_obstacles)
        ],
    )
