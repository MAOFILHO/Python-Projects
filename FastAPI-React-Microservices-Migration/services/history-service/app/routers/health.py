from common.schemas import HealthResponse
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlmodel import Session

from app.database import get_session

SERVICE_NAME = "history-service"
VERSION = "0.1.0"

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(session: Session = Depends(get_session)) -> HealthResponse:
    try:
        session.exec(text("SELECT 1"))
        status = "ok"
    except Exception:
        status = "down"
    return HealthResponse(service=SERVICE_NAME, status=status, version=VERSION)
