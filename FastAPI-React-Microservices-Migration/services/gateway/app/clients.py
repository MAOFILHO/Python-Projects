"""Thin httpx-based helpers for calling downstream services.

Every helper here is careful to never let a downstream failure (connection
refused, timeout, non-2xx, ...) raise up into a route handler. Callers get
back a uniform ``(json_body, duration_ms, status)`` tuple instead, where
``status`` is ``"ok"`` or ``"error"``. Route handlers decide what to do with
an "error" result (e.g. the primary compute call surfaces a 502, while the
best-effort history call just records the failed hop and moves on).
"""

from __future__ import annotations

import time
from typing import Any, Literal

import httpx

from app.config import REQUEST_TIMEOUT_SECONDS

CallStatus = Literal["ok", "error"]


async def call_downstream(
    method: str,
    url: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = REQUEST_TIMEOUT_SECONDS,
) -> tuple[dict[str, Any] | None, float, CallStatus]:
    """Call a downstream service and return ``(body, duration_ms, status)``.

    Never raises: connection errors, timeouts, and non-2xx responses are all
    turned into ``status == "error"`` with ``body == None``.
    """
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(method, url, json=json, params=params, headers=headers)
        duration_ms = (time.perf_counter() - start) * 1000
        response.raise_for_status()
        return response.json(), duration_ms, "ok"
    except (httpx.HTTPError, ValueError):
        duration_ms = (time.perf_counter() - start) * 1000
        return None, duration_ms, "error"
