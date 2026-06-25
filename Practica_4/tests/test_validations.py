import pytest
from pydantic import ValidationError

from app.models.schemas import (
    Coordinate,
    MazeConfiguration,
)


def test_rejects_start_outside_maze() -> None:
    with pytest.raises(ValidationError):
        MazeConfiguration(
            rows=5,
            columns=5,
            start=Coordinate(row=5, column=0),
            goal=Coordinate(row=4, column=4),
            obstacles=[],
        )


def test_rejects_equal_start_and_goal() -> None:
    with pytest.raises(ValidationError):
        MazeConfiguration(
            rows=5,
            columns=5,
            start=Coordinate(row=0, column=0),
            goal=Coordinate(row=0, column=0),
            obstacles=[],
        )


def test_rejects_obstacle_on_goal() -> None:
    with pytest.raises(ValidationError):
        MazeConfiguration(
            rows=5,
            columns=5,
            start=Coordinate(row=0, column=0),
            goal=Coordinate(row=4, column=4),
            obstacles=[
                Coordinate(row=4, column=4),
            ],
        )


def test_rejects_repeated_obstacles() -> None:
    with pytest.raises(ValidationError):
        MazeConfiguration(
            rows=5,
            columns=5,
            start=Coordinate(row=0, column=0),
            goal=Coordinate(row=4, column=4),
            obstacles=[
                Coordinate(row=2, column=2),
                Coordinate(row=2, column=2),
            ],
        )
