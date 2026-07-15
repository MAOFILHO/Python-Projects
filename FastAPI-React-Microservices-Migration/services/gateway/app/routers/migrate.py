"""Triggers and reports on a REAL Azure Container Apps deployment.

Every endpoint here except /token requires BOTH a localhost-only source IP
AND the X-Migrate-Token header (see app/migration_control.py for the full
threat-model writeup). The frontend fetches the token once via /token
(itself localhost-gated) and attaches it to every subsequent call.

Design note on streaming: this uses polling (GET .../status?since=N)
rather than a persistent SSE/WebSocket connection - simpler, no
long-lived-connection edge cases through proxies, and consistent with how
the frontend already polls Service Health. The frontend polls every
~700ms while a deployment is running, which still reads as "live".
"""

from fastapi import APIRouter, Header, HTTPException, Request

from app import migration_control

router = APIRouter(prefix="/api/migrate/azure", tags=["migrate"])


def _require_local(request: Request) -> None:
    client_host = request.client.host if request.client else None
    if not migration_control.is_local_request(client_host):
        raise HTTPException(status_code=403, detail="This endpoint only accepts local requests.")


def _require_local_and_token(request: Request, x_migrate_token: str | None = Header(default=None)) -> None:
    _require_local(request)
    if x_migrate_token != migration_control.MIGRATE_TOKEN:
        raise HTTPException(status_code=403, detail="Missing or invalid X-Migrate-Token.")


@router.get("/token")
async def token(request: Request) -> dict:
    _require_local(request)
    return {"token": migration_control.MIGRATE_TOKEN}


@router.get("/check")
async def check(request: Request, x_migrate_token: str | None = Header(default=None)) -> dict:
    _require_local_and_token(request, x_migrate_token)
    return migration_control.check_azure_cli()


@router.post("/deploy")
async def deploy(request: Request, x_migrate_token: str | None = Header(default=None)) -> dict:
    _require_local_and_token(request, x_migrate_token)
    return migration_control.start_deploy()


@router.get("/status")
async def status(
    request: Request, x_migrate_token: str | None = Header(default=None), since: int = 0
) -> dict:
    _require_local_and_token(request, x_migrate_token)
    return migration_control.state.snapshot(since=since)
