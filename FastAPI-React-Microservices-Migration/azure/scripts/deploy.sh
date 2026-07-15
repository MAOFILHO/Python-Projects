#!/usr/bin/env bash
# Deploys microservices-lab to Azure Container Apps.
#
# Two-phase approach (chosen for simplicity/reliability over a
# skipContainerApps-style conditional-deployment parameter):
#
#   Phase A: deploy azure/main.bicep with useRealImages=false. Every
#   Container App runs a public placeholder image
#   (mcr.microsoft.com/k8se/quickstart:latest), so this phase succeeds
#   even though no real image exists in the ACR yet - the ACR itself is
#   created in this same phase.
#
#   Phase B: `az acr build` the 5 real images into the now-existing ACR
#   (build happens in Azure - no local Docker involved), then re-run the
#   SAME bicep deployment with useRealImages=true so every Container App
#   is updated in place to point at its real image.
#
# This avoids maintaining two separate bicep files / modules and avoids
# any ordering trickery - it's just "deploy scaffolding, build images,
# deploy again with the real images switched on".
#
# No local Docker is used anywhere in this script.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

AZURE_RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-rg-microservices-lab}"
AZURE_LOCATION="${AZURE_LOCATION:-eastus}"
AZURE_PROJECT_NAME="${AZURE_PROJECT_NAME:-ms-lab}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
STATE_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.deploy-state"

DEPLOYMENT_NAME="microservices-lab-$(date +%Y%m%d%H%M%S)"

echo "===== microservices-lab: Azure Container Apps deploy ====="
echo "Resource group : $AZURE_RESOURCE_GROUP"
echo "Location       : $AZURE_LOCATION"
echo "Project name   : $AZURE_PROJECT_NAME (requested - may be auto-incremented below)"
echo ""

# --- 1. az CLI present + logged in ---
if ! command -v az >/dev/null 2>&1; then
    echo "ERROR: Azure CLI ('az') not found on PATH. Install it first: https://learn.microsoft.com/cli/azure/install-azure-cli" >&2
    exit 1
fi

if ! az account show >/dev/null 2>&1; then
    echo "ERROR: Not logged in to Azure CLI. Run 'az login' first, then re-run this script." >&2
    exit 1
fi

ACCOUNT_NAME="$(az account show --query name -o tsv)"
echo "Logged in to Azure account: $ACCOUNT_NAME"
echo ""

# --- 2. ensure containerapp extension is available (idempotent) ---
az extension add --name containerapp --upgrade --only-show-errors >/dev/null 2>&1 || true

# --- 3. create resource group if it doesn't exist ---
if az group show --name "$AZURE_RESOURCE_GROUP" >/dev/null 2>&1; then
    echo "Resource group '$AZURE_RESOURCE_GROUP' already exists, reusing it."
else
    echo "Creating resource group '$AZURE_RESOURCE_GROUP' in '$AZURE_LOCATION'..."
    az group create --name "$AZURE_RESOURCE_GROUP" --location "$AZURE_LOCATION" --output none
fi
echo ""

# --- 3b. resolve a collision-free project name ---
#
# All resource names in main.bicep derive from projectName. Two of them can
# genuinely collide on a redeploy into the SAME resource group after a prior
# teardown:
#
#   - Log Analytics Workspace (<project>-logs): Azure soft-deletes these for
#     up to 14 days after deletion, during which the name stays RESERVED in
#     this resource group/region - a plain redeploy right after a teardown
#     can hit this for real, not hypothetically.
#   - Azure Container Registry: names are globally unique across ALL of
#     Azure (not just this subscription), and since our ACR name is derived
#     deterministically from projectName + a hash of the resource group's
#     own (also deterministic, name-based) ID, redeploying into a
#     recreated resource group with the same name reproduces the exact same
#     ACR name every time - occasionally hitting a brief propagation delay
#     before Azure fully releases a just-deleted name.
#
# Neither has a "force delete"/purge that skips this - see the note in
# azure/scripts/teardown.sh. Instead, detect a collision here and try
# "<name>-2", "<name>-3", ... automatically, same spirit as how a filesystem
# avoids overwriting an existing file.
resolve_project_name() {
    local base="$1" candidate="$1" attempt=1

    while true; do
        local reason=""

        if az monitor log-analytics workspace show \
            --resource-group "$AZURE_RESOURCE_GROUP" \
            --workspace-name "${candidate}-logs" >/dev/null 2>&1; then
            reason="Log Analytics workspace '${candidate}-logs' already exists"
        fi

        # Soft-deleted workspaces reserve the name too. This subcommand is
        # only on newer az CLI versions - if it's missing, skip this check
        # rather than failing the whole deploy (the active-workspace check
        # above still catches the common case).
        if [ -z "$reason" ] && az monitor log-analytics workspace list-deleted-workspaces \
            --resource-group "$AZURE_RESOURCE_GROUP" -o tsv \
            --query "[?name=='${candidate}-logs'].name" 2>/dev/null | grep -q .; then
            reason="Log Analytics workspace '${candidate}-logs' is soft-deleted (Azure reserves the name for up to 14 days)"
        fi

        if [ -z "$reason" ]; then
            echo "$candidate"
            return 0
        fi

        attempt=$((attempt + 1))
        echo "NOTE: $reason - trying '${base}-${attempt}' instead..." >&2
        candidate="${base}-${attempt}"

        if [ "$attempt" -gt 20 ]; then
            echo "ERROR: could not find a collision-free project name after 20 attempts (base: '$base')." >&2
            echo "       Recover or purge the soft-deleted workspace(s) yourself, or set AZURE_PROJECT_NAME explicitly." >&2
            exit 1
        fi
    done
}

