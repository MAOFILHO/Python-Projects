#!/usr/bin/env bash
# End-to-end smoke test against the real (non-mocked) local services.
#
# Starts every backend service via scripts/run_local.py, waits for health,
# exercises the gateway's operations/history endpoints, prints a PASS/FAIL
# checklist, and always tears down the background process on exit.
#
# NOTE: deliberately avoids bash 4+ features (associative arrays, etc.)
# since macOS ships bash 3.2 by default.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

RUN_LOCAL_PID=""
OVERALL_FAIL=0
CHECKS_PASSED=0
CHECKS_FAILED=0

RESULT_LINES=()

record() {
    # record <PASS|FAIL> <message>
    local status="$1"
    shift
    RESULT_LINES+=("$status: $*")
    if [ "$status" = "PASS" ]; then
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        OVERALL_FAIL=1
    fi
}

cleanup() {
    echo ""
    echo "Cleaning up background services..."
    if [ -n "$RUN_LOCAL_PID" ] && kill -0 "$RUN_LOCAL_PID" 2>/dev/null; then
        # SIGTERM the whole process group so uvicorn children die too.
        kill -TERM "-$RUN_LOCAL_PID" 2>/dev/null || kill -TERM "$RUN_LOCAL_PID" 2>/dev/null
        for _ in $(seq 1 10); do
            kill -0 "$RUN_LOCAL_PID" 2>/dev/null || break
            sleep 0.5
        done
        kill -0 "$RUN_LOCAL_PID" 2>/dev/null && kill -KILL "-$RUN_LOCAL_PID" 2>/dev/null
    fi

    echo ""
    echo "===== Smoke Test Summary ====="
    for line in "${RESULT_LINES[@]}"; do
        echo "$line"
    done
    echo "==============================="
    echo "$CHECKS_PASSED passed, $CHECKS_FAILED failed"

    exit $OVERALL_FAIL
}

trap cleanup EXIT INT TERM

# --- 1. prereqs ---
if ! "$REPO_ROOT/scripts/check_prereqs.sh"; then
    record FAIL "prerequisite check"
    exit 1
fi
record PASS "prerequisite check"

# --- 2. start services (own process group so we can kill uvicorn children too) ---
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

set -m  # enable job control so the background job gets its own pgid
"$PYTHON_BIN" "$REPO_ROOT/scripts/run_local.py" &
RUN_LOCAL_PID=$!
set +m

# run_local.py now fails fast (before spawning anything) if its target ports
# are already bound - e.g. another `make run-local`/`make smoke` still
# running in a different terminal. Give it a moment to hit that check and
# exit; if it already died, stop here with a clear reason instead of
# polling health endpoints, which could otherwise misleadingly "pass" by
# reaching that OTHER, unrelated instance instead of the one we just tried
# to start.
sleep 1
if ! kill -0 "$RUN_LOCAL_PID" 2>/dev/null; then
    record FAIL "run_local.py exited immediately - likely a port conflict with another running instance (see error above); stop it first, or check the /tmp or terminal output for the exact port"
    exit 1
fi

echo "Started run_local.py (pid $RUN_LOCAL_PID), waiting for services to become healthy..."

# --- 3. poll health endpoints ---
# name|url pairs (avoiding associative arrays for bash 3.2 compatibility)
HEALTH_TARGETS=(
    "sum-service|http://localhost:8001/health"
    "mul-service|http://localhost:8002/health"
    "monolith|http://localhost:8000/health"
    "history-service|http://localhost:8003/health"
    "gateway|http://localhost:8080/api/health"
)

TIMEOUT=30
DEADLINE=$((SECONDS + TIMEOUT))
UP_LIST=""

is_up() {
    # is_up <name> -> 0 if already recorded up
    case "|$UP_LIST|" in
        *"|$1|"*) return 0 ;;
        *) return 1 ;;
    esac
}

while [ "$SECONDS" -lt "$DEADLINE" ]; do
    all_up=1
    for target in "${HEALTH_TARGETS[@]}"; do
        name="${target%%|*}"
        url="${target#*|}"
        if is_up "$name"; then
            continue
        fi
        if curl -fsS -o /dev/null -m 2 "$url"; then
            UP_LIST="$UP_LIST|$name|"
        else
            all_up=0
        fi
    done
    if [ "$all_up" = "1" ]; then
        break
    fi
    sleep 1
done

for target in "${HEALTH_TARGETS[@]}"; do
    name="${target%%|*}"
    if is_up "$name"; then
        record PASS "$name became healthy"
    else
        record FAIL "$name did not become healthy within ${TIMEOUT}s"
    fi
