"""GET /api/history and /api/history/stats - thin proxies to history-service."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.clients import call_downstream
from app.config import HISTORY_URL

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def list_history(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)) -> dict:
    body, _duration_ms, status = await call_downstream(
        "GET", f"{HISTORY_URL}/history", params={"limit": limit, "offset": offset}
    )
    if status == "error" or body is None:
        raise HTTPException(status_code=502, detail="history-service is unreachable.")
    return body


@router.get("/stats")
async def history_stats() -> dict:
    body, _duration_ms, status = await call_downstream("GET", f"{HISTORY_URL}/history/stats")
    if status == "error" or body is None:
        raise HTTPException(status_code=502, detail="history-service is unreachable.")
    return body
