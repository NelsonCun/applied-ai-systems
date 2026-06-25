from time import perf_counter_ns

from app.algorithms.common import (
    Position,
    SearchOutcome,
    build_outcome,
    get_neighbors,
    reconstruct_path,
)


def depth_first_search(
    *,
    rows: int,
    columns: int,
    start: Position,
    goal: Position,
    obstacles: set[Position],
) -> SearchOutcome:
    """
    Ejecuta Depth-First Search.

    DFS utiliza una pila LIFO. Puede encontrar una solución cuando
    existe, pero no garantiza que sea la ruta más corta.
    """

    started_at = perf_counter_ns()

    frontier: list[Position] = [start]
    discovered: set[Position] = {start}
    parents: dict[Position, Position | None] = {
        start: None,
    }
    explored_order: list[Position] = []

    while frontier:
        current = frontier.pop()
        explored_order.append(current)

        if current == goal:
            path = reconstruct_path(parents, goal)
            finished_at = perf_counter_ns()

            return build_outcome(
                found=True,
                path=path,
                explored_order=explored_order,
                execution_time_ns=finished_at - started_at,
            )

        neighbors = get_neighbors(
            current,
            rows,
            columns,
            obstacles,
        )

        # Se insertan en orden inverso para que, al extraer de la pila,
        # se procese primero: arriba, derecha, abajo e izquierda.
        for neighbor in reversed(neighbors):
            if neighbor in discovered:
                continue

            discovered.add(neighbor)
            parents[neighbor] = current
            frontier.append(neighbor)

    finished_at = perf_counter_ns()

    return build_outcome(
        found=False,
        path=[],
        explored_order=explored_order,
        execution_time_ns=finished_at - started_at,
    )
