from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_host_allowlist_from_deployment(monkeypatch):
    """ASGI fixtures own their hosts; do not inherit Compose deployment values."""
    monkeypatch.delenv("CLIMAPREV_ALLOWED_HOSTS", raising=False)


@pytest.fixture
def production_config(tmp_path: Path) -> dict[str, object]:
    """Valid SEC-01 fixtures, never credentials from the operator's environment."""
    password = tmp_path / "redis.password"
    password.write_text("SyntheticRedisPasswordForTests")
    hmac_key = tmp_path / "client-ip-hmac.key"
    hmac_key.write_text("ab" * 32)
    return {
        "redis_password_file": password,
        "client_ip_hmac_key_file": hmac_key,
        "allowed_hosts": ("localhost", "127.0.0.1", "app", "test", "testserver"),
    }
