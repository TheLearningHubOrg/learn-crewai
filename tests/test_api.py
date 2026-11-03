from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": "offline"}


def test_create_brief():
    response = client.post("/briefs", json={"topic": "hierarchical process", "audience": "tech leads"})
    assert response.status_code == 200
    body = response.json()
    assert body["brief"]["topic"] == "hierarchical process"
    assert body["research_notes"].startswith("Research notes on hierarchical process")


def test_rejects_short_topic():
    response = client.post("/briefs", json={"topic": "x"})
    assert response.status_code == 422
