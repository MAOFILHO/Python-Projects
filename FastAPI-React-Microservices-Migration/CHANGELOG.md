# Changelog

## [Unreleased]

### Added
- **`make install` now also upgrades the `az` CLI's bundled Bicep tooling** (`az bicep
  upgrade`, falling back to `az bicep install` if none is present yet), so the
  "A new Bicep release is available" warning during `make azure-deploy` doesn't linger.
  Silently skipped if `az` isn't installed at all, since Azure is optional for this project.
- **README now documents what to expect from the in-app "Deploy to Azure" button**: the
  disabled/running button state, the live streamed console, that it can take several minutes
  (Phase A infra + Phase B image builds), and that success is signaled unambiguously by the
  gateway URL auto-opening in a new tab (vs. an error banner on failure).
- **`scripts/run_local.py` now prints clickable URLs.** Any `http(s)://` URL in a child
  process's output (e.g. Vite's `Local: http://localhost:5173/`) is wrapped in an OSC 8
  terminal hyperlink escape sequence, so it's Cmd/Ctrl-clickable in terminals that support it
  (iTerm2, VS Code, Terminal.app, Windows Terminal); terminals that don't support OSC 8 just
  show the plain URL as before.
- **`scripts/run_local.py` now self-heals from leftover processes.** Running `make run-local` or
  `make smoke` while a previous instance is still bound to the same ports used to produce
  confusing "address already in use" errors — and worse, `make smoke`'s health checks could
  silently pass against the *other*, unrelated running instance instead of the one it just tried
  to start, masking the real problem. It now finds and stops leftover processes from a prior run
  of this same stack automatically (verified by checking each process's own command line — never
  killing something just because it happens to be on the port), retries, then fails with one
  clear, actionable message if a port is still busy afterward. Handles multiple PIDs per port,
  permission errors, and a missing `lsof` gracefully. Verified against a real reproduction of the
  exact scenario before/after the fix, not just written and assumed correct.
