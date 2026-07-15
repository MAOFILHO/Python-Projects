from __future__ import annotations

from typing import Literal

from common.trace import TraceHop
from pydantic import BaseModel


class OperationRequest(BaseModel):
    a: float
    b: float
    mode: Literal["monolith", "microservices"]


class OperationResponse(BaseModel):
    result: float
    mode: str
    operation: str
    correlation_id: str
    total_latency_ms: float
    trace: list[TraceHop]


class ServiceHealth(BaseModel):
    service: str
    status: Literal["ok", "down"]
    latency_ms: float


class HealthAggregate(BaseModel):
    services: list[ServiceHealth]
    overall: Literal["ok", "degraded"]
