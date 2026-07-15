.PHONY: install run-local test smoke lint clean diagram azure-deploy azure-teardown azure-verify smoke-azure

# Root venv: services/common's own tests + dev tooling (ruff, diagram generation,
# the Azure teardown-verification pytest). Every OTHER service gets its OWN venv
# (services/<name>/.venv) rather than sharing one - each service's FastAPI app
# lives in a top-level package literally named `app`, so installing more than one
# of them editable into the SAME venv makes the last-installed one silently shadow
# the others at import time (a real bug this project hit and fixed). Runtime
# (uvicorn, launched with cwd=services/<name>) isn't affected by this - only a
# shared install/test environment is - but per-service venvs also match this
# project's own "independent deployability, no shared runtime" principle.
APP_SERVICES := sum-service mul-service monolith history-service gateway
VENV_PIP := .venv/bin/pip

install:
	@echo "Installing root dev tooling + services/common..."
	@$(VENV_PIP) install -e services/common || exit 1
	@$(VENV_PIP) install -e ".[dev]" || exit 1
	@for name in $(APP_SERVICES); do \
		echo "Installing $$name (own venv: services/$$name/.venv)..."; \
		python3.12 -m venv "services/$$name/.venv" || python3 -m venv "services/$$name/.venv" || exit 1; \
		"services/$$name/.venv/bin/pip" install --upgrade pip -q || exit 1; \
		"services/$$name/.venv/bin/pip" install -e services/common -e "services/$$name" pytest pytest-asyncio respx -q || exit 1; \
	done
	@if [ -d frontend ]; then \
		echo "Installing frontend dependencies..."; \
		npm --prefix frontend install; \
	fi
	@if command -v az >/dev/null 2>&1; then \
		echo "Upgrading az CLI's Bicep tooling (used by the optional Azure deploy)..."; \
		az bicep upgrade >/dev/null 2>&1 || az bicep install >/dev/null 2>&1 || true; \
	fi

run-local:
	@if [ -d frontend ]; then \
		python3 scripts/run_local.py --include-frontend; \
	else \
		python3 scripts/run_local.py; \
	fi

test:
	@echo "Testing common..."
	@.venv/bin/pytest services/common || exit 1
	@for name in $(APP_SERVICES); do \
		echo "Testing $$name..."; \
		"services/$$name/.venv/bin/pytest" "services/$$name" || exit 1; \
	done
	@if [ -d frontend ]; then \
		npm --prefix frontend test -- --run; \
	fi

smoke:
	@bash scripts/smoke_local.sh

lint:
	@if .venv/bin/ruff --version >/dev/null 2>&1; then \
		.venv/bin/ruff check services/; \
	else \
		echo "ruff not available, skipping lint"; \
	fi

clean:
	find . -type d -name '__pycache__' -not -path '*/.venv/*' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -not -path '*/.venv/*' -exec rm -rf {} + 2>/dev/null || true

diagram:
	@.venv/bin/python diagram/generate_diagram.py

# Azure targets added separately
azure-deploy:
	@bash azure/scripts/deploy.sh

azure-teardown:
	@bash azure/scripts/teardown.sh

azure-verify:
	@bash azure/scripts/verify_teardown.sh

smoke-azure:
	@bash azure/scripts/smoke_azure.sh
