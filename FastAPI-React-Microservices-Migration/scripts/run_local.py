#!/usr/bin/env python3
"""Run all microservices-lab services locally as plain uvicorn processes.

No Docker is used anywhere in local dev - each service is started directly
with ITS OWN venv interpreter (services/<name>/.venv, created by `make
install`). Each service's FastAPI app lives in a top-level package literally
named `app`, so running them all from one shared interpreter would only ever
work by accident of import order - a real bug this project hit once. A
per-service venv keeps every service's own `app` package genuinely isolated,
matching how they're actually deployed (one container each). Logs from every
subprocess are streamed to this process's stdout, each line prefixed with
`[service-name]`.

Usage:
    python3 scripts/run_local.py [--include-frontend]

Ctrl+C (SIGINT) or SIGTERM stops every child cleanly.
"""

from __future__ import annotations

import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DEV_PORT = 5173

# name -> (directory relative to repo root, port, extra env vars)
SERVICES: list[tuple[str, str, int, dict[str, str]]] = [
    ("sum-service", "services/sum-service", 8001, {}),
    ("mul-service", "services/mul-service", 8002, {}),
    ("monolith", "services/monolith", 8000, {}),
    ("history-service", "services/history-service", 8003, {}),
    (
        "gateway",
        "services/gateway",
        8080,
        {
            "SUM_URL": "http://localhost:8001",
            "MUL_URL": "http://localhost:8002",
            "HISTORY_URL": "http://localhost:8003",
            "MONOLITH_URL": "http://localhost:8000",
        },
    ),
]

processes: list[subprocess.Popen] = []
threads: list[threading.Thread] = []
_shutdown_lock = threading.Lock()
_shutting_down = False


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


_lsof_missing_warned = False


def _find_pids_on_port(port: int) -> list[int]:
    """Best-effort: ALL PIDs listening on `port` (macOS/Linux via lsof).

    Returns every match, not just the first - a port can in principle have
    more than one listening process (e.g. SO_REUSEPORT), and only cleaning
    up one of them would leave the port just as busy as before.
    """
    global _lsof_missing_warned
    try:
        result = subprocess.run(
            ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
            capture_output=True,
            text=True,
            timeout=3,
        )
    except FileNotFoundError:
        if not _lsof_missing_warned:
            _lsof_missing_warned = True
            print(
                "[run_local] NOTE: 'lsof' not found - automatic leftover-process cleanup is "
                "disabled. If a port is already in use, you'll need to find and stop it "
                "yourself.",
                flush=True,
            )
        return []
    except subprocess.TimeoutExpired:
        return []
    return [int(p) for p in result.stdout.split() if p.strip().isdigit()]


def _process_command(pid: int) -> str:
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip()


def _looks_like_our_process(command: str, port: int) -> bool:
    """Only ever auto-kill a process whose OWN command line clearly
    identifies it as one of THIS project's services (a previous run_local.py
    invocation, our uvicorn command for this exact port, or our frontend's
    vite dev server) - never blindly kill whatever happens to be on the
    port, since that could be something unrelated to this project entirely.
    """
    if "run_local.py" in command:
        return True
    if "uvicorn" in command and "app.main:app" in command and f"--port {port}" in command:
        return True
    if "vite" in command and str(REPO_ROOT / "frontend") in command:
        return True
    return False


def _kill_pid(pid: int, sig: int) -> bool:
    """Send a signal to a PID, tolerating every reason this can fail
    (already gone, not ours to signal, transient OS error) without ever
    crashing the script - a leftover-cleanup helper has to be robust to ALL
    of these, not just the common case.
    """
    try:
        os.kill(pid, sig)
        return True
    except ProcessLookupError:
        return True  # already gone - fine, that's the goal anyway
    except PermissionError:
        print(
            f"[run_local] WARNING: no permission to stop pid {pid} (owned by another user?) "
            "- leaving it alone.",
            flush=True,
        )
        return False
    except OSError as exc:
        print(f"[run_local] WARNING: could not signal pid {pid}: {exc}", flush=True)
        return False


def _cleanup_stale_processes(ports: list[tuple[str, int]]) -> None:
    """Find and stop leftover processes from a PRIOR run of this same stack
    still holding our ports, so a fresh `make run-local`/`make smoke`
    doesn't need a manual `kill` first - the exact situation this project
    hit for real (a `make run-local` left running in one terminal caused
    confusing bind errors, and a misleading smoke-test pass, in another).
    Skips (does not kill) anything that doesn't look like one of our own
    processes - see _looks_like_our_process. Handles every PID found on a
    port, not just the first, and every failure mode of actually killing
    one (already gone, not permitted, transient OS error).
    """
    for name, port in ports:
        pids = _find_pids_on_port(port)
        for pid in pids:
            command = _process_command(pid)
            if not _looks_like_our_process(command, port):
                continue  # not recognizably ours - leave it alone

            print(
                f"[run_local] found a leftover {name} process (pid {pid}) still on port {port} "
                "from a previous run - stopping it...",
                flush=True,
            )
            if not _kill_pid(pid, signal.SIGTERM):
                continue

        # Whether or not any of the above kills nominally "succeeded", verify
        # the actual port state rather than trusting the signal was enough -
        # a TERM'd process can take a moment to release its socket.
        if not pids:
            continue
        for _ in range(10):
            if not _port_in_use(port):
                break
            time.sleep(0.3)
        else:
            # Still busy after TERM + waiting - escalate to KILL for any of
            # our own PIDs that are still alive, then give it one more beat.
            for pid in pids:
                command = _process_command(pid)
                if command and _looks_like_our_process(command, port):
                    _kill_pid(pid, signal.SIGKILL)
            time.sleep(0.5)


