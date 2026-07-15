"""Correlation-ID helpers.

Services use ``X-Request-ID`` to correlate a single logical request across
process/network boundaries. If a caller doesn't supply one, we mint a fresh
uuid4 so downstream logs/traces still have something to key on.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping

CORRELATION_HEADER = "X-Request-ID"


def get_or_create_correlation_id(headers: Mapping[str, str]) -> str:
    """Return the correlation id from ``headers`` or mint a new uuid4.

    ``headers`` is expected to be case-insensitive-ish (e.g. Starlette's
    ``Headers`` object) but a plain dict works too as long as the key casing
    matches ``CORRELATION_HEADER``.
    """
    for key, value in headers.items():
        if key.lower() == CORRELATION_HEADER.lower() and value:
            return value
    return str(uuid.uuid4())
