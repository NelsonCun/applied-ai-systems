from app.algorithms.dfs import depth_first_search


def test_dfs_finds_a_valid_path() -> None:
    result = depth_first_search(
        rows=4,
        columns=4,
        start=(0, 0),
        goal=(3, 3),
        obstacles={(1, 1), (2, 1)},
    )

    assert result.found is True
    assert result.path[0] == (0, 0)
    assert result.path[-1] == (3, 3)
    assert result.path_length == len(result.path) - 1

    for position in result.path:
        assert position not in {(1, 1), (2, 1)}


def test_dfs_reports_no_route() -> None:
    result = depth_first_search(
        rows=3,
        columns=3,
        start=(0, 0),
        goal=(2, 2),
        obstacles={(0, 1), (1, 0)},
    )

    assert result.found is False
    assert result.path == []
    assert result.explored_order == [(0, 0)]
