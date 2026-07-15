# microservices-lab on Azure Container Apps

> **Optional — Not Required to Run This Project Locally**
>
> Everything under `azure/` is an optional deployment path. The project runs
> entirely locally with plain Python (see the root `README.md` and
> `scripts/run_local.py`) — no Azure account, credit card, or cloud resource
> is needed to develop, test, or demo this project on your own machine.
> Use this only if you specifically want a live, publicly-reachable URL.

This deploys the 5 backend services (`sum-service`, `mul-service`,
`monolith`, `history-service`, `gateway`) to **Azure Container Apps (ACA)**,
with the gateway also serving the built React frontend. Images are built
in Azure via `az acr build` (ACR Tasks) — **no local Docker is used at any
point.**

Not covered, and intentionally out of scope: Kubernetes/AKS (dropped
entirely — this project has no Kubernetes manifests anywhere), and Azure
Container Instances as a real target (ACI is mentioned only as a
"you could also..." aside below — it's not what's built or tested here).

## Cost Estimate

**These are estimates, not guaranteed pricing.** Azure prices change; check
the [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
for current numbers in your region/currency.

| Resource | Configuration | Estimated cost |
|---|---|---|
| Container Apps (x5) | 0.25 vCPU / 0.5Gi, `minReplicas: 0` | ACA's consumption plan includes a **monthly free grant** (roughly 180,000 vCPU-seconds, 360,000 GiB-seconds, and 2M requests, per the general ACA consumption pricing structure). An idle-most-of-the-time demo like this one, especially if torn down between demos, will likely land **close to $0/month** in compute. If left running continuously with `minReplicas: 1` on the gateway, expect low single-digit $/month for that one always-on app; the other 4 stay at zero cost while unused. |
| Azure Container Registry | Basic SKU | ~$0.167/day (~**$5/month flat fee**) while it exists — this is the main *fixed* cost, independent of usage. Delete the resource group (which deletes the ACR) between demos to avoid this. |
| Log Analytics Workspace | PerGB2018, 30-day retention | Minimal for this workload (a handful of lightweight services logging occasionally) — likely under $1/month, and Azure also has a small free daily ingestion allowance. Required plumbing for the Container Apps Environment; there's no way to run one without a log destination. |
| Container Apps Environment | — | No separate charge; you pay for the apps running in it (above). |

**Bottom line:** run a demo, then `make azure-teardown` — you'll mostly pay
for the hour(s) it was up, and the ACR's flat fee only accrues while the
resource group exists. Leaving it deployed indefinitely costs roughly
**~$5/month** (ACR) plus whatever compute/log usage you generate.

## Prerequisites

- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed
- Logged in: `az login` (this is the *only* credential needed — no API keys, no secrets, nothing hardcoded in this repo)
- An Azure subscription with permission to create resource groups and the resource types below

## Deploy

```bash
make azure-deploy
# or directly:
bash azure/scripts/deploy.sh
```

Optional overrides (env vars, all have sensible defaults — nothing is
hardcoded):

```bash
AZURE_RESOURCE_GROUP=rg-microservices-lab \
AZURE_LOCATION=eastus \
AZURE_PROJECT_NAME=ms-lab \
IMAGE_TAG=latest \
    make azure-deploy
```

`AZURE_PROJECT_NAME` must stay <= 16 characters (enforced by `main.bicep`'s `@maxLength(16)`):
Azure Container App names are capped at 32 characters, and the longest name this template
derives is `<project-name>-history-service` (a 16-character suffix).

What it does (see `azure/scripts/deploy.sh` for full detail):

1. Checks `az` is installed and you're logged in.
2. Creates the resource group if it doesn't already exist.
3. **Phase A**: deploys `azure/main.bicep` — this provisions the Azure
   Container Registry, Log Analytics Workspace, Container Apps
   Environment, and all 5 Container Apps. On this first pass the apps run
   a public placeholder image (`mcr.microsoft.com/k8se/quickstart:latest`)
   since no real image exists in the registry yet.
4. **Phase B**: runs `az acr build` for each of the 5 services (build
   happens in Azure, not locally), then re-deploys the same Bicep template
   with `useRealImages=true` so every Container App is updated in place to
   point at its real, freshly-built image.
5. Prints the gateway's public URL.

## Architecture on Azure

- **gateway**: the only app with **external** (public) ingress — this is
  your demo URL.
- **sum-service / mul-service / monolith / history-service**: **internal-only**
  ingress — reachable from the gateway via Container Apps' internal DNS
  (`https://<app-name>.internal.<environment-domain>`), not exposed to the
  internet at all.
- All 5 apps default to `minReplicas: 0` (scale-to-zero) for cost. See the
  cold-start note below.

## Cold start tradeoff

Every app, **including the gateway**, defaults to `minReplicas: 0`. This is
the most cost-conscious setting — you pay nothing for idle apps — but it
means the **first request after a period of inactivity has to wait for a
cold start** (pulling the image and booting the FastAPI process), typically
a few seconds for these small images.

If you're about to demo this live and don't want that first-request delay,
edit `azure/main.bicep` and flip the gateway's `scale.minReplicas` from `0`
to `1` (there's a commented-out `minReplicas: 1` line directly above the
active `minReplicas: 0` line in the gateway's Container App definition,
specifically for this purpose), then re-run `make azure-deploy`. This keeps
one gateway replica always warm at a small ongoing cost (see the cost table
above) while the 4 backend services stay scale-to-zero regardless, since
they're only hit on-demand.

## Redeploying after a code change

`make azure-deploy` always works (it re-runs `az acr build` and re-deploys the Bicep template),
but if you instead manually rebuild a single image with `az acr build` and then try to point the
running app at it with a plain `az containerapp update --image <acr>/<service>:latest`, **nothing
will happen** if the image string is unchanged from what's already configured — Azure Container
Apps only creates a new revision when the image *reference string* changes, not when a mutable
tag's underlying digest changes after a rebuild. Force a real redeploy with:

```bash
az containerapp update \
  --name <project-name>-<service> \
  --resource-group $AZURE_RESOURCE_GROUP \
  --image <acr-login-server>/<service>:latest \
  --revision-suffix <any-new-value>
```

The `--revision-suffix` is what actually forces a fresh pull and a new revision. This was hit
for real during this project's own first Azure deployment — see the
[Troubleshooting & Lessons Learned](../README.md#troubleshooting--lessons-learned) section in
the root README.

## Verify it's working

```bash
GATEWAY_URL=https://<your-gateway-fqdn> make smoke-azure
# or, if you're still logged in and know the resource group, omit
# GATEWAY_URL and it'll be looked up automatically via `az containerapp show`
make smoke-azure
```

This runs the same operation/health/history checks as the local
`scripts/smoke_local.sh`, against the live deployed URL instead of
localhost, with extra allowance for a possible cold start.

## Teardown

```bash
make azure-teardown
# or directly:
bash azure/scripts/teardown.sh
```

This deletes the entire resource group (`az group delete --name ... --yes`)
and **blocks until deletion completes** by default, so you get a clear
"it's actually gone" confirmation before walking away — this can take
several minutes, mostly waiting on the Container Apps Environment itself to
finish deprovisioning (the slowest resource in the group). There is no
"force delete" or purge option that skips this — unlike soft-deletable
resources such as Key Vault, Container Apps Environments have no purge
operation, so the wait is genuine Azure backend cleanup, not something a
flag can shortcut.

If you'd rather not wait, set `AZURE_TEARDOWN_NO_WAIT=1` to return
immediately (deletion still runs to completion in Azure — you just won't
see the confirmation here):

```bash
AZURE_TEARDOWN_NO_WAIT=1 make azure-teardown
# then, a few minutes later:
make azure-verify
```

## Verify teardown

```bash
make azure-verify
# or directly:
bash azure/scripts/verify_teardown.sh
```

Prints a PASS/FAIL checklist confirming the resource group (and everything
in it) is gone. There's also a pytest-based check for the same thing,
meant to be run manually after a teardown (it is *not* part of the normal
`make test` run, since it needs live Azure credentials):

```bash
AZURE_RESOURCE_GROUP=rg-microservices-lab \
    .venv/bin/pytest azure/tests/test_teardown_verification.py -v
```

It skips (rather than fails) if the Azure CLI isn't installed or you're not
logged in.

## Alternatives considered

- **AKS** — explicitly out of scope; overkill for a 5-service demo and this
  project has no Kubernetes manifests anywhere.
- **Azure Container Instances (ACI)** — a lighter-weight alternative worth
  knowing about if you just want to run one container without an
  orchestration layer at all, but it lacks ACA's built-in internal
  service-to-service DNS and scale-to-zero HTTP-triggered scaling that this
  project relies on for the gateway → backend calls, so it isn't what's
  built or tested here.

## Diagram regeneration

`diagram/generate_diagram.py` (repo root, not under `azure/`) generates
`data/monolith.png` and `data/microservices.png` (before/after topology). It's a
dev-only tool (`pip install diagrams` + system `graphviz`) and isn't part
of any service's runtime dependencies. Run `make diagram` to regenerate it.
