from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, func, select

from app.database import get_session
from app.models import OperationRecord
from app.schemas import HistoryPage, HistoryStats, ModeStats, OperationCreate, OperationRead

router = APIRouter(prefix="/history", tags=["history"])


@router.post("", response_model=OperationRead, status_code=201)
async def create_operation(
    payload: OperationCreate, session: Session = Depends(get_session)
) -> OperationRecord:
    record = OperationRecord(**payload.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.get("", response_model=HistoryPage)
async def list_history(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> HistoryPage:
    total = session.exec(select(func.count()).select_from(OperationRecord)).one()
    items = session.exec(
        select(OperationRecord)
        .order_by(OperationRecord.created_at.desc(), OperationRecord.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return HistoryPage(items=items, total=total)


@router.get("/stats", response_model=HistoryStats)
async def history_stats(session: Session = Depends(get_session)) -> HistoryStats:
    records = session.exec(select(OperationRecord)).all()

    by_mode_records: dict[str, list[OperationRecord]] = {}
    for record in records:
        by_mode_records.setdefault(record.mode, []).append(record)

    by_mode: dict[str, ModeStats] = {}
    for mode, mode_records in by_mode_records.items():
        # oldest -> newest, then keep the last 10 for a sparkline
        ordered = sorted(mode_records, key=lambda r: (r.created_at, r.id))
        latencies = [r.latency_ms for r in ordered]
        recent = latencies[-10:]
        by_mode[mode] = ModeStats(
            count=len(latencies),
            avg_ms=sum(latencies) / len(latencies),
            min_ms=min(latencies),
            max_ms=max(latencies),
            recent_ms=recent,
        )

    return HistoryStats(by_mode=by_mode)
