from collections.abc import Callable

from app.algorithms.astar import a_star_search
from app.algorithms.bfs import breadth_first_search
from app.algorithms.common import Position, SearchOutcome
from app.algorithms.dfs import depth_first_search
from app.models.schemas import (
    ComparisonResponse,
    Coordinate,
    MazeConfiguration,
    SearchRequest,
    SearchResponse,
)


SearchAlgorithm = Callable[..., SearchOutcome]


ALGORITHMS: dict[str, SearchAlgorithm] = {
    "bfs": breadth_first_search,
    "dfs": depth_first_search,
    "astar": a_star_search,
}

ALGORITHM_NAMES: dict[str, str] = {
    "bfs": "Breadth-First Search (BFS)",
    "dfs": "Depth-First Search (DFS)",
    "astar": "A*",
}


def coordinate_to_position(
    coordinate: Coordinate,
) -> Position:
    return coordinate.row, coordinate.column


def position_to_coordinate(
    position: Position,
) -> Coordinate:
    return Coordinate(
        row=position[0],
        column=position[1],
    )


def execute_algorithm(
    configuration: MazeConfiguration,
    algorithm: str,
) -> SearchResponse:
    """Ejecuta un algoritmo y transforma su resultado interno."""

    search_function = ALGORITHMS[algorithm]

    start = coordinate_to_position(configuration.start)
    goal = coordinate_to_position(configuration.goal)
    obstacles = {
        coordinate_to_position(obstacle)
        for obstacle in configuration.obstacles
    }

    outcome = search_function(
        rows=configuration.rows,
        columns=configuration.columns,
        start=start,
        goal=goal,
        obstacles=obstacles,
    )

    if outcome.found:
        message = (
            f"{ALGORITHM_NAMES[algorithm]} encontró una ruta "
            "entre el origen y el destino."
        )
    else:
        message = (
            f"{ALGORITHM_NAMES[algorithm]} no encontró una ruta "
            "válida entre el origen y el destino."
        )

    return SearchResponse(
        algorithm=algorithm,
        algorithm_name=ALGORITHM_NAMES[algorithm],
        found=outcome.found,
        path=[
            position_to_coordinate(position)
            for position in outcome.path
        ],
        explored_order=[
            position_to_coordinate(position)
            for position in outcome.explored_order
        ],
        path_length=outcome.path_length,
        explored_nodes=outcome.explored_nodes,
        execution_time_ms=outcome.execution_time_ms,
        message=message,
    )


def execute_search(
    request: SearchRequest,
) -> SearchResponse:
    """Ejecuta el algoritmo solicitado por el cliente."""

    return execute_algorithm(
        configuration=request,
        algorithm=request.algorithm,
    )


def compare_algorithms(
    configuration: MazeConfiguration,
) -> ComparisonResponse:
    """Ejecuta BFS, DFS y A* sobre el mismo laberinto."""

    return ComparisonResponse(
        bfs=execute_algorithm(configuration, "bfs"),
        dfs=execute_algorithm(configuration, "dfs"),
        astar=execute_algorithm(configuration, "astar"),
    )
