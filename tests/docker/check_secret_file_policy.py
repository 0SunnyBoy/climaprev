"""Host gate: pytest -q tests/docker/check_secret_file_policy.py.

GIT-01/CFG-01 needs Git metadata, intentionally absent from application images.
Names only; never inspect local credential contents.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from climaprev.config import Settings


@pytest.mark.parametrize(
    "name,ignored",
    [
        (".env", True),
        (".env.production", True),
        (".env.local", True),
        ("src/.env.production", True),
        ("tests/.env.example", True),
        ("docs/.env.private", True),
        (".homolog/redis.password", True),
        (".env.example", False),
        ("src/climaprev/config.py", False),
    ],
)
def test_git_secret_names(tmp_path: Path, name: str, ignored: bool) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    shutil.copyfile(".gitignore", tmp_path / ".gitignore")
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", name], cwd=tmp_path, check=False
    )
    assert result.returncode == (0 if ignored else 1)


def test_no_tracked_secret_env_names() -> None:
    result = subprocess.run(
        ["git", "ls-files", "-z"], check=True, capture_output=True, text=True
    )
    names = result.stdout.split("\0")
    assert not [
        name for name in names
        if (Path(name).name == ".env" or Path(name).name.startswith(".env."))
        and name != ".env.example"
    ]


def test_example_keeps_local_configuration_and_only_secret_file_references() -> None:
    example = Path(".env.example").read_text()
    fields = dict(line.split("=", 1) for line in example.splitlines()
                  if line and not line.startswith("#"))
    assert fields["CLIMAPREV_ENVIRONMENT"] == "development"
    assert "@" not in fields["REDIS_URL"]
    assert not any("PASSWORD" in key or "HMAC" in key for key in fields)
    assert "# CLIMAPREV_REDIS_PASSWORD_FILE=/run/secrets/redis_password" in example
    assert "# CLIMAPREV_CLIENT_IP_HMAC_KEY_FILE=/run/secrets/client_ip_hmac_key" in example
    settings = Settings(**{key: value for key, value in fields.items()
                           if key == "REDIS_URL"}, environment="development")
    assert settings.redis_password is None
