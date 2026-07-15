"""POST /api/operations/sum and /api/operations/mul.

Total latency is computed as wall-clock time from when the gateway started
handling the request until the response is built (not the sum of hop
durations) - this reflects what the caller actually experienced, including
any gateway-side overhead between hops.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from common.correlation import get_or_create_correlation_id
from common.trace import TraceHop, make_hop
from fastapi import APIRouter, HTTPException, Request

from app.clients import call_downstream
from app.config import HISTORY_URL, MONOLITH_URL, MUL_URL, SUM_URL
from app.schemas import OperationRequest, OperationResponse

router = APIRouter(prefix="/api/operations", tags=["operations"])


async def _handle_operation(operation: str, payload: OperationRequest, request: Request) -> OperationResponse:
    request_start = time.perf_counter()
    correlation_id = get_or_create_correlation_id(request.headers)
    headers = {"X-Request-ID": correlation_id}
    trace: list[TraceHop] = []

    if payload.mode == "microservices":
        service_name = "sum-service" if operation == "sum" else "mul-service"
        base_url = SUM_URL if operation == "sum" else MUL_URL
    else:
        service_name = "monolith"
        base_url = MONOLITH_URL

    compute_started_at = datetime.now(timezone.utc)
    body, duration_ms, status = await call_downstream(
        "POST",
        f"{base_url}/{operation}",
        json={"values": [payload.a, payload.b]},
        headers=headers,
    )
    trace.append(make_hop(service_name, "compute", compute_started_at, duration_ms, status))

    if status == "error" or body is None:
        raise HTTPException(
            status_code=502,
            detail=f"{service_name} is unreachable or returned an error while computing '{operation}'.",
        )

    result = body["result"]

    # Best-effort history logging: never fail the overall request because of
    # this call, just record the hop as an error and move on.
    history_started_at = datetime.now(timezone.utc)
    _history_body, history_duration_ms, history_status = await call_downstream(
        "POST",
        f"{HISTORY_URL}/history",
        json={
            "operation": operation,
            "operand_a": payload.a,
            "operand_b": payload.b,
            "result": result,
            "mode": payload.mode,
            "handled_by": service_name,
            "correlation_id": correlation_id,
            "latency_ms": duration_ms,
        },
        headers=headers,
    )
    trace.append(make_hop("history-service", "record", history_started_at, history_duration_ms, history_status))

    total_latency_ms = (time.perf_counter() - request_start) * 1000

    return OperationResponse(
        result=result,
        mode=payload.mode,
        operation=operation,
        correlation_id=correlation_id,
        total_latency_ms=total_latency_ms,
        trace=trace,
    )


@router.post("/sum", response_model=OperationResponse)
async def sum_operation(payload: OperationRequest, request: Request) -> OperationResponse:
    return await _handle_operation("sum", payload, request)


@router.post("/mul", response_model=OperationResponse)
async def mul_operation(payload: OperationRequest, request: Request) -> OperationResponse:
    return await _handle_operation("mul", payload, request)
