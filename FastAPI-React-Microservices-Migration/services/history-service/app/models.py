from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class OperationRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    operation: str
    operand_a: float
    operand_b: float
    result: float
    mode: str  # "monolith" | "microservices"
    handled_by: str
    correlation_id: str
    latency_ms: float
    created_at: datetime = Field(default_factory=_utcnow)
