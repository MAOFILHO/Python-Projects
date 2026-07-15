from fastapi.testclient import TestClient

from app import migration_control
from app.main import app

client = TestClient(app)


def test_is_local_request_helper():
    assert migration_control.is_local_request("127.0.0.1") is True
    assert migration_control.is_local_request("::1") is True
    assert migration_control.is_local_request("localhost") is True
    assert migration_control.is_local_request("203.0.113.5") is False
    assert migration_control.is_local_request(None) is False


def test_all_endpoints_reject_non_local_requests():
    # TestClient's default client host is "testclient", not a local address,
    # so every endpoint here should reject it - this is the actual security
    # boundary working, not a test artifact to work around.
    assert client.get("/api/migrate/azure/token").status_code == 403
    assert client.get("/api/migrate/azure/check").status_code == 403
    assert client.post("/api/migrate/azure/deploy").status_code == 403
    assert client.get("/api/migrate/azure/status").status_code == 403


def test_deploy_requires_token_even_when_local(monkeypatch):
    monkeypatch.setattr(migration_control, "is_local_request", lambda host: True)

    resp = client.post("/api/migrate/azure/deploy")
    assert resp.status_code == 403

    resp = client.post(
        "/api/migrate/azure/deploy",
        headers={"X-Migrate-Token": "wrong-token"},
    )
    assert resp.status_code == 403


def test_find_repo_root_does_not_crash_on_shallow_container_filesystem(monkeypatch):
    # Regression test for a real bug hit deploying to Azure: a hardcoded
    # `parents[N]` index raised a bare IndexError at MODULE IMPORT TIME
    # inside the gateway's own Docker image, where this file lives at a much
    # shallower path (/app/app/migration_control.py) than in local dev
    # (services/gateway/app/migration_control.py) - crashing the whole
    # gateway before it could ever start serving. Simulate that shallow
    # path here and confirm _find_repo_root() degrades gracefully instead.
    monkeypatch.setattr(migration_control, "__file__", "/app/app/migration_control.py")
    result = migration_control._find_repo_root()
    assert isinstance(result, migration_control.Path)
    # No azure/scripts/deploy.sh exists anywhere above this synthetic path,
    # so the derived DEPLOY_SCRIPT must not exist - check_azure_cli() relies
    # on exactly this to report "unavailable" instead of crashing.
    assert not (result / "azure" / "scripts" / "deploy.sh").is_file()


def test_check_azure_cli_reports_unavailable_when_deploy_script_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(migration_control, "DEPLOY_SCRIPT", tmp_path / "does-not-exist.sh")
    result = migration_control.check_azure_cli()
    assert result["available"] is False
    assert "deploy.sh not found" in result["message"]


def test_deploy_with_correct_token_and_local_reaches_the_handler(monkeypatch):
    # Never let this test exercise the real `az` CLI or spawn deploy.sh -
    # whatever machine runs this suite might have a live `az login` session
    # (as this repo's own dev machine did), and a leaky mock here would
    # mean `pytest` could kick off a real, billable Azure deployment.
    # Force the "not available" path explicitly instead.
    monkeypatch.setattr(migration_control, "is_local_request", lambda host: True)
    monkeypatch.setattr(
        migration_control,
        "check_azure_cli",
        lambda: {"available": False, "message": "mocked: not logged in"},
    )

    resp = client.post(
        "/api/migrate/azure/deploy",
        headers={"X-Migrate-Token": migration_control.MIGRATE_TOKEN},
    )
    # Proves auth passed and control reached start_deploy(), without ever
    # touching the real Azure CLI or spawning a deployment subprocess.
    assert resp.status_code == 200
    body = resp.json()
    assert body["started"] is False
    assert body["message"] == "mocked: not logged in"
