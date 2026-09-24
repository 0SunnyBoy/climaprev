import ipaddress
import json
import os
import re
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import urlsplit

from pydantic import (
    AliasChoices,
    Field,
    PrivateAttr,
    SecretStr,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    LOAD = "load"
    PRODUCTION = "production"


def _hostname(value: str) -> bool:
    return bool(re.fullmatch(
        r"(?=.{1,253}$)[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
        r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*", value
    ))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CLIMAPREV_",
        validate_default=True,
        hide_input_in_errors=True,
        allow_inf_nan=False,
        populate_by_name=True,
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("CLIMAPREV_REDIS_URL", "REDIS_URL"),
        repr=False,
        exclude=True,
    )
    redis_password_file: Path | None = Field(default=None, repr=False, exclude=True)
    client_ip_hmac_key_file: Path | None = Field(default=None, repr=False, exclude=True)
    _redis_password: SecretStr | None = PrivateAttr(default=None)
    _client_ip_hmac_key: bytes | None = PrivateAttr(default=None)
    environment: Environment = Environment.DEVELOPMENT
    allowed_hosts: Annotated[tuple[str, ...], NoDecode] = ()
    rate_limit: int = Field(default=60, gt=0)
    rate_limit_window_seconds: int = Field(default=60, gt=0)
    rate_limit_burst: int = Field(default=10, gt=0)
    cors_allow_origins: Annotated[tuple[str, ...], NoDecode] = ()
    trusted_proxy_ips: Annotated[tuple[str, ...], NoDecode] = ()
    provider_allowed_hosts: Annotated[tuple[str, ...], NoDecode] = (
        "api.open-meteo.com",
        "geocoding-api.open-meteo.com",
        "apiprevmet3.inmet.gov.br",
    )
    geocoding_base_url: str = "https://geocoding-api.open-meteo.com"
    forecast_base_url: str = "https://api.open-meteo.com"
    inmet_alerts_base_url: str = "https://apiprevmet3.inmet.gov.br"
    connect_timeout_seconds: float = Field(default=2.0, gt=0)
    read_timeout_seconds: float = Field(default=5.0, gt=0)
    provider_max_response_bytes: int = Field(default=5 * 1024 * 1024, gt=0, le=64 * 1024 * 1024)
    provider_total_timeout_seconds: float = Field(default=20.0, gt=0, le=60)
    http_max_connections: int = Field(default=20, gt=0)
    http_max_keepalive_connections: int = Field(default=10, gt=0)
    redis_socket_timeout_seconds: float = Field(default=1.0, gt=0)
    additional_retries: int = Field(default=2, ge=0)
    provider_budget_capacity: int = Field(default=60, gt=0)
    provider_budget_refill: int = Field(default=60, gt=0)
    provider_budget_window_seconds: int = Field(default=60, gt=0)
    load_scenario: str | None = None
    load_redis_operation_delay_ms: int = 50

    def __init__(self, **values: Any) -> None:
        # InitSettingsSource collapses AliasChoices before model validators run.
        supplied = [values[name] for name in ("CLIMAPREV_REDIS_URL", "REDIS_URL", "redis_url")
                    if name in values]
        if supplied and any(value != supplied[0] for value in supplied[1:]):
            raise ValidationError.from_exception_data(
                type(self).__name__, [{"type": "value_error", "loc": (), "input": None,
                                      "ctx": {"error": ValueError("conflicting Redis URL aliases")}}],
                hide_input=True,
            )
        super().__init__(**values)

    @model_validator(mode="before")
    @classmethod
    def reject_ambiguous_sources(cls, values: object) -> object:
        if isinstance(values, dict):
            aliases = ("CLIMAPREV_REDIS_URL", "REDIS_URL")
            # Check both process aliases before pydantic's AliasChoices discards one.
            supplied = [os.environ[name] for name in aliases if name in os.environ]
            explicit = [values[name] for name in aliases if name in values]
            if ((supplied and any(value != supplied[0] for value in supplied[1:]))
                    or (explicit and any(value != explicit[0] for value in explicit[1:]))):
                raise ValueError("conflicting Redis URL aliases")
        return values

    @property
    def effective_redis_operation_delay_ms(self) -> int:
        if self.environment == "load" and self.load_scenario == "redis_latency":
            return self.load_redis_operation_delay_ms
        return 0

    @field_validator("additional_retries")
    @classmethod
    def clamp_additional_retries(cls, value: int) -> int:
        return min(value, 2)

    @field_validator("load_redis_operation_delay_ms")
    @classmethod
    def nonnegative_load_redis_delay(cls, value: int) -> int:
        if value < 0:
            raise ValueError("load_redis_operation_delay_ms must not be negative")
        return value

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_environment(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("environment must be a string")  # noqa: TRY004 -- Pydantic validation
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("environment must not be empty")
        return normalized

    @field_validator(
        "cors_allow_origins", "trusted_proxy_ips", "provider_allowed_hosts", "allowed_hosts",
        mode="before"
    )
    @classmethod
    def parse_list_values(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                try:
                    decoded = json.loads(stripped)
                except json.JSONDecodeError as error:
                    raise ValueError("list configuration must be valid JSON or CSV") from error
                if not isinstance(decoded, list) or not all(
                    isinstance(item, str) for item in decoded
                ):
                    raise ValueError("list configuration must contain strings")
                return tuple(item.strip() for item in decoded if item.strip())
            return tuple(item.strip() for item in stripped.split(",") if item.strip())
        return value

    @field_validator("trusted_proxy_ips")
    @classmethod
    def normalize_trusted_proxy_ips(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        try:
            if any("%" in item for item in value):
                raise ValueError("scoped addresses are not supported")
            return tuple(str(ipaddress.ip_address(item)) for item in value)
        except ValueError as error:
            raise ValueError("trusted_proxy_ips must contain valid IP addresses") from error

    @model_validator(mode="after")
    def prevent_implicit_production_cors_wildcard(self) -> "Settings":
        if self.environment == "production":
            for origin in self.cors_allow_origins:
                if "*" in origin:
                    raise ValueError("cors_allow_origins must not contain wildcard in production")
                try:
                    url = urlsplit(origin)
                    valid = (url.scheme in ("http", "https") and url.hostname
                             and url.username is None and url.password is None
                             and not url.path and not url.query and not url.fragment
                             and not any(character.isspace() for character in origin)
                             and (url.port is None or 0 < url.port <= 65535))
                except ValueError:
                    valid = False
                if not valid:
                    raise ValueError("invalid production CORS origin")
        return self

    @model_validator(mode="after")
    def validate_http_connection_limits(self) -> "Settings":
        if self.http_max_keepalive_connections > self.http_max_connections:
            raise ValueError(
                "http_max_keepalive_connections must not exceed http_max_connections"
            )
        return self

    @model_validator(mode="after")
    def validate_production_destinations(self) -> "Settings":
        if self.environment != "production":
            return self
        for host in self.provider_allowed_hosts:
            if (not _hostname(host) or "." not in host
                    or host.endswith((".localhost", ".local", ".internal"))
                    or host.rsplit(".", 1)[-1].isdigit()
                    or all(re.fullmatch(r"(?:0x[0-9a-f]+|[0-9]+)", part)
                           for part in host.split("."))):
                raise ValueError("invalid production provider host allowlist")
            try:
                ipaddress.ip_address(host)
            except ValueError:
                pass
            else:
                raise ValueError("invalid production provider host allowlist")
        for value in (
            self.geocoding_base_url,
            self.forecast_base_url,
            self.inmet_alerts_base_url,
        ):
            try:
                url = urlsplit(value)
                valid = (
                    url.scheme == "https"
                    and url.hostname in self.provider_allowed_hosts
                    and url.port in (None, 443)
                    and url.username is None
                    and url.password is None
                    and not url.query
                    and not url.fragment
                    and not any(character.isspace() for character in value)
                )
            except ValueError:
                valid = False
            if not valid:
                raise ValueError("invalid production provider destination")
        return self

    @model_validator(mode="after")
    def validate_hosts_and_redis(self) -> "Settings":
        if not self.allowed_hosts:
            if self.environment == "production":
                raise ValueError("allowed_hosts must be explicit in production")
            self.allowed_hosts = ("localhost", "127.0.0.1", "app", "test", "testserver")
        if any(not _hostname(host) for host in self.allowed_hosts):
            raise ValueError("allowed_hosts must contain exact hostnames without wildcard or port")
        try:
            url = urlsplit(self.redis_url)
            valid = (url.scheme in ("redis", "rediss") and url.hostname
                     and url.port is not None and 0 < url.port <= 65535
                     and bool(re.fullmatch(r"/[0-9]+", url.path))
                     and not url.query and not url.fragment
                     and not any(character.isspace() for character in self.redis_url))
        except ValueError:
            valid = False
        if not valid:
            raise ValueError("invalid Redis URL")
        if url.password is not None and (
            self.environment == "production" or self.redis_password_file is not None
        ):
            raise ValueError("Redis password must have a single file source")
        if self.environment == "production" and any(
            name in os.environ for name in ("CLIMAPREV_REDIS_PASSWORD", "REDIS_PASSWORD")
        ):
            raise ValueError("literal Redis password variables are not supported")
        return self

    @model_validator(mode="after")
    def load_redis_password(self) -> "Settings":
        if self.environment == "production" and self.redis_password_file is None:
            raise ValueError("Redis secret file is required in production")
        if self.redis_password_file is not None:
            try:
                value = self.redis_password_file.read_text().strip()
                if not value:
                    raise ValueError("empty secret")
            except (OSError, ValueError):
                raise ValueError("Redis secret file is missing, unreadable or empty") from None
            self._redis_password = SecretStr(value)
        if self.environment == "production" and self.client_ip_hmac_key_file is None:
            raise ValueError("client IP HMAC key file is required in production")
        if self.client_ip_hmac_key_file is not None:
            try:
                value = self.client_ip_hmac_key_file.read_text().strip()
                if re.fullmatch(r"[0-9a-fA-F]{64}", value) is None:
                    raise ValueError("invalid key")
                self._client_ip_hmac_key = bytes.fromhex(value)
            except (OSError, ValueError):
                raise ValueError("HMAC secret file is missing, unreadable or invalid") from None
        return self

    @property
    def redis_password(self) -> str | None:
        return None if self._redis_password is None else self._redis_password.get_secret_value()

    @property
    def client_ip_hmac_key(self) -> bytes | None:
        return self._client_ip_hmac_key