RESOLVED_PROJECT_NAME="$(resolve_project_name "$AZURE_PROJECT_NAME")"
if [ "$RESOLVED_PROJECT_NAME" != "$AZURE_PROJECT_NAME" ]; then
    echo "Project name '$AZURE_PROJECT_NAME' was unavailable - using '$RESOLVED_PROJECT_NAME' instead."
fi
AZURE_PROJECT_NAME="$RESOLVED_PROJECT_NAME"
echo "Using project name: $AZURE_PROJECT_NAME"
echo ""

# Persist what we actually used so other scripts (smoke_azure.sh) can pick
# it up automatically instead of needing it typed in again by hand.
cat > "$STATE_FILE" <<EOF
AZURE_RESOURCE_GROUP=$AZURE_RESOURCE_GROUP
AZURE_PROJECT_NAME=$AZURE_PROJECT_NAME
AZURE_LOCATION=$AZURE_LOCATION
EOF

# --- 4. Phase A: deploy scaffolding + placeholder-image container apps ---
echo "--- Phase A: deploying ACR, Log Analytics, Container Apps Environment, and placeholder Container Apps ---"
az deployment group create \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --name "${DEPLOYMENT_NAME}-phaseA" \
    --template-file "$REPO_ROOT/azure/main.bicep" \
    --parameters location="$AZURE_LOCATION" projectName="$AZURE_PROJECT_NAME" imageTag="$IMAGE_TAG" useRealImages=false \
    --output none

ACR_NAME="$(az deployment group show \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --name "${DEPLOYMENT_NAME}-phaseA" \
    --query properties.outputs.acrName.value -o tsv)"

echo "ACR provisioned: $ACR_NAME"
echo ""

# --- 5. Phase B: build the 5 real images in Azure (az acr build, no local Docker) ---
# Build context is the repo root for every service, matching the
# "Build context assumption" comment at the top of each Dockerfile.
# Gateway is built last since its Dockerfile needs frontend/ (already present).
echo "--- Phase B: building service images in ACR (az acr build - no local Docker) ---"

SERVICES="sum-service mul-service monolith history-service gateway"

for svc in $SERVICES; do
    echo ""
    echo ">>> Building $svc..."
    az acr build \
        --registry "$ACR_NAME" \
        --image "${svc}:${IMAGE_TAG}" \
        --file "services/${svc}/Dockerfile" \
        "$REPO_ROOT"
done

echo ""
echo "All 5 images built."
echo ""

# --- 6. re-deploy pointing the Container Apps at the real images ---
echo "--- Phase B (cont'd): updating Container Apps to use the freshly-built images ---"
az deployment group create \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --name "${DEPLOYMENT_NAME}-phaseB" \
    --template-file "$REPO_ROOT/azure/main.bicep" \
    --parameters location="$AZURE_LOCATION" projectName="$AZURE_PROJECT_NAME" imageTag="$IMAGE_TAG" useRealImages=true \
    --output none

GATEWAY_URL="$(az deployment group show \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --name "${DEPLOYMENT_NAME}-phaseB" \
    --query properties.outputs.gatewayUrl.value -o tsv)"

echo ""
echo "===== Deploy complete ====="
echo "Your app is live at ${GATEWAY_URL}"
# Machine-parseable marker line for tooling (e.g. the gateway's
# /api/migrate/azure endpoints) that needs to reliably extract the final
# URL from streamed log output without regexing free-form text.
echo "GATEWAY_URL_MACHINE=${GATEWAY_URL}"
echo ""
echo "Note: sum-service/mul-service/monolith/history-service/gateway all"
echo "default to minReplicas=0 (scale-to-zero), so the first request after"
echo "idle may take a few seconds (cold start) while the container starts."
echo ""
echo "Run 'make azure-teardown' when you're done to avoid ongoing ACR cost."
