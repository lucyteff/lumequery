
from fastapi.testclient import TestClient
from api import app
import api

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": ""})

    assert response.status_code == 422


def test_ask_rejects_missing_question():
    response = client.post("/ask", json={})

    assert response.status_code == 422


def test_ask_success(monkeypatch):
    expected = {
        "question": "Qual foi o faturamento?",
        "sql": "SELECT 1",
        "row_count": 1,
        "insights": "Faturamento analisado."
    }

    monkeypatch.setattr(
        api,
        "ask_lumequery",
        lambda question: expected
    )

    response = client.post(
        "/ask",
        json={"question": "Qual foi o faturamento?"}
    )

    assert response.status_code == 200
    assert response.json() == expected


def test_ask_handles_internal_error(monkeypatch):
    def raise_error(question):
        raise RuntimeError("Test error")

    monkeypatch.setattr(api, "ask_lumequery", raise_error)

    response = client.post(
        "/ask",
        json={"question": "Test question"}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Test error"
