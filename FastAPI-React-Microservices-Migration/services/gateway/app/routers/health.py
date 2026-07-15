"""GET /api/health - aggregates health of all downstream services.

This endpoint must never 500: every downstream call is individually
guarded, and any failure just marks that service "down" rather than
propagating an exception.
"""

from __future__ import annotations

import asyncio
import time

from fastapi import APIRouter

from app.clients import call_downstream
from app.config import HISTORY_URL, MONOLITH_URL, MUL_URL, SUM_URL
from app.schemas import HealthAggregate, ServiceHealth

router = APIRouter(prefix="/api", tags=["health"])

_DOWNSTREAMS = {
    "sum-service": SUM_URL,
    "mul-service": MUL_URL,
    "monolith": MONOLITH_URL,
    "history-service": HISTORY_URL,
}


async def _check(service: str, base_url: str) -> ServiceHealth:
    body, duration_ms, status = await call_downstream("GET", f"{base_url}/health")
    if status == "ok" and body is not None and body.get("status") == "ok":
        return ServiceHealth(service=service, status="ok", latency_ms=duration_ms)
    return ServiceHealth(service=service, status="down", latency_ms=duration_ms)


@router.get("/health", response_model=HealthAggregate)
async def health() -> HealthAggregate:
    start = time.perf_counter()
    results = await asyncio.gather(
        *(_check(service, base_url) for service, base_url in _DOWNSTREAMS.items()),
        return_exceptions=True,
    )

    services: list[ServiceHealth] = [ServiceHealth(service="gateway", status="ok", latency_ms=0.0)]
    for service, result in zip(_DOWNSTREAMS.keys(), results):
        if isinstance(result, Exception):
            services.append(
                ServiceHealth(service=service, status="down", latency_ms=(time.perf_counter() - start) * 1000)
            )
        else:
            services.append(result)

    overall = "ok" if all(s.status == "ok" for s in services) else "degraded"
    return HealthAggregate(services=services, overall=overall)
