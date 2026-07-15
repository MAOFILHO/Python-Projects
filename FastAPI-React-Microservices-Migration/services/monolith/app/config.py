"""Environment-driven configuration for the monolith."""

import os

HOST = os.getenv("MONOLITH_HOST", "0.0.0.0")
PORT = int(os.getenv("MONOLITH_PORT", "8000"))
