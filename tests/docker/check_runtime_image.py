"""Run explicitly inside the final runtime image with this script mounted read-only."""

import importlib.util
import os
from pathlib import Path

import climaprev

assert os.getuid() == 10001
assert not Path("/app/tests").exists()
assert not Path("/app/docs").exists()
assert not Path("/app/.env").exists()
assert not Path("/app/.env.example").exists()
for dependency in ("pytest", "ruff", "mypy", "locust", "setuptools", "wheel"):
    assert importlib.util.find_spec(dependency) is None
assert Path(climaprev.__file__).is_file()
assert importlib.util.find_spec("climaprev.runtime") is not None
print("runtime: UID10001; production package present; tests/docs/env/dev tools absent")
