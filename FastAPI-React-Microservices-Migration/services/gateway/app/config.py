"""Environment-driven configuration for the gateway."""

import os

HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
PORT = int(os.getenv("GATEWAY_PORT", "8080"))

SUM_URL = os.getenv("SUM_URL", "http://localhost:8001")
MUL_URL = os.getenv("MUL_URL", "http://localhost:8002")
HISTORY_URL = os.getenv("HISTORY_URL", "http://localhost:8003")
MONOLITH_URL = os.getenv("MONOLITH_URL", "http://localhost:8000")

# When set and pointing at an existing directory, the gateway serves the
# built frontend as static files at "/". Normal local dev leaves this unset
# and runs the frontend separately via Vite.
STATIC_DIR = os.getenv("STATIC_DIR") or None

REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "5.0"))
