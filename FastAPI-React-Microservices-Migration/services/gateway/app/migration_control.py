"""Real Azure Container Apps deployment, triggered from the browser.

This shells out to azure/scripts/deploy.sh - the same script documented in
azure/README.md for manual use - and streams its output back to the
frontend so the "Migrate to Azure" button in the UI can show a live
console instead of a silent multi-minute wait.

Safety note: this only ever succeeds where the gateway PROCESS has a
working `az` CLI login available to it. When you run the gateway locally
(`make run-local`), that's whatever Azure account you're logged into on
your own machine. The gateway's own Docker image (and therefore the
already-migrated copy running on Azure Container Apps) has no `az` CLI and
no Azure credentials baked in at all, so this endpoint fails cleanly with
"Azure CLI not found" there - nobody else's credentials are ever at risk,
and clicking this button on someone else's deployed copy can't spend
someone else's money.

That alone isn't sufficient access control though - a bare, unauthenticated
HTTP endpoint that can trigger a real billable deployment is a genuine risk
if this gateway is ever reachable by anything other than you on your own
machine (a LAN, a VPN, an accidentally forwarded port). So every request to
these endpoints (except the token bootstrap endpoint itself) must:
  1. originate from 127.0.0.1/::1 (rejected otherwise), AND
  2. carry the X-Migrate-Token header matching MIGRATE_TOKEN below, which is
     generated fresh in memory each time the gateway process starts and is
     never written to disk or logged - the frontend fetches it once (itself
     gated by the same localhost-only check) and attaches it to every
     subsequent call. This also closes a CSRF gap: a malicious page open in
     another tab could still blindly POST to localhost, but it can't read
     the token endpoint's response (blocked by the browser's same-origin
     policy) to learn the token, so it can't produce a request the gateway
     will accept.

There's also an explicit confirmation step in the browser UI before this is
ever triggered, since it's a real, billable action regardless.
"""

from __future__ import annotations

import re
import secrets
import shutil
import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path

def _find_repo_root() -> Path:
    """Locate the repo root by walking up looking for azure/scripts/deploy.sh.

    In local dev this file lives at services/gateway/app/migration_control.py,
    3 levels below the repo root - a fixed `parents[N]` index would work
    there. But the gateway's OWN Docker image (services/gateway/Dockerfile)
    only copies services/common and services/gateway/app in, flattened to
    /app/app/migration_control.py - there is no azure/ directory and no `az`
    CLI at all in that image, by design (see module docstring). A hardcoded
    parents[N] index computed for the local case previously raised a bare
    IndexError at MODULE IMPORT TIME in that shallower container filesystem,
    which crashed the entire gateway app before it could ever reach the
    "az not available" checks below - a real bug caught the hard way during
    this project's first real Azure deployment. Walking up defensively and
    falling back to a sentinel that simply won't exist (which the
    availability checks already handle) fixes this in both environments.
    """
    here = Path(__file__).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "azure" / "scripts" / "deploy.sh").is_file():
            return candidate
    return here  # sentinel - DEPLOY_SCRIPT below won't exist; checks handle it gracefully


REPO_ROOT = _find_repo_root()
DEPLOY_SCRIPT = REPO_ROOT / "azure" / "scripts" / "deploy.sh"

_GATEWAY_URL_RE = re.compile(r"^GATEWAY_URL_MACHINE=(\S+)$")

# Regenerated every process start, kept in memory only.
MIGRATE_TOKEN = secrets.token_urlsafe(24)

LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost"}


def is_local_request(client_host: str | None) -> bool:
    return client_host in LOCAL_HOSTS


@dataclass
class MigrationState:
    status: str = "idle"  # idle | running | success | failed
    lines: list[str] = field(default_factory=list)
    gateway_url: str | None = None
    error: str | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def reset_for_new_run(self) -> None:
        with self._lock:
            self.status = "running"
            self.lines = []
            self.gateway_url = None
            self.error = None

    def append_line(self, line: str) -> None:
        with self._lock:
            self.lines.append(line)
            match = _GATEWAY_URL_RE.match(line.strip())
            if match:
                self.gateway_url = match.group(1)

    def finish(self, status: str, error: str | None = None) -> None:
        with self._lock:
            self.status = status
            self.error = error

    def snapshot(self, since: int = 0) -> dict:
        with self._lock:
            return {
                "status": self.status,
                "lines": list(self.lines[since:]),
                "total_lines": len(self.lines),
                "gateway_url": self.gateway_url,
                "error": self.error,
            }


state = MigrationState()


def check_azure_cli() -> dict:
    """Quick synchronous check: is `az` installed, is someone logged in, and
    does deploy.sh actually exist where we expect it (always false in the
    gateway's own deployed container, by design - see module docstring)?
    """
    if not DEPLOY_SCRIPT.is_file():
        return {
            "available": False,
            "message": "deploy.sh not found - this only works when running the gateway "
            "locally from a full checkout of the repo, not in a deployed container.",
        }
    az_path = shutil.which("az")
    if not az_path:
        return {
            "available": False,
            "message": "Azure CLI ('az') not found on this machine's PATH. Install it, "
            "then run `az login`, to enable real deployment.",
        }
    try:
        result = subprocess.run(
            ["az", "account", "show", "--query", "name", "-o", "tsv"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.TimeoutExpired, OSError):
        return {"available": False, "message": "Could not reach the Azure CLI. Try again."}

    if result.returncode != 0:
        return {
            "available": False,
            "message": "Not logged into Azure CLI. Run `az login` in your terminal, then try again.",
        }

    account_name = result.stdout.strip() or "your Azure account"
    return {"available": True, "message": f"Logged in as {account_name}."}


def _run_deploy_in_background() -> None:
    try:
        process = subprocess.Popen(
            ["bash", str(DEPLOY_SCRIPT)],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except OSError as exc:
        state.append_line(f"ERROR: could not start deploy script: {exc}")
        state.finish("failed", error=str(exc))
        return

    assert process.stdout is not None
    for line in iter(process.stdout.readline, ""):
        if not line:
            break
        state.append_line(line.rstrip())

    returncode = process.wait()
    if returncode == 0 and state.gateway_url:
        state.finish("success")
    else:
        state.finish("failed", error=f"deploy.sh exited with code {returncode}")


def start_deploy() -> dict:
    with state._lock:
        already_running = state.status == "running"
    if already_running:
        return {"started": False, "message": "A deployment is already in progress."}

    check = check_azure_cli()
    if not check["available"]:
        return {"started": False, "message": check["message"]}

    state.reset_for_new_run()
    thread = threading.Thread(target=_run_deploy_in_background, daemon=True)
    thread.start()
    return {"started": True, "message": "Deployment started."}
