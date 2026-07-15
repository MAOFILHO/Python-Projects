from pydantic import BaseModel


class OperationRequest(BaseModel):
    values: list[float]


class OperationResponse(BaseModel):
    result: float
    service: str
