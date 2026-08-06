import os

os.environ["LAHJA_MOCK_MODE"] = "true"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_transform_mock() -> None:
    response = client.post(
        "/api/transform",
        json={
            "text": "mar7aba kifak shu l akhbar",
            "source_dialect": "lebanese",
            "target_dialect": "syrian",
            "input_script": "arabizi",
            "output_script": "arabic",
            "tone": "casual",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["transformed_text"]
    assert body["mock_mode"] is True
