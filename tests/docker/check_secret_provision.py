"""Host gate: pytest -q tests/docker/check_secret_provision.py.

SEC-01/REDIS-01: provisioning sources intentionally stay outside app images.
"""

import hashlib
import runpy
import stat
import subprocess
import sys
from pathlib import Path

import pytest

PROVISION = Path(__file__).resolve().parents[2] / "docker/homolog/provision.py"


@pytest.mark.parametrize("environment", ["production", "development", "test", "load"])
def test_provision_creates_private_independent_secrets(tmp_path, environment):
    provision = runpy.run_path(str(PROVISION))["provision"]
    directory = tmp_path / "generated"
    provision(directory, 60, 60, 60, environment)
    password = (directory / "redis.password").read_text()
    key = (directory / "client-ip-hmac.key").read_text()
    assert len(bytes.fromhex(key)) == 32
    assert key != password
    assert stat.S_IMODE(directory.stat().st_mode) == 0o700
    for name in ("redis.password", "client-ip-hmac.key", "redis.acl"):
        assert stat.S_IMODE((directory / name).stat().st_mode) == 0o444
    acl = (directory / "redis.acl").read_text()
    assert "user default off\n" in acl
    assert f"#{hashlib.sha256(password.encode()).hexdigest()}" in acl
    assert f"~climaprev:{environment}:* " in acl
    assert "~climaprev:*" not in acl
    assert all(command not in acl for command in ("+scan", "+hgetall", "+config", "+acl"))
    for output in (acl, (directory / "compose.env").read_text()):
        assert password not in output
        assert key not in output
    with pytest.raises(FileExistsError):
        provision(directory, 60, 60, 60, environment)
    assert (directory / "redis.password").read_text() == password
    assert (directory / "client-ip-hmac.key").read_text() == key


def test_invalid_environment_creates_nothing(tmp_path):
    provision = runpy.run_path(str(PROVISION))["provision"]
    directory = tmp_path / "generated"
    with pytest.raises(ValueError, match="invalid environment"):
        provision(directory, 60, 60, 60, "prodution")
    assert not directory.exists()


def test_provision_cli_never_prints_secret_values(tmp_path):
    directory = tmp_path / "generated"
    result = subprocess.run([sys.executable, str(PROVISION), str(directory), "--capacity", "60",
                             "--refill", "60"], check=True, capture_output=True, text=True)
    for name in ("redis.password", "client-ip-hmac.key"):
        assert (directory / name).read_text() not in result.stdout + result.stderr
    assert result.stdout == "Local configuration provisioned; credentials are not displayed.\n"
