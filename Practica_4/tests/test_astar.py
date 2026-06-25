from app.algorithms.astar import (
    a_star_search,
    manhattan_distance,
)
from app.algorithms.bfs import breadth_first_search


def test_manhattan_distance() -> None:
    assert manhattan_distance((0, 0), (3, 4)) == 7
    assert manhattan_distance((2, 2), (2, 2)) == 0


def test_astar_finds_optimal_path() -> None:
    obstacles = {
        (1, 1),
        (1, 2),
        (1, 3),
    }

    bfs_result = breadth_first_search(
        rows=5,
        columns=5,
        start=(0, 0),
        goal=(4, 4),
        obstacles=obstacles,
    )

    astar_result = a_star_search(
        rows=5,
        columns=5,
        start=(0, 0),
        goal=(4, 4),
        obstacles=obstacles,
    )

    assert astar_result.found is True
    assert astar_result.path_length == bfs_result.path_length
    assert astar_result.path[0] == (0, 0)
    assert astar_result.path[-1] == (4, 4)
