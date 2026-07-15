#!/usr/bin/env bash
# Checks local dev prerequisites for microservices-lab.
# No Docker check on purpose - this project never uses local Docker.

set -u

FAILED=0

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; FAILED=1; }

# --- python3 >= 3.12 ---
if command -v python3 >/dev/null 2>&1; then
    PY_VERSION="$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null)"
    PY_MAJOR="$(echo "$PY_VERSION" | cut -d. -f1)"
    PY_MINOR="$(echo "$PY_VERSION" | cut -d. -f2)"
    if [ "$PY_MAJOR" -gt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 12 ]; }; then
        pass "python3 $PY_VERSION (>= 3.12 required)"
    else
        fail "python3 $PY_VERSION found, but >= 3.12 is required"
    fi
else
    fail "python3 not found on PATH"
fi

# --- node >= 18 ---
if command -v node >/dev/null 2>&1; then
    NODE_VERSION="$(node --version | sed 's/^v//')"
    NODE_MAJOR="$(echo "$NODE_VERSION" | cut -d. -f1)"
    if [ "$NODE_MAJOR" -ge 18 ]; then
        pass "node v$NODE_VERSION (>= 18 required)"
    else
        fail "node v$NODE_VERSION found, but >= 18 is required"
    fi
else
    fail "node not found on PATH"
fi

if [ "$FAILED" -ne 0 ]; then
    echo ""
    echo "One or more prerequisites are missing. Please install/upgrade and re-run."
    exit 1
fi

echo ""
echo "All prerequisites satisfied."
exit 0
