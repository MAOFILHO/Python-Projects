from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR
from app.routers import health, history, migrate, operations

app = FastAPI(title="Gateway")

app.include_router(operations.router)
app.include_router(health.router)
app.include_router(history.router)
app.include_router(migrate.router)

# In normal local dev STATIC_DIR is unset and the frontend runs separately
# via Vite. It's only set (e.g. in the Azure container image) once the
# frontend has been built into a directory the gateway can serve directly.
if STATIC_DIR:
    static_path = Path(STATIC_DIR)
    if static_path.is_dir():
        app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")
