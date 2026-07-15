#!/usr/bin/env bash
# Tears down the microservices-lab Azure Container Apps deployment by
# deleting the entire resource group.
#
# Default is BLOCKING (no --no-wait): for a teardown script, the default
# should give clear confirmation that everything is actually gone before
# the user walks away. This can take several minutes for a resource group
# containing a Container Apps Environment - that's normal Azure
# deprovisioning time (the managed environment's underlying infrastructure
# takes a while to tear down), not something a "force delete" flag can
# skip - unlike soft-deletable resources (Key Vault, etc.), Container Apps
# Environments have no purge operation that bypasses real cleanup.
#
# Set AZURE_TEARDOWN_NO_WAIT=1 to return immediately instead (the deletion
# still runs to completion in Azure, you just won't see the confirmation
# here) - check `make azure-verify` yourself once you expect it's done.

set -euo pipefail

AZURE_RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-rg-microservices-lab}"
AZURE_TEARDOWN_NO_WAIT="${AZURE_TEARDOWN_NO_WAIT:-0}"

echo "===== microservices-lab: Azure teardown ====="
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

if ! az group show --name "$AZURE_RESOURCE_GROUP" >/dev/null 2>&1; then
    echo "Resource group '$AZURE_RESOURCE_GROUP' does not exist - nothing to tear down."
    exit 0
fi

if [ "$AZURE_TEARDOWN_NO_WAIT" = "1" ]; then
    echo "Deleting resource group '$AZURE_RESOURCE_GROUP' (--no-wait: returning immediately, deletion continues in the background)..."
    az group delete --name "$AZURE_RESOURCE_GROUP" --yes --no-wait
    echo ""
    echo "===== Teardown initiated ====="
    echo "Deletion of '$AZURE_RESOURCE_GROUP' is running in the background in Azure."
    echo "Run 'make azure-verify' in a few minutes to confirm it has finished."
    exit 0
fi

echo "Deleting resource group '$AZURE_RESOURCE_GROUP' (this blocks until deletion completes; can take several minutes)..."
echo "(Set AZURE_TEARDOWN_NO_WAIT=1 to return immediately instead and verify later.)"
az group delete --name "$AZURE_RESOURCE_GROUP" --yes

echo ""
echo "===== Teardown complete ====="
echo "Resource group '$AZURE_RESOURCE_GROUP' and everything in it has been deleted."
echo "Run 'make azure-verify' to double-check nothing remains."
