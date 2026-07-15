"""Human-run confirmation test: verifies the microservices-lab Azure
resource group no longer exists after running azure/scripts/teardown.sh.

This is NOT part of the normal `make test` pass - it requires the Azure
CLI to be installed, the user to be logged in (`az login`), and is only
meaningful *after* a teardown has actually been run. It is skipped
(not failed) whenever those preconditions aren't met, so it never
breaks a routine `pytest` run of the repo.

Run it manually after tearing down:

    AZURE_RESOURCE_GROUP=rg-microservices-lab \
        pytest azure/tests/test_teardown_verification.py -v
"""

from __future__ import annotations

import os
import shutil
import subprocess

import pytest

RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "rg-microservices-lab")


def _az_available_and_logged_in() -> bool:
    if shutil.which("az") is None:
        return False
    try:
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return False
    return result.returncode == 0


@pytest.mark.skipif(
    not _az_available_and_logged_in(),
    reason=(
        "Azure CLI not installed or not logged in (`az login`). This test "
        "only makes sense to run manually, after azure/scripts/teardown.sh, "
        "with live Azure credentials."
    ),
)
def test_resource_group_no_longer_exists() -> None:
    """After teardown, `az group exists` should report false."""
    result = subprocess.run(
        ["az", "group", "exists", "--name", RESOURCE_GROUP],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    output = result.stdout.strip().lower()
    assert output == "false", (
        f"Resource group '{RESOURCE_GROUP}' still exists (az group exists "
        f"returned {output!r}). Run azure/scripts/teardown.sh first, or "
        "wait for a still-in-progress deletion to finish."
    )
