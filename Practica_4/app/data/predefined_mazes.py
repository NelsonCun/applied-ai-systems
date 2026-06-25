from app.models.schemas import Coordinate, PredefinedMaze


def coordinates(
    positions: set[tuple[int, int]] | list[tuple[int, int]],
) -> list[Coordinate]:
    """Convierte posiciones internas en coordenadas de respuesta."""

    return [
        Coordinate(row=row, column=column)
        for row, column in sorted(positions)
    ]


BASIC_OBSTACLES = {
    *((2, column) for column in range(1, 7) if column != 4),
    *((5, column) for column in range(1, 7) if column != 2),
}

DETOUR_OBSTACLES = {
    *((4, column) for column in range(0, 9)),
    (1, 4),
    (2, 4),
    (6, 6),
    (7, 6),
    (8, 6),
}

CORRIDOR_OBSTACLES = {
    *((row, 2) for row in range(0, 11) if row != 10),
    *((row, 5) for row in range(1, 12) if row != 1),
    *((row, 8) for row in range(0, 11) if row != 10),
}

MULTIPLE_ROUTES_OBSTACLES = {
    (1, 3),
    (1, 4),
    (1, 9),
    (2, 1),
    (2, 6),
    (2, 9),
    (3, 3),
    (3, 6),
    (3, 11),
    (4, 1),
    (4, 4),
    (4, 8),
    (4, 11),
    (5, 4),
    (5, 6),
    (5, 8),
    (6, 2),
    (6, 6),
    (6, 10),
    (7, 2),
    (7, 5),
    (7, 10),
    (8, 7),
    (8, 11),
}

LARGE_OBSTACLES = {
    *((4, column) for column in range(1, 19) if column not in {4, 14}),
    *((8, column) for column in range(1, 19) if column not in {2, 10}),
    *((12, column) for column in range(1, 19) if column not in {6, 16}),
    *((16, column) for column in range(1, 19) if column not in {3, 12}),
    *((row, 7) for row in range(1, 8) if row != 5),
    *((row, 13) for row in range(9, 16) if row != 14),
}

NO_SOLUTION_OBSTACLES = {
    (5, 6),
    (6, 5),
    (6, 7),
    (7, 6),
    (2, 2),
    (2, 3),
    (3, 2),
}


PREDEFINED_MAZES: tuple[PredefinedMaze, ...] = (
    PredefinedMaze(
        id="basic",
        name="Introducción",
        description=(
            "Laberinto pequeño para observar el funcionamiento "
            "básico de los algoritmos."
        ),
        rows=8,
        columns=8,
        start=Coordinate(row=0, column=0),
        goal=Coordinate(row=7, column=7),
        obstacles=coordinates(BASIC_OBSTACLES),
        has_solution=True,
    ),
    PredefinedMaze(
        id="detour",
        name="Desvío obligatorio",
        description=(
            "Una barrera horizontal obliga al agente a recorrer "
            "el extremo derecho del tablero."
        ),
        rows=10,
        columns=10,
        start=Coordinate(row=1, column=1),
        goal=Coordinate(row=8, column=1),
        obstacles=coordinates(DETOUR_OBSTACLES),
        has_solution=True,
    ),
    PredefinedMaze(
        id="corridors",
        name="Corredores alternados",
        description=(
            "Tres muros verticales con aperturas alternadas forman "
            "un recorrido largo en forma de zigzag."
        ),
        rows=12,
        columns=12,
        start=Coordinate(row=0, column=0),
        goal=Coordinate(row=11, column=11),
        obstacles=coordinates(CORRIDOR_OBSTACLES),
        has_solution=True,
    ),
    PredefinedMaze(
        id="multiple-routes",
        name="Múltiples rutas",
        description=(
            "Contiene varias rutas posibles para comparar la "
            "estrategia de BFS, DFS y A*."
        ),
        rows=10,
        columns=14,
        start=Coordinate(row=0, column=0),
        goal=Coordinate(row=9, column=13),
        obstacles=coordinates(MULTIPLE_ROUTES_OBSTACLES),
        has_solution=True,
    ),
    PredefinedMaze(
        id="large",
        name="Exploración amplia",
        description=(
            "Laberinto de veinte por veinte diseñado para observar "
            "diferencias en nodos explorados y tiempo de ejecución."
        ),
        rows=20,
        columns=20,
        start=Coordinate(row=0, column=0),
        goal=Coordinate(row=19, column=19),
        obstacles=coordinates(LARGE_OBSTACLES),
        has_solution=True,
    ),
    PredefinedMaze(
        id="no-solution",
        name="Objetivo aislado",
        description=(
            "El objetivo se encuentra completamente rodeado y "
            "permite comprobar el manejo de laberintos sin solución."
        ),
        rows=8,
        columns=8,
        start=Coordinate(row=0, column=0),
        goal=Coordinate(row=6, column=6),
        obstacles=coordinates(NO_SOLUTION_OBSTACLES),
        has_solution=False,
    ),
)
