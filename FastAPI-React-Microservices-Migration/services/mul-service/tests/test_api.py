from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "mul-service"


def test_mul_valid_returns_correct_result():
    resp = client.post("/mul", json={"values": [2, 3, 4]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"] == 24
    assert body["service"] == "mul-service"


def test_mul_malformed_body_returns_422():
    resp = client.post("/mul", json={"values": "not-a-list"})
    assert resp.status_code == 422
