#!/usr/bin/env bash
# Verifies that the microservices-lab Azure Container Apps deployment has
# been fully torn down: the resource group no longer exists (and, as a
# belt-and-suspenders check, that no stray resources are left behind if
# it somehow still does). PASS/FAIL checklist style mirrors
# scripts/smoke_local.sh in the repo root.
#
# Exit 0 if clean, non-zero if anything remains.

set -u

AZURE_RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-rg-microservices-lab}"

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

echo "===== microservices-lab: verify Azure teardown ====="
echo "Resource group : $AZURE_RESOURCE_GROUP"
echo ""

if ! command -v az >/dev/null 2>&1; then
    echo "ERROR: Azure CLI ('az') not found on PATH." >&2
    exit 1
fi

if ! az account show >/dev/null 2>&1; then
    echo "ERROR: Not logged in to Azure CLI. Run 'az login' first, then re-run this script." >&2
    exit 1
fi

# --- 1. resource group should not exist ---
RG_EXISTS="$(az group exists --name "$AZURE_RESOURCE_GROUP")"
if [ "$RG_EXISTS" = "false" ]; then
    record PASS "resource group '$AZURE_RESOURCE_GROUP' does not exist"
else
    record FAIL "resource group '$AZURE_RESOURCE_GROUP' still exists"

    # --- 2. (only relevant if the group still exists) no leftover resources ---
    RESOURCE_COUNT="$(az resource list --resource-group "$AZURE_RESOURCE_GROUP" --query 'length(@)' -o tsv 2>/dev/null || echo "unknown")"
    if [ "$RESOURCE_COUNT" = "0" ]; then
        record PASS "resource group exists but is empty (0 resources) - deletion likely in progress"
    else
        record FAIL "resource group still contains $RESOURCE_COUNT resource(s)"
    fi
fi

echo ""
echo "===== Verify Teardown Summary ====="
for line in "${RESULT_LINES[@]}"; do
    echo "$line"
done
echo "===================================="
echo "$CHECKS_PASSED passed, $CHECKS_FAILED failed"

if [ "$OVERALL_FAIL" -eq 0 ]; then
    echo ""
    echo "PASS: teardown verified clean."
else
    echo ""
    echo "FAIL: resources remain. If deletion is still in progress, wait a few minutes and re-run this script."
fi

exit $OVERALL_FAIL
