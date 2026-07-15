from common.trace import TraceHop
from pydantic import BaseModel


class OperationRequest(BaseModel):
    values: list[float]


class OperationResponse(BaseModel):
    result: float
    service: str
    trace: list[TraceHop]
