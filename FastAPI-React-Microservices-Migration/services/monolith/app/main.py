from common.correlation import get_or_create_correlation_id
from common.schemas import HealthResponse
from common.trace import timed_hop
from fastapi import FastAPI, Request

from app.arithmetic_mul import my_mul
from app.arithmetic_sum import my_sum
from app.schemas import OperationRequest, OperationResponse

SERVICE_NAME = "monolith"
VERSION = "0.1.0"

app = FastAPI(title="Monolith")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(service=SERVICE_NAME, status="ok", version=VERSION)


@app.post("/sum", response_model=OperationResponse)
async def sum_endpoint(payload: OperationRequest, request: Request) -> OperationResponse:
    get_or_create_correlation_id(request.headers)
    with timed_hop(SERVICE_NAME, "compute_sum") as builder:
        result = my_sum(*payload.values)
    return OperationResponse(result=result, service=SERVICE_NAME, trace=[builder.hop])


@app.post("/mul", response_model=OperationResponse)
async def mul_endpoint(payload: OperationRequest, request: Request) -> OperationResponse:
    get_or_create_correlation_id(request.headers)
    with timed_hop(SERVICE_NAME, "compute_mul") as builder:
        result = my_mul(*payload.values)
    return OperationResponse(result=result, service=SERVICE_NAME, trace=[builder.hop])
