from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "sum-service"


def test_sum_valid_returns_correct_result():
    resp = client.post("/sum", json={"values": [1, 2, 3]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"] == 6
    assert body["service"] == "sum-service"


def test_sum_malformed_body_returns_422():
    resp = client.post("/sum", json={"values": "not-a-list"})
    assert resp.status_code == 422
