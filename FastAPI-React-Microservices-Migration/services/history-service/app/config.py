"""Environment-driven configuration for history-service."""

import os
from pathlib import Path

HOST = os.getenv("HISTORY_HOST", "0.0.0.0")
PORT = int(os.getenv("HISTORY_PORT", "8003"))
DB_PATH = os.getenv("HISTORY_DB_PATH", "./data/history.db")

# Ensure the parent directory for the DB file exists (no-op for ":memory:"
# or other non-file paths that don't have a meaningful parent to create).
_parent = Path(DB_PATH).parent
if str(_parent) not in ("", "."):
    _parent.mkdir(parents=True, exist_ok=True)
