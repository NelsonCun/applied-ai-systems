from collections import deque
from time import perf_counter_ns

from app.algorithms.common import (
    Position,
    SearchOutcome,
    build_outcome,
    get_neighbors,
    reconstruct_path,
)


def breadth_first_search(
    *,
    rows: int,
    columns: int,
    start: Position,
    goal: Position,
    obstacles: set[Position],
) -> SearchOutcome:
    """
    Ejecuta Breadth-First Search.

    BFS utiliza una cola FIFO y garantiza una ruta con la menor
    cantidad de movimientos cuando todos los movimientos tienen
    el mismo costo.
    """

    started_at = perf_counter_ns()

    frontier: deque[Position] = deque([start])
    discovered: set[Position] = {start}
    parents: dict[Position, Position | None] = {
        start: None,
    }
    explored_order: list[Position] = []

    while frontier:
        current = frontier.popleft()
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

        for neighbor in get_neighbors(
            current,
            rows,
            columns,
            obstacles,
        ):
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
