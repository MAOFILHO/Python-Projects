import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app


@pytest.fixture()
def client(tmp_path):
    db_file = tmp_path / "test_api_history.db"
    engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _sample_payload(**overrides):
    payload = {
        "operation": "sum",
        "operand_a": 2,
        "operand_b": 3,
        "result": 5,
        "mode": "monolith",
        "handled_by": "monolith",
        "correlation_id": "corr-1",
        "latency_ms": 1.2,
    }
    payload.update(overrides)
    return payload


def test_health_returns_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "history-service"


def test_post_and_get_history(client):
    post_resp = client.post("/history", json=_sample_payload())
    assert post_resp.status_code == 201
    created = post_resp.json()
    assert created["result"] == 5
    assert created["id"] is not None

    get_resp = client.get("/history")
    assert get_resp.status_code == 200
    page = get_resp.json()
    assert page["total"] == 1
    assert len(page["items"]) == 1
    assert page["items"][0]["operation"] == "sum"


def test_history_stats_reflects_inserted_record(client):
    client.post("/history", json=_sample_payload())
    client.post("/history", json=_sample_payload(mode="microservices", handled_by="sum-service"))

    resp = client.get("/history/stats")
    assert resp.status_code == 200
    stats = resp.json()
    assert "monolith" in stats["by_mode"]
    assert "microservices" in stats["by_mode"]
    assert stats["by_mode"]["monolith"]["count"] == 1
    assert stats["by_mode"]["monolith"]["avg_ms"] == 1.2


def test_pagination_limit_and_offset(client):
    for i in range(5):
        client.post("/history", json=_sample_payload(operand_a=i))

    page1 = client.get("/history", params={"limit": 2, "offset": 0}).json()
    page2 = client.get("/history", params={"limit": 2, "offset": 2}).json()

    assert page1["total"] == 5
    assert len(page1["items"]) == 2
    assert len(page2["items"]) == 2
    assert page1["items"][0]["id"] != page2["items"][0]["id"]


def test_stats_empty_history_returns_no_crash(client):
    resp = client.get("/history/stats")
    assert resp.status_code == 200
    assert resp.json()["by_mode"] == {}
