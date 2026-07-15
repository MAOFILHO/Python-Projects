from datetime import datetime

from pydantic import BaseModel


class OperationCreate(BaseModel):
    operation: str
    operand_a: float
    operand_b: float
    result: float
    mode: str
    handled_by: str
    correlation_id: str
    latency_ms: float


class OperationRead(BaseModel):
    id: int
    operation: str
    operand_a: float
    operand_b: float
    result: float
    mode: str
    handled_by: str
    correlation_id: str
    latency_ms: float
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryPage(BaseModel):
    items: list[OperationRead]
    total: int


class ModeStats(BaseModel):
    count: int
    avg_ms: float
    min_ms: float
    max_ms: float
    recent_ms: list[float]


class HistoryStats(BaseModel):
    by_mode: dict[str, ModeStats]