def _check_ports_available(ports: list[tuple[str, int]]) -> None:
    """Fail fast with a clear message if any target port is STILL bound
    after _cleanup_stale_processes has already had a chance to clear our
    own leftover processes. If something is still on the port at this
    point, it's either not ours (so we correctly declined to kill it) or
    the cleanup didn't work - either way, a clear message beats the
    confusing "address already in use" bind errors buried in per-service
    logs, and beats a smoke test silently passing against the wrong
    (someone else's) process on that port.
    """
    busy = [(name, port) for name, port in ports if _port_in_use(port)]
    if not busy:
        return

    print("ERROR: the following ports are still in use after cleanup:", file=sys.stderr)
    for name, port in busy:
        print(f"  - {name}: port {port}", file=sys.stderr)
    print(
        "\nEither whatever's on this port doesn't look like one of this project's own "
        "processes (so it was deliberately left alone rather than killed automatically), or "
        "it IS ours but couldn't be stopped (see any WARNING above, e.g. a permission error). "
        f"Find and stop it yourself, e.g.: lsof -i :{busy[0][1]}",
        file=sys.stderr,
    )
    sys.exit(1)


_URL_RE = re.compile(r"https?://\S+")


def _linkify(line: str) -> str:
    """Wrap any URL in an OSC 8 terminal hyperlink escape sequence, so it's
    clickable in terminals that support it (iTerm2, VS Code, Terminal.app,
    Windows Terminal, ...). Terminals that don't support OSC 8 just ignore
    the escape codes and show the URL text as before - harmless either way.
    """

    def _wrap(match: re.Match) -> str:
        url = match.group(0)
        return f"\033]8;;{url}\033\\{url}\033]8;;\033\\"

    return _URL_RE.sub(_wrap, line)


def _stream_output(name: str, pipe) -> None:
    try:
        for line in iter(pipe.readline, ""):
            if not line:
                break
            print(f"[{name}] {_linkify(line.rstrip())}", flush=True)
    except ValueError:
        # pipe closed while reading, e.g. during shutdown
        pass


def _start_python_service(name: str, rel_dir: str, port: int, extra_env: dict[str, str]) -> subprocess.Popen:
    cwd = REPO_ROOT / rel_dir
    venv_python = cwd / ".venv" / "bin" / "python3"
    if not venv_python.exists():
        print(
            f"WARNING: {venv_python} not found; falling back to `{sys.executable}`. "
            f"Run `make install` to create services/{name}/.venv first.",
            flush=True,
        )
    python = str(venv_python) if venv_python.exists() else sys.executable
    env = os.environ.copy()
    env.update(extra_env)
    cmd = [python, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(port)]
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    return proc


def _start_frontend() -> subprocess.Popen | None:
    frontend_dir = REPO_ROOT / "frontend"
    node_modules = frontend_dir / "node_modules"
    if not node_modules.is_dir():
        print("[frontend] WARNING: frontend/node_modules not found, skipping frontend dev server "
              "(run `npm --prefix frontend install` first if you want it).", flush=True)
        return None
    proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    return proc


def _shutdown(*_args) -> None:
    global _shutting_down
    with _shutdown_lock:
        if _shutting_down:
            return
        _shutting_down = True

    print("\nShutting down all services...", flush=True)
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()

    for proc in processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    for t in threads:
        t.join(timeout=2)

    sys.exit(0)


def main() -> None:
    include_frontend = "--include-frontend" in sys.argv

    backend_targets = [(name, port) for name, _rel_dir, port, _env in SERVICES]
    # Frontend (Vite) already falls back to another port gracefully on its
    # own if 5173 is busy, so it's included in the cleanup attempt (nice to
    # land on the expected port) but NOT in the hard-fail check below.
    cleanup_targets = backend_targets + [("frontend", FRONTEND_DEV_PORT)]

    _cleanup_stale_processes(cleanup_targets)
    _check_ports_available(backend_targets)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    for name, rel_dir, port, extra_env in SERVICES:
        print(f"[run_local] starting {name} on port {port}...", flush=True)
        proc = _start_python_service(name, rel_dir, port, extra_env)
        processes.append(proc)
        t = threading.Thread(target=_stream_output, args=(name, proc.stdout), daemon=True)
        t.start()
        threads.append(t)

    if include_frontend or (REPO_ROOT / "frontend" / "node_modules").is_dir():
        proc = _start_frontend()
        if proc is not None:
            print("[run_local] starting frontend (npm run dev)...", flush=True)
            processes.append(proc)
            t = threading.Thread(target=_stream_output, args=("frontend", proc.stdout), daemon=True)
            t.start()
            threads.append(t)

    print("[run_local] all services started. Press Ctrl+C to stop.", flush=True)

    # Wait until a child exits unexpectedly or we get a shutdown signal.
    try:
        while True:
            for proc in processes:
                ret = proc.poll()
                if ret is not None:
                    print(f"[run_local] a service exited unexpectedly (code {ret}), shutting down.", flush=True)
                    _shutdown()
                    return
            signal.pause() if hasattr(signal, "pause") else None
            # signal.pause() blocks until a signal arrives; on platforms
            # without it (unlikely here) we'd spin, but macOS/Linux have it.
    except KeyboardInterrupt:
        _shutdown()


if __name__ == "__main__":
    main()
