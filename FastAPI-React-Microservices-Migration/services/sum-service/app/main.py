from common.correlation import get_or_create_correlation_id
from common.schemas import HealthResponse
from fastapi import FastAPI, Request

from app.arithmetic import my_sum
from app.schemas import OperationRequest, OperationResponse

SERVICE_NAME = "sum-service"
VERSION = "0.1.0"

app = FastAPI(title="Sum Service")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(service=SERVICE_NAME, status="ok", version=VERSION)


@app.post("/sum", response_model=OperationResponse)
async def sum_endpoint(payload: OperationRequest, request: Request) -> OperationResponse:
    # Correlation id is made available for future use (logging/tracing) even
    # though this simple service doesn't do anything else with it yet.
    get_or_create_correlation_id(request.headers)
    result = my_sum(*payload.values)
    return OperationResponse(result=result, service=SERVICE_NAME)
