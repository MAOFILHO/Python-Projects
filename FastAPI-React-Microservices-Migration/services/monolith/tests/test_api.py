from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "monolith"


def test_sum_returns_trace_with_exactly_one_hop():
    resp = client.post("/sum", json={"values": [1, 2, 3]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"] == 6
    assert body["service"] == "monolith"
    assert len(body["trace"]) == 1
    hop = body["trace"][0]
    assert hop["service"] == "monolith"
    assert hop["action"] == "compute_sum"
    assert hop["status"] == "ok"


def test_mul_returns_trace_with_exactly_one_hop():
    resp = client.post("/mul", json={"values": [2, 3, 4]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"] == 24
    assert len(body["trace"]) == 1
    assert body["trace"][0]["action"] == "compute_mul"


def test_sum_malformed_body_returns_422():
    resp = client.post("/sum", json={"values": "nope"})
    assert resp.status_code == 422
