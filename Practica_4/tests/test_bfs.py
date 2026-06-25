from app.algorithms.bfs import breadth_first_search


def test_bfs_finds_shortest_path() -> None:
    result = breadth_first_search(
        rows=3,
        columns=3,
        start=(0, 0),
        goal=(0, 2),
        obstacles=set(),
    )

    assert result.found is True
    assert result.path == [
        (0, 0),
        (0, 1),
        (0, 2),
    ]
    assert result.path_length == 2
    assert result.explored_nodes >= 3


def test_bfs_reports_no_route() -> None:
    result = breadth_first_search(
        rows=3,
        columns=3,
        start=(0, 0),
        goal=(2, 2),
        obstacles={(0, 1), (1, 0)},
    )

    assert result.found is False
    assert result.path == []
    assert result.path_length == 0
    assert result.explored_order == [(0, 0)]
