#!/usr/bin/env bash
# End-to-end smoke test against a LIVE Azure Container Apps deployment of
# the gateway (adapted from scripts/smoke_local.sh, same PASS/FAIL
# checklist style, but hitting the deployed gateway's public FQDN over
# HTTPS instead of localhost, and skipping the "start local services"
# step entirely).
#
# Gateway URL resolution order:
#   1. $GATEWAY_URL env var, if set (e.g. GATEWAY_URL=https://foo.example.com)
#   2. otherwise, queried live via `az containerapp show` for the gateway app
#
# AZURE_RESOURCE_GROUP / AZURE_PROJECT_NAME resolution order:
#   1. explicit env var, if set
#   2. azure/.deploy-state, written by deploy.sh with whatever names it
#      actually used (deploy.sh may auto-increment AZURE_PROJECT_NAME on a
#      naming collision - see its "resolve_project_name" step - so this
#      avoids needing to type the resolved name in here by hand)
#   3. the same hardcoded defaults deploy.sh falls back to
#
# NOTE: deliberately avoids bash 4+ features (associative arrays, etc.)
# since macOS ships bash 3.2 by default.

set -u

STATE_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.deploy-state"
STATE_RESOURCE_GROUP=""
STATE_PROJECT_NAME=""
if [ -f "$STATE_FILE" ]; then
    STATE_RESOURCE_GROUP="$(grep '^AZURE_RESOURCE_GROUP=' "$STATE_FILE" | cut -d= -f2-)"
    STATE_PROJECT_NAME="$(grep '^AZURE_PROJECT_NAME=' "$STATE_FILE" | cut -d= -f2-)"
fi

# Explicit env var wins over the state file, which wins over the hardcoded default.
AZURE_RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-${STATE_RESOURCE_GROUP:-rg-microservices-lab}}"
AZURE_PROJECT_NAME="${AZURE_PROJECT_NAME:-${STATE_PROJECT_NAME:-ms-lab}}"
GATEWAY_APP_NAME="${AZURE_PROJECT_NAME}-gateway"

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

print_summary_and_exit() {
    echo ""
    echo "===== Azure Smoke Test Summary ====="
    for line in "${RESULT_LINES[@]}"; do
        echo "$line"
    done
    echo "====================================="
    echo "$CHECKS_PASSED passed, $CHECKS_FAILED failed"
    exit $OVERALL_FAIL
}

# --- 1. resolve gateway URL ---
if [ -n "${GATEWAY_URL:-}" ]; then
    echo "Using GATEWAY_URL from environment: $GATEWAY_URL"
else
    echo "GATEWAY_URL not set - querying Azure for the gateway's FQDN..."
    if ! command -v az >/dev/null 2>&1; then
        echo "ERROR: Azure CLI ('az') not found on PATH, and GATEWAY_URL was not set." >&2
        exit 1
    fi
    if ! az account show >/dev/null 2>&1; then
        echo "ERROR: Not logged in to Azure CLI (and GATEWAY_URL was not set). Run 'az login' first." >&2
        exit 1
    fi
    FQDN="$(az containerapp show \
        --name "$GATEWAY_APP_NAME" \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --query properties.configuration.ingress.fqdn -o tsv 2>/dev/null)"
    if [ -z "$FQDN" ]; then
        echo "ERROR: Could not resolve the gateway FQDN via 'az containerapp show' (app '$GATEWAY_APP_NAME' in resource group '$AZURE_RESOURCE_GROUP'). Set GATEWAY_URL explicitly." >&2
        exit 1
    fi
    GATEWAY_URL="https://${FQDN}"
fi
echo "Target: $GATEWAY_URL"
echo ""

# --- helper: extract a field from JSON via python3 ---
PYTHON_BIN="python3"
json_get() {
    # json_get <json_string> <python expression using `d`>
    "$PYTHON_BIN" -c "
import json, sys
d = json.loads(sys.argv[1])
print(eval(sys.argv[2]))
" "$1" "$2"
}

# --- 2. gateway health (allow extra time - possible cold start from scale-to-zero) ---
echo "Checking gateway health (allowing up to 60s for a cold start)..."
TIMEOUT=60
DEADLINE=$((SECONDS + TIMEOUT))
HEALTHY=0
while [ "$SECONDS" -lt "$DEADLINE" ]; do
    if curl -fsS -o /dev/null -m 5 "${GATEWAY_URL}/api/health"; then
        HEALTHY=1
        break
    fi
    sleep 2
done

if [ "$HEALTHY" -eq 1 ]; then
    record PASS "gateway became healthy (within ${TIMEOUT}s, cold start included)"
else
    record FAIL "gateway did not become healthy within ${TIMEOUT}s"
    print_summary_and_exit
fi

# --- 3. sum, microservices mode ---
RESP="$(curl -fsS -m 15 -X POST "${GATEWAY_URL}/api/operations/sum" \
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

# --- 4. sum, monolith mode ---
RESP="$(curl -fsS -m 15 -X POST "${GATEWAY_URL}/api/operations/sum" \
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

# --- 5. mul ---
RESP="$(curl -fsS -m 15 -X POST "${GATEWAY_URL}/api/operations/mul" \
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

# --- 6. history list ---
RESP="$(curl -fsS -m 15 "${GATEWAY_URL}/api/history?limit=5")"
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

# --- 7. history stats ---
RESP="$(curl -fsS -m 15 "${GATEWAY_URL}/api/history/stats")"
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

print_summary_and_exit
