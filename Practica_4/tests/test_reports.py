from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


MAZE = {
    "rows": 6,
    "columns": 6,
    "start": {
        "row": 0,
        "column": 0,
    },
    "goal": {
        "row": 5,
        "column": 5,
    },
    "obstacles": [
        {
            "row": 1,
            "column": 1,
        },
        {
            "row": 2,
            "column": 1,
        },
        {
            "row": 3,
            "column": 3,
        },
    ],
}


def test_generate_pdf_report() -> None:
    search_response = client.post(
        "/api/v1/search",
        json={
            **MAZE,
            "algorithm": "bfs",
        },
    )

    assert search_response.status_code == 200

    report_response = client.post(
        "/api/v1/reports/pdf",
        json={
            "maze": MAZE,
            "result": search_response.json(),
            "comparison": None,
        },
    )

    assert report_response.status_code == 200
    assert (
        report_response.headers["content-type"]
        == "application/pdf"
    )
    assert "attachment" in report_response.headers[
        "content-disposition"
    ]
    assert report_response.content.startswith(b"%PDF")
    assert len(report_response.content) > 1500


def test_pdf_requires_results() -> None:
    response = client.post(
        "/api/v1/reports/pdf",
        json={
            "maze": MAZE,
            "result": None,
            "comparison": None,
        },
    )

    assert response.status_code == 422
