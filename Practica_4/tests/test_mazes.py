from fastapi.testclient import TestClient

from app.algorithms.bfs import breadth_first_search
from app.data.predefined_mazes import PREDEFINED_MAZES
from app.main import app


client = TestClient(app)


def maze_positions(maze):
    start = (
        maze.start.row,
        maze.start.column,
    )
    goal = (
        maze.goal.row,
        maze.goal.column,
    )
    obstacles = {
        (
            obstacle.row,
            obstacle.column,
        )
        for obstacle in maze.obstacles
    }

    return start, goal, obstacles


def test_catalog_contains_at_least_five_solvable_mazes() -> None:
    solvable = [
        maze
        for maze in PREDEFINED_MAZES
        if maze.has_solution
    ]

    assert len(solvable) >= 5


def test_first_five_predefined_mazes_are_solvable() -> None:
    solvable = [
        maze
        for maze in PREDEFINED_MAZES
        if maze.has_solution
    ]

    for maze in solvable:
        start, goal, obstacles = maze_positions(maze)

        result = breadth_first_search(
            rows=maze.rows,
            columns=maze.columns,
            start=start,
            goal=goal,
            obstacles=obstacles,
        )

        assert result.found is True, (
            f"El laberinto {maze.id} debería tener solución."
        )


def test_no_solution_maze_is_not_solvable() -> None:
    maze = next(
        maze
        for maze in PREDEFINED_MAZES
        if maze.id == "no-solution"
    )

    start, goal, obstacles = maze_positions(maze)

    result = breadth_first_search(
        rows=maze.rows,
        columns=maze.columns,
        start=start,
        goal=goal,
        obstacles=obstacles,
    )

    assert result.found is False


def test_list_mazes_endpoint() -> None:
    response = client.get("/api/v1/mazes")

    assert response.status_code == 200
    assert len(response.json()) >= 6


def test_get_predefined_maze_endpoint() -> None:
    response = client.get("/api/v1/mazes/basic")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == "basic"
    assert body["name"] == "Introducción"
    assert body["has_solution"] is True
    assert len(body["obstacles"]) > 0


def test_unknown_maze_returns_404() -> None:
    response = client.get(
        "/api/v1/mazes/not-found",
    )

    assert response.status_code == 404


def test_generated_maze_is_reproducible_and_solvable() -> None:
    payload = {
        "rows": 15,
        "columns": 15,
        "obstacle_density": 0.30,
        "seed": 2026,
    }

    first_response = client.post(
        "/api/v1/mazes/generate",
        json=payload,
    )
    second_response = client.post(
        "/api/v1/mazes/generate",
        json=payload,
    )

    assert first_response.status_code == 200
    assert first_response.json() == second_response.json()

    maze = first_response.json()

    obstacles = {
        (
            obstacle["row"],
            obstacle["column"],
        )
        for obstacle in maze["obstacles"]
    }

    result = breadth_first_search(
        rows=maze["rows"],
        columns=maze["columns"],
        start=(
            maze["start"]["row"],
            maze["start"]["column"],
        ),
        goal=(
            maze["goal"]["row"],
            maze["goal"]["column"],
        ),
        obstacles=obstacles,
    )

    assert result.found is True
    assert len(obstacles) > 0
