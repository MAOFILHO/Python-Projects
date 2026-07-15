"""Environment-driven configuration for mul-service."""

import os

HOST = os.getenv("MUL_HOST", "0.0.0.0")
PORT = int(os.getenv("MUL_PORT", "8002"))
