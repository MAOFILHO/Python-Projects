import httpx
import pytest
import respx

from app.config import HISTORY_URL, MONOLITH_URL, MUL_URL, SUM_URL
from app.main import app


@pytest.mark.asyncio
@respx.mock
async def test_health_marks_down_service_and_degrades_overall():
    respx.get(f"{SUM_URL}/health").mock(
        return_value=httpx.Response(200, json={"service": "sum-service", "status": "ok", "version": "0.1.0"})
    )
    respx.get(f"{MUL_URL}/health").mock(
        return_value=httpx.Response(200, json={"service": "mul-service", "status": "ok", "version": "0.1.0"})
    )
    respx.get(f"{MONOLITH_URL}/health").mock(
        return_value=httpx.Response(200, json={"service": "monolith", "status": "ok", "version": "0.1.0"})
    )
    respx.get(f"{HISTORY_URL}/health").mock(side_effect=httpx.ConnectError("connection refused"))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://gateway") as client:
        resp = await client.get("/api/health")

    assert resp.status_code == 200
    body = resp.json()
    assert body["overall"] == "degraded"

    by_service = {s["service"]: s for s in body["services"]}
    assert by_service["history-service"]["status"] == "down"
    assert by_service["sum-service"]["status"] == "ok"
    assert by_service["mul-service"]["status"] == "ok"
    assert by_service["monolith"]["status"] == "ok"
    assert by_service["gateway"]["status"] == "ok"


@pytest.mark.asyncio
@respx.mock
async def test_health_all_up_is_ok():
    for url in (SUM_URL, MUL_URL, MONOLITH_URL, HISTORY_URL):
        respx.get(f"{url}/health").mock(
            return_value=httpx.Response(200, json={"service": "x", "status": "ok", "version": "0.1.0"})
        )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://gateway") as client:
        resp = await client.get("/api/health")

    assert resp.status_code == 200
    assert resp.json()["overall"] == "ok"
