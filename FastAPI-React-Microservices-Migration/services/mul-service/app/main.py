from common.correlation import get_or_create_correlation_id
from common.schemas import HealthResponse
from fastapi import FastAPI, Request

from app.arithmetic import my_mul
from app.schemas import OperationRequest, OperationResponse

SERVICE_NAME = "mul-service"
VERSION = "0.1.0"

app = FastAPI(title="Mul Service")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(service=SERVICE_NAME, status="ok", version=VERSION)


@app.post("/mul", response_model=OperationResponse)
async def mul_endpoint(payload: OperationRequest, request: Request) -> OperationResponse:
    get_or_create_correlation_id(request.headers)
    result = my_mul(*payload.values)
    return OperationResponse(result=result, service=SERVICE_NAME)
