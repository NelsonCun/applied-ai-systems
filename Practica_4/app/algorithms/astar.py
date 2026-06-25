from heapq import heappop, heappush
from itertools import count
from time import perf_counter_ns

from app.algorithms.common import (
    Position,
    SearchOutcome,
    build_outcome,
    get_neighbors,
    reconstruct_path,
)


def manhattan_distance(
    current: Position,
    goal: Position,
) -> int:
    """
    Calcula distancia Manhattan.

    Es adecuada porque RoboMaze solo permite movimientos
    verticales y horizontales.
    """

    return (
        abs(current[0] - goal[0])
        + abs(current[1] - goal[1])
    )


def a_star_search(
    *,
    rows: int,
    columns: int,
    start: Position,
    goal: Position,
    obstacles: set[Position],
) -> SearchOutcome:
    """Ejecuta el algoritmo A* con distancia Manhattan."""

    started_at = perf_counter_ns()

    sequence = count()

    start_heuristic = manhattan_distance(start, goal)

    frontier: list[tuple[int, int, int, Position]] = []
    heappush(
        frontier,
        (
            start_heuristic,
            start_heuristic,
            next(sequence),
            start,
        ),
    )

    parents: dict[Position, Position | None] = {
        start: None,
    }
    costs: dict[Position, int] = {
        start: 0,
    }
    closed: set[Position] = set()
    explored_order: list[Position] = []

    while frontier:
        _, _, _, current = heappop(frontier)

        if current in closed:
            continue

        closed.add(current)
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
            tentative_cost = costs[current] + 1
            known_cost = costs.get(neighbor)

            if (
                known_cost is not None
                and tentative_cost >= known_cost
            ):
                continue

            costs[neighbor] = tentative_cost
            parents[neighbor] = current

            heuristic = manhattan_distance(neighbor, goal)
            total_cost = tentative_cost + heuristic

            heappush(
                frontier,
                (
                    total_cost,
                    heuristic,
                    next(sequence),
                    neighbor,
                ),
            )

    finished_at = perf_counter_ns()

    return build_outcome(
        found=False,
        path=[],
        explored_order=explored_order,
        execution_time_ns=finished_at - started_at,
    )
