"""Trace hop model + a small timing helper used to build hops for a request trace.

A ``TraceHop`` represents one unit of work performed by one service while
handling a request (e.g. "monolith computed a sum in-process", or "sum-service
received a call over the network"). Chaining hops together across services
lets a caller see where time was spent.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class TraceHop(BaseModel):
    """A single timed step in a request's processing trace."""

    service: str
    action: str
    started_at: datetime
    duration_ms: float
    status: Literal["ok", "error"] = "ok"


class _HopBuilder:
    """Mutable helper populated by :func:`timed_hop` once the block finishes."""

    def __init__(self) -> None:
        self.hop: TraceHop | None = None


@contextmanager
def timed_hop(service: str, action: str) -> Iterator[_HopBuilder]:
    """Context manager that times a block of code and yields a builder.

    Usage::

        with timed_hop("monolith", "compute_sum") as builder:
            result = my_sum(*values)
        hop = builder.hop  # populated after the `with` block exits

    On exception, the hop is still recorded with ``status="error"`` and the
    exception is re-raised.
    """
    builder = _HopBuilder()
    started_at = datetime.now(timezone.utc)
    start = time.perf_counter()
    status: Literal["ok", "error"] = "ok"
    try:
        yield builder
    except Exception:
        status = "error"
        raise
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        builder.hop = TraceHop(
            service=service,
            action=action,
            started_at=started_at,
            duration_ms=duration_ms,
            status=status,
        )


def make_hop(
    service: str,
    action: str,
    started_at: datetime,
    duration_ms: float,
    status: Literal["ok", "error"] = "ok",
) -> TraceHop:
    """Build a :class:`TraceHop` directly, without the context manager."""
    return TraceHop(
        service=service,
        action=action,
        started_at=started_at,
        duration_ms=duration_ms,
        status=status,
    )
