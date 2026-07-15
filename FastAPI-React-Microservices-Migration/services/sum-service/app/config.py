"""Environment-driven configuration for sum-service."""

import os

HOST = os.getenv("SUM_HOST", "0.0.0.0")
PORT = int(os.getenv("SUM_PORT", "8001"))
