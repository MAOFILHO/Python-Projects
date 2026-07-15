import httpx
import pytest
import respx

from app.config import HISTORY_URL, MONOLITH_URL, SUM_URL
from app.main import app


@pytest.mark.asyncio
@respx.mock
async def test_microservices_mode_calls_sum_service_then_history_service():
    respx.post(f"{SUM_URL}/sum").mock(
        return_value=httpx.Response(200, json={"result": 12.0, "service": "sum-service"})
    )
    respx.post(f"{HISTORY_URL}/history").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 1,
                "operation": "sum",
                "operand_a": 5,
                "operand_b": 7,
                "result": 12.0,
                "mode": "microservices",
                "handled_by": "sum-service",
                "correlation_id": "abc",
                "latency_ms": 1.2,
                "created_at": "2026-01-01T00:00:00Z",
            },
        )
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://gateway") as client:
        resp = await client.post("/api/operations/sum", json={"a": 5, "b": 7, "mode": "microservices"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["result"] == 12.0
    assert body["mode"] == "microservices"
    assert len(body["trace"]) >= 2
    services_called = [hop["service"] for hop in body["trace"]]
    assert services_called == ["sum-service", "history-service"]
    assert all(hop["status"] == "ok" for hop in body["trace"])
    assert body["correlation_id"]


@pytest.mark.asyncio
@respx.mock
async def test_monolith_mode_calls_monolith_then_history_service():
    respx.post(f"{MONOLITH_URL}/sum").mock(
        return_value=httpx.Response(
            200, json={"result": 12.0, "service": "monolith", "trace": []}
        )
    )
    respx.post(f"{HISTORY_URL}/history").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 2,
                "operation": "sum",
                "operand_a": 5,
                "operand_b": 7,
                "result": 12.0,
                "mode": "monolith",
                "handled_by": "monolith",
                "correlation_id": "abc",
                "latency_ms": 1.2,
                "created_at": "2026-01-01T00:00:00Z",
            },
        )
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://gateway") as client:
        resp = await client.post("/api/operations/sum", json={"a": 5, "b": 7, "mode": "monolith"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["result"] == 12.0
    assert body["mode"] == "monolith"
    assert len(body["trace"]) >= 1
    services_called = [hop["service"] for hop in body["trace"]]
    assert services_called == ["monolith", "history-service"]


@pytest.mark.asyncio
@respx.mock
async def test_request_id_propagated_when_supplied():
    def sum_responder(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("X-Request-ID") == "my-correlation-id"
        return httpx.Response(200, json={"result": 12.0, "service": "sum-service"})

    def history_responder(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("X-Request-ID") == "my-correlation-id"
        return httpx.Response(
            201,
            json={
                "id": 3,
                "operation": "sum",
                "operand_a": 5,
                "operand_b": 7,
                "result": 12.0,
                "mode": "microservices",
                "handled_by": "sum-service",
                "correlation_id": "my-correlation-id",
                "latency_ms": 1.2,
                "created_at": "2026-01-01T00:00:00Z",
            },
        )

    respx.post(f"{SUM_URL}/sum").mock(side_effect=sum_responder)
    respx.post(f"{HISTORY_URL}/history").mock(side_effect=history_responder)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://gateway") as client:
        resp = await client.post(
            "/api/operations/sum",
            json={"a": 5, "b": 7, "mode": "microservices"},
            headers={"X-Request-ID": "my-correlation-id"},
        )

    assert resp.status_code == 200
    assert resp.json()["correlation_id"] == "my-correlation-id"


@pytest.mark.asyncio
@respx.mock
async def test_request_id_generated_when_absent():
    respx.post(f"{SUM_URL}/sum").mock(
        return_value=httpx.Response(200, json={"result": 12.0, "service": "sum-service"})
    )
    respx.post(f"{HISTORY_URL}/history").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 4,
                "operation": "sum",
                "operand_a": 5,
                "operand_b": 7,
                "result": 12.0,
                "mode": "microservices",
                "handled_by": "sum-service",
                "correlation_id": "generated",
                "latency_ms": 1.2,
                "created_at": "2026-01-01T00:00:00Z",
            },
        )
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://gateway") as client:
        resp = await client.post("/api/operations/sum", json={"a": 5, "b": 7, "mode": "microservices"})

    assert resp.status_code == 200
    correlation_id = resp.json()["correlation_id"]
    assert correlation_id
    # a real uuid4 string, e.g. "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    assert len(correlation_id) == 36


@pytest.mark.asyncio
@respx.mock
async def test_primary_compute_failure_returns_502():
    respx.post(f"{SUM_URL}/sum").mock(side_effect=httpx.ConnectError("connection refused"))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://gateway") as client:
        resp = await client.post("/api/operations/sum", json={"a": 5, "b": 7, "mode": "microservices"})

    assert resp.status_code == 502
