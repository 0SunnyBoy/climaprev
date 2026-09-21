"""CFG-01, SEC-01 and HTTP-01 configuration acceptance criteria."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from climaprev.config import Settings


@pytest.mark.parametrize("environment", ["prodution", "stage", "integration", "", 123])
def test_environment_is_closed(environment) -> None:
    with pytest.raises(ValidationError):
        Settings(environment=environment)


@pytest.mark.parametrize("environment", [" Development ", "TEST", "load"])
def test_nonproduction_can_use_synthetic_data_without_secrets(environment) -> None:
    settings = Settings(environment=environment)
    assert settings.environment == environment.strip().lower()
    assert settings.redis_password is None
    assert settings.client_ip_hmac_key is None


def test_production_secrets_are_private(production_config) -> None:
    settings = Settings(environment=" Production ", **production_config)
    assert settings.redis_password == "SyntheticRedisPasswordForTests"
    assert settings.client_ip_hmac_key == bytes.fromhex("ab" * 32)
    for output in (repr(settings), settings.model_dump_json(), str(settings.model_dump())):
        assert "SyntheticRedisPasswordForTests" not in output
        assert "ab" * 32 not in output
        assert str(production_config["redis_password_file"]) not in output


@pytest.mark.parametrize("field", ["redis_password_file", "client_ip_hmac_key_file"])
def test_production_requires_both_secret_files(production_config, field) -> None:
    production_config.pop(field)
    with pytest.raises(ValidationError, match="required in production"):
        Settings(environment="production", **production_config)


@pytest.mark.parametrize("contents", ["", "abcdef", "gh" * 32, "aa" * 31, "aa" * 33])
def test_hmac_file_rejects_invalid_material_without_echo(tmp_path, contents) -> None:
    secret = tmp_path / "SecretPathSentinel"
    secret.write_text(contents)
    with pytest.raises(ValidationError) as raised:
        Settings(client_ip_hmac_key_file=secret)
    assert "HMAC secret file" in str(raised.value)
    assert "SecretPathSentinel" not in str(raised.value)
    if contents:
        assert contents not in str(raised.value)


@pytest.mark.parametrize("field", ["redis_password_file", "client_ip_hmac_key_file"])
def test_unreadable_secret_is_sanitized(monkeypatch, field, tmp_path) -> None:
    def denied(*args, **kwargs):
        raise PermissionError("SecretPathSentinel")
    monkeypatch.setattr(Path, "read_text", denied)
    with pytest.raises(ValidationError) as raised:
        Settings(**{field: tmp_path / "SecretPathSentinel"})
    assert "unreadable" in str(raised.value)
    assert "SecretPathSentinel" not in str(raised.value)


def test_redis_aliases_reject_ambiguity_before_selection(monkeypatch) -> None:
    monkeypatch.setenv("CLIMAPREV_REDIS_URL", "redis://redis:6379/0")
    monkeypatch.setenv("REDIS_URL", "redis://redis:6380/0")
    with pytest.raises(ValidationError, match="conflicting Redis URL aliases"):
        Settings()
    monkeypatch.setenv("REDIS_URL", "redis://redis:6379/0")
    assert Settings().redis_url == "redis://redis:6379/0"


def test_constructor_redis_aliases_and_override(monkeypatch) -> None:
    monkeypatch.delenv("CLIMAPREV_REDIS_URL", raising=False)
    monkeypatch.setenv("REDIS_URL", "redis://redis:6379/0")
    assert Settings(redis_url="redis://localhost:6380/1").redis_url == "redis://localhost:6380/1"
    with pytest.raises(ValidationError, match="conflicting Redis URL aliases"):
        Settings(CLIMAPREV_REDIS_URL="redis://redis:6379/0", REDIS_URL="redis://redis:6380/0")


@pytest.mark.parametrize("url", [
    "http://redis:6379/0", "redis://:6379/0", "redis://redis:0/0",
    "redis://redis:bad/0", "redis://redis:6379/-1", "redis://redis:6379/abc",
    "redis://redis:6379/0?password=SecretSentinel", "redis://redis:6379/0#x",
])
def test_invalid_redis_urls_are_sanitized(url) -> None:
    with pytest.raises(ValidationError) as raised:
        Settings(redis_url=url)
    assert "invalid Redis URL" in str(raised.value)
    assert url not in str(raised.value)


def test_production_rejects_inline_password_and_competing_sources(production_config) -> None:
    for environment in ("development", "production"):
        with pytest.raises(ValidationError, match="single file source") as raised:
            Settings(environment=environment, redis_url="redis://user:SecretSentinel@redis:6379/0",
                     **production_config)
        assert "SecretSentinel" not in str(raised.value)


@pytest.mark.parametrize("name", ["CLIMAPREV_REDIS_PASSWORD", "REDIS_PASSWORD"])
def test_production_rejects_password_environment_variable(monkeypatch, production_config, name):
    monkeypatch.setenv(name, "SecretSentinel")
    with pytest.raises(ValidationError, match="literal Redis password") as raised:
        Settings(environment="production", **production_config)
    assert "SecretSentinel" not in str(raised.value)


@pytest.mark.parametrize("hosts", [(), ("*",), ("*.example.com",), ("https://example.com",),
                                   ("localhost:8000",), ("bad host",)])
def test_production_requires_exact_allowed_hosts(production_config, hosts):
    production_config["allowed_hosts"] = hosts
    with pytest.raises(ValidationError, match="allowed_hosts"):
        Settings(environment="production", **production_config)


@pytest.mark.parametrize("host", ["localhost", "redis", "127.0.0.1", "169.254.169.254",
                                  "weather.internal", "weather.local", "*.example.com",
                                  "127.0.0.01", "127.1", "0x7f.0x0.0x0.0x1"])
def test_production_provider_allowlist_rejects_internal_or_ip_hosts(production_config, host):
    with pytest.raises(ValidationError, match="provider host allowlist"):
        Settings(environment="production", provider_allowed_hosts=(host,), **production_config)


@pytest.mark.parametrize("field,invalid", [
    ("provider_max_response_bytes", [0, -1, 67108865, 1.5]),
    ("provider_total_timeout_seconds", [0, -1, 60.1, float("inf"), float("nan")]),
])
def test_http_bounds_are_positive_finite_and_capped(field, invalid):
    for value in invalid:
        with pytest.raises(ValidationError):
            Settings(**{field: value})
    assert Settings().provider_max_response_bytes == 5 * 1024 * 1024
    assert Settings().provider_total_timeout_seconds == 20


def test_bad_secret_fails_before_application_startup(production_config, monkeypatch):
    from climaprev.main import create_app
    monkeypatch.setenv("CLIMAPREV_ENVIRONMENT", "production")
    monkeypatch.setenv("CLIMAPREV_ALLOWED_HOSTS", "localhost")
    monkeypatch.setenv("CLIMAPREV_REDIS_PASSWORD_FILE", "/nonexistent/SyntheticSecretPath")
    with pytest.raises(ValidationError) as raised:
        create_app()
    assert "SyntheticSecretPath" not in str(raised.value)
