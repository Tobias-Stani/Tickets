import subprocess
import sys

# Runs in a fresh interpreter: the test suite itself imports every model,
# which would hide a missing import in production entry points.
SCRIPT = """
import app.modules.users.seed
from sqlalchemy.orm import configure_mappers
configure_mappers()
"""


def test_database_entry_point_registers_all_models():
    result = subprocess.run([sys.executable, "-c", SCRIPT], capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
