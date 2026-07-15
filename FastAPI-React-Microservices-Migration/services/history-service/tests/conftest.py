"""Ensure the default (module-level) engine never touches a real path during tests.

conftest.py is imported by pytest before test modules in this directory, so
setting the env var here — before anything imports app.config/app.database —
keeps the default engine pointed at a throwaway file instead of ./data/history.db.
Individual tests still override the `get_session` dependency with their own
temp-file engine; this just keeps app-import-time side effects harmless.
"""

import os
import tempfile

os.environ.setdefault(
    "HISTORY_DB_PATH", os.path.join(tempfile.gettempdir(), "ms-lab-history-default.db")
)
