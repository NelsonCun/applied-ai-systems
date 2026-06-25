# RoboMaze

RoboMaze es una aplicación web para representar laberintos bidimensionales y comparar algoritmos clásicos de búsqueda en inteligencia artificial.

## Algoritmos

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- A* como funcionalidad adicional

Los movimientos permitidos son exclusivamente:

- Arriba
- Derecha
- Abajo
- Izquierda

No se permiten movimientos diagonales.

## Tecnologías

- Python 3.11 o superior
- FastAPI
- HTML
- CSS
- JavaScript
- Pytest

## Ejecución inicial

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La aplicación estará disponible en:

Interfaz: http://127.0.0.1:8002
Swagger: http://127.0.0.1:8002/docs
Salud: http://127.0.0.1:8002/api/v1/health

## Ejecución
```bash
cd Practica_4
source .venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```