- **Migration page** (`/migration`, now the app's primary landing flow): an interactive
  Strangler Fig cutover simulator that stages traffic from 0% to 100% microservices, narrating
  every stage transition and individual routed request in a live console. Includes a
  "Start Migration to Microservices" auto-pilot that runs all stages end-to-end, and a
  completion banner linking straight to Compare Performance.
- **Real Azure Container Apps deployment trigger**, launched from the Migration page: a
  "Deploy to Azure (real)" button that runs the existing `azure/scripts/deploy.sh` and streams
  its live output into the browser, opening the deployed gateway's public URL in a new tab on
  success. Protected by a localhost-only source-IP check plus a random in-memory token
  (`services/gateway/app/migration_control.py`) so it can't be triggered remotely or by anyone
  without their own `az` login on the machine running the gateway process.
- Split the architecture diagram into a proper before/after pair — `data/monolith.png` and
  `data/microservices.png` — instead of one merged topology diagram.
- `azure/scripts/teardown.sh`: opt-in `AZURE_TEARDOWN_NO_WAIT=1` to return immediately instead
  of blocking on the resource group deletion (deletion still runs to completion in Azure either
  way — there's no actual "force delete" for a Container Apps Environment, only whether you wait
  around for the confirmation or check `make azure-verify` yourself later).
- **Sidebar restructure**: reordered to OPERATIONS → FEATURES (renamed from ARCHITECTURE) →
  MIGRATION → LEARN, so the first thing a visitor sees is "Run Operation," the actionable entry
  point, rather than reference material. The Migration item is now labeled "Start Migration" to
  match the page's own primary call-to-action.
- **Consolidated the five separate Learn pages (plus Glossary) into one scrollable page**
  (`/learn`): "What Are Microservices?" renders first, followed by an in-page index that jumps
  down to the Strangler Fig pattern, service boundaries, observability, when-not-to-use, and
  glossary sections via anchors. Old routes (`/learn/what-are-microservices`,
  `/learn/strangler-fig`, etc., and `/glossary`) redirect into the matching anchor on the new
  page rather than 404ing.

### Fixed
- Real bug caught during the first real Azure deployment: `services/gateway/app/migration_control.py`
  computed its repo-root path with a hardcoded `Path(__file__).resolve().parents[4]`, which only
  happened to work in local dev by accident (the absolute path there has enough parent
  directories to not raise, even though the index was already off by one). Inside the deployed
  container, where the file lives at a much shallower `/app/app/migration_control.py`, this
  raised a bare `IndexError` **at module import time**, crash-looping the entire gateway before
  it could serve a single request. Fixed by walking up from the file looking for a marker
  (`azure/scripts/deploy.sh`) instead of assuming a fixed directory depth, with 2 new regression
  tests covering the shallow-filesystem case.
- Azure Bicep: the default `projectName` (`microservices-lab`, 18 chars) combined with the
  longest derived Container App suffix (`-history-service`, 16 chars) exceeded Azure's 32-char
  Container App name limit, failing Phase A preflight validation on the first real deploy
  attempt. Fixed by shortening the default to `ms-lab` and adding a Bicep `@maxLength(16)` guard.
- Azure Bicep: the ACR had `adminUserEnabled: false` (a deliberate, good security default) but
  no managed identity or `AcrPull` role assignment existed anywhere in the template to actually
  grant pull access — caught in review before it could fail Phase B. Fixed by adding a
  user-assigned managed identity scoped only to this ACR, attached to all 5 Container Apps.
- Learned the hard way that Azure Container Apps only creates a new revision when the image
  *string* changes, not when a mutable `:latest` tag's underlying digest changes — an
  `az containerapp update --image ...` with the same tag string was silently a no-op. Documented
  in `azure/README.md`; a real redeploy after rebuilding an image needs
  `--revision-suffix <new-value>` to force a fresh pull.
- Real bug: every backend service's FastAPI app lived in a top-level package literally named
  `app`; installed editable into one shared venv, only the last-installed service's `app` would
  resolve at import time for `pytest`, silently breaking sibling services' test suites. Fixed
  by giving each service its own venv (`services/<name>/.venv`, created by `make install`) —
  smaller and more correct than renaming packages, and consistent with the project's own
  "no shared runtime between services" principle.
- `.gitignore`'s blanket `data/` rule was accidentally excluding the committed architecture
  diagrams; narrowed to `services/*/data/` (the actual runtime SQLite directory).

## [0.1.0] - 2026-07-14

### Added
- Initial release: monolith vs. microservices teaching/portfolio app, rewritten from the
  ground up on FastAPI + Python 3.12 (the Flask/Python 3.8 predecessor is retired).
- Four backend services: `sum-service`, `mul-service`, `history-service` (SQLite via
  SQLModel), and a `gateway` (BFF) that orchestrates compute + history calls and builds a
  step-by-step request trace.
- Standalone `monolith` service preserving the original single-process design, enabling live
  latency/trace comparison against the microservices path.
- Distributed correlation id (`X-Request-ID`, uuid4) generated at the gateway and propagated
  to all downstream services; included in both the trace payload and history records.
- `services/common` shared package scoping only the trace/correlation-id/health schema
  contract — arithmetic logic is intentionally duplicated per service, not shared, to avoid
  the "Shared Libraries" anti-pattern.
- React + TypeScript frontend (Vite) with a Contoso-styled layout: Operations page (run
  sum/multiply in Monolith or Microservices mode with animated trace playback), Service
  Health page (live aggregated `/health` polling), Compare Performance page (historical
  latency stats, bar chart, sparklines, "run N trials" control), Recent History page, and five
  in-app Learn pages plus a glossary covering microservices fundamentals, the Strangler Fig
  migration pattern, service boundary anti-patterns, observability/resilience patterns, and
  when not to use microservices.
- `scripts/run_local.py`: plain-Python local orchestration (no Docker) launching all 5
  backend services plus the frontend dev server as subprocesses.
- 40+ pytest tests across all 5 backend services (unit, endpoint, mocked-downstream
  integration) plus a Vitest frontend smoke test, plus an 11-check end-to-end
  `scripts/smoke_local.sh` (`make smoke`) exercising the real running stack in both modes.
- Optional Azure Container Apps deployment path (`azure/`): Bicep template (ACR + Log
  Analytics + Container Apps Environment + 5 Container Apps, scale-to-zero by default),
  `az acr build`-based image builds (no local Docker), deploy/teardown/verify scripts, a
  cost estimate, and a pytest-based teardown-verification check.
- Architecture diagram generator (`diagram/generate_diagram.py`, via the `diagrams` package).

### Credits
- Architecture and arithmetic logic based on / inspired by
  [Senhaji-Rhazi-Hamza/kube-python-micro-services-example](https://github.com/Senhaji-Rhazi-Hamza/kube-python-micro-services-example)
  (MIT License).
