from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


VALID_MAZE = {
    "rows": 5,
    "columns": 5,
    "start": {
        "row": 0,
        "column": 0,
    },
    "goal": {
        "row": 4,
        "column": 4,
    },
    "obstacles": [
        {
            "row": 1,
            "column": 1,
        },
        {
            "row": 1,
            "column": 2,
        },
    ],
}


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search_endpoint_executes_bfs() -> None:
    payload = {
        **VALID_MAZE,
        "algorithm": "bfs",
    }

    response = client.post(
        "/api/v1/search",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["algorithm"] == "bfs"
    assert body["found"] is True
    assert body["path"][0] == {
        "row": 0,
        "column": 0,
    }
    assert body["path"][-1] == {
        "row": 4,
        "column": 4,
    }


def test_compare_endpoint() -> None:
    response = client.post(
        "/api/v1/search/compare",
        json=VALID_MAZE,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["bfs"]["found"] is True
    assert body["dfs"]["found"] is True
    assert body["astar"]["found"] is True


def test_api_rejects_invalid_algorithm() -> None:
    payload = {
        **VALID_MAZE,
        "algorithm": "invalid",
    }

    response = client.post(
        "/api/v1/search",
        json=payload,
    )

    assert response.status_code == 422