done

if [ "$OVERALL_FAIL" -eq 1 ]; then
    echo "One or more services failed to start; aborting remaining checks."
    exit 1
fi

# --- helper: extract a field from JSON via python3 ---
json_get() {
    # json_get <json_string> <python expression using `d`>
    "$PYTHON_BIN" -c "
import json, sys
d = json.loads(sys.argv[1])
print(eval(sys.argv[2]))
" "$1" "$2"
}

# --- 4. sum, microservices mode ---
RESP="$(curl -fsS -m 5 -X POST http://localhost:8080/api/operations/sum \
    -H 'Content-Type: application/json' \
    -d '{"a":7,"b":5,"mode":"microservices"}')"
if [ -n "$RESP" ]; then
    HOPS="$(json_get "$RESP" 'len(d["trace"])' 2>/dev/null || echo 0)"
    RESULT="$(json_get "$RESP" 'd["result"]' 2>/dev/null || echo "")"
    if [ "$HOPS" -ge 2 ] 2>/dev/null && { [ "$RESULT" = "12.0" ] || [ "$RESULT" = "12" ]; }; then
        record PASS "sum (microservices mode): result=$RESULT, trace hops=$HOPS"
    else
        record FAIL "sum (microservices mode): unexpected response: $RESP"
    fi
else
    record FAIL "sum (microservices mode): no response from gateway"
fi

# --- 5. sum, monolith mode ---
RESP="$(curl -fsS -m 5 -X POST http://localhost:8080/api/operations/sum \
    -H 'Content-Type: application/json' \
    -d '{"a":7,"b":5,"mode":"monolith"}')"
if [ -n "$RESP" ]; then
    HOPS="$(json_get "$RESP" 'len(d["trace"])' 2>/dev/null || echo 0)"
    RESULT="$(json_get "$RESP" 'd["result"]' 2>/dev/null || echo "")"
    if [ "$HOPS" -ge 1 ] 2>/dev/null && { [ "$RESULT" = "12.0" ] || [ "$RESULT" = "12" ]; }; then
        record PASS "sum (monolith mode): result=$RESULT, trace hops=$HOPS"
    else
        record FAIL "sum (monolith mode): unexpected response: $RESP"
    fi
else
    record FAIL "sum (monolith mode): no response from gateway"
fi

# --- 6. mul ---
RESP="$(curl -fsS -m 5 -X POST http://localhost:8080/api/operations/mul \
    -H 'Content-Type: application/json' \
    -d '{"a":7,"b":5,"mode":"microservices"}')"
if [ -n "$RESP" ]; then
    RESULT="$(json_get "$RESP" 'd["result"]' 2>/dev/null || echo "")"
    if [ "$RESULT" = "35.0" ] || [ "$RESULT" = "35" ]; then
        record PASS "mul (microservices mode): result=$RESULT (expected 35)"
    else
        record FAIL "mul (microservices mode): unexpected response: $RESP"
    fi
else
    record FAIL "mul (microservices mode): no response from gateway"
fi

# --- 7. history list ---
RESP="$(curl -fsS -m 5 "http://localhost:8080/api/history?limit=5")"
if [ -n "$RESP" ]; then
    COUNT="$(json_get "$RESP" 'len(d["items"])' 2>/dev/null || echo 0)"
    if [ "$COUNT" -ge 1 ] 2>/dev/null; then
        record PASS "history list: $COUNT recent record(s) returned"
    else
        record FAIL "history list: expected records from earlier steps, got: $RESP"
    fi
else
    record FAIL "history list: no response from gateway"
fi

# --- 8. history stats ---
RESP="$(curl -fsS -m 5 "http://localhost:8080/api/history/stats")"
if [ -n "$RESP" ]; then
    HAS_BOTH="$($PYTHON_BIN -c "
import json, sys
d = json.loads(sys.argv[1])
modes = d.get('by_mode', {})
ok = 'monolith' in modes and 'microservices' in modes
ok = ok and modes['monolith']['count'] >= 1 and modes['microservices']['count'] >= 1
print('yes' if ok else 'no')
" "$RESP" 2>/dev/null || echo "no")"
    if [ "$HAS_BOTH" = "yes" ]; then
        record PASS "history stats: both monolith and microservices present with count >= 1"
    else
        record FAIL "history stats: unexpected response: $RESP"
    fi
else
    record FAIL "history stats: no response from gateway"
fi

exit $OVERALL_FAIL
