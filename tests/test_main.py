
import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_database = tmp_path / "test_evalforge.db"
    monkeypatch.setattr(main, "DB_PATH", test_database)

    with TestClient(main.app) as test_client:
        yield test_client


def make_payload():
    return {
        "prompt": "Test prompt",
        "response_a": "Response A",
        "response_b": "Response B",
        "score_a": 4,
        "score_b": 3,
        "notes": "Automated test",
        "accuracy_a": 5,
        "relevance_a": 4,
        "clarity_a": 5,
        "completeness_a": 4,
        "accuracy_b": 3,
        "relevance_b": 3,
        "clarity_b": 3,
        "completeness_b": 3,
    }


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_evaluation_rejects_empty_data(client):
    response = client.post("/api/evaluations", json={})
    assert response.status_code == 422


def test_create_evaluation(client):
    response = client.post(
        "/api/evaluations",
        json=make_payload()
    )

    assert response.status_code == 201
    assert response.json()["id"] > 0
    assert response.json()["message"] == "Evaluation saved successfully."


@pytest.mark.parametrize(
    "scores, expected_winner",
    [
        (
            {
                "accuracy_a": 5, "relevance_a": 5,
                "clarity_a": 5, "completeness_a": 5,
                "accuracy_b": 1, "relevance_b": 1,
                "clarity_b": 1, "completeness_b": 1,
            },
            "A",
        ),
        (
            {
                "accuracy_a": 1, "relevance_a": 1,
                "clarity_a": 1, "completeness_a": 1,
                "accuracy_b": 5, "relevance_b": 5,
                "clarity_b": 5, "completeness_b": 5,
            },
            "B",
        ),
        (
            {
                "accuracy_a": 4, "relevance_a": 4,
                "clarity_a": 4, "completeness_a": 4,
                "accuracy_b": 4, "relevance_b": 4,
                "clarity_b": 4, "completeness_b": 4,
            },
            "Tie",
        ),
    ],
)
def test_winner_calculation(client, scores, expected_winner):
    payload = make_payload()
    payload.update(scores)

    created = client.post("/api/evaluations", json=payload)
    assert created.status_code == 201

    evaluation_id = created.json()["id"]
    evaluations = client.get("/api/evaluations").json()

    saved = next(
        item for item in evaluations
        if item["id"] == evaluation_id
    )

    assert saved["winner"] == expected_winner


def test_evaluation_history(client):
    created = client.post(
        "/api/evaluations",
        json=make_payload()
    )

    evaluation_id = created.json()["id"]
    response = client.get("/api/evaluations")

    assert response.status_code == 200
    assert any(
        item["id"] == evaluation_id
        for item in response.json()
    )


def test_stats_endpoint(client):
    client.post("/api/evaluations", json=make_payload())

    response = client.get("/api/stats")

    assert response.status_code == 200

    data = response.json()
    assert data["total_evaluations"] == 1
    assert data["winner_counts"]["A"] == 1
    assert data["average_score"] == 3.5
    assert len(data["score_distribution"]) > 0


def test_delete_evaluation(client):
    created = client.post(
        "/api/evaluations",
        json=make_payload()
    )

    evaluation_id = created.json()["id"]

    deleted = client.delete(
        f"/api/evaluations/{evaluation_id}"
    )

    assert deleted.status_code == 200
    assert deleted.json()["message"] == "Evaluation deleted."

    history = client.get("/api/evaluations").json()

    assert all(
        item["id"] != evaluation_id
        for item in history
    )


def test_delete_nonexistent_evaluation(client):
    response = client.delete("/api/evaluations/999999")
    assert response.status_code == 404
