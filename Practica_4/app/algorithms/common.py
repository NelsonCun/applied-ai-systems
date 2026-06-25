from dataclasses import dataclass


Position = tuple[int, int]

# Orden determinista:
# arriba, derecha, abajo e izquierda.
DIRECTIONS: tuple[Position, ...] = (
    (-1, 0),
    (0, 1),
    (1, 0),
    (0, -1),
)


@dataclass(slots=True)
class SearchOutcome:
    """Resultado interno compartido por los algoritmos."""

    found: bool
    path: list[Position]
    explored_order: list[Position]
    path_length: int
    explored_nodes: int
    execution_time_ms: float


def get_neighbors(
    position: Position,
    rows: int,
    columns: int,
    obstacles: set[Position],
) -> list[Position]:
    """
    Devuelve los vecinos válidos de una posición.

    Solo se permiten movimientos verticales y horizontales.
    """

    row, column = position
    neighbors: list[Position] = []

    for row_offset, column_offset in DIRECTIONS:
        candidate = (
            row + row_offset,
            column + column_offset,
        )

        candidate_row, candidate_column = candidate

        is_inside = (
            0 <= candidate_row < rows
            and 0 <= candidate_column < columns
        )

        if is_inside and candidate not in obstacles:
            neighbors.append(candidate)

    return neighbors


def reconstruct_path(
    parents: dict[Position, Position | None],
    goal: Position,
) -> list[Position]:
    """Reconstruye la ruta desde el objetivo hasta el origen."""

    path: list[Position] = []
    current: Position | None = goal

    while current is not None:
        path.append(current)
        current = parents[current]

    path.reverse()

    return path


def build_outcome(
    *,
    found: bool,
    path: list[Position],
    explored_order: list[Position],
    execution_time_ns: int,
) -> SearchOutcome:
    """Construye un resultado interno uniforme."""

    return SearchOutcome(
        found=found,
        path=path,
        explored_order=explored_order,
        path_length=max(len(path) - 1, 0),
        explored_nodes=len(explored_order),
        execution_time_ms=round(
            execution_time_ns / 1_000_000,
            6,
        ),
    )
