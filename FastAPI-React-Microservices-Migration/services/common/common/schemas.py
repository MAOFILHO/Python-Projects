"""Shared response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Standard health-check payload returned by every service."""

    service: str
    status: Literal["ok", "down"]
    version: str
