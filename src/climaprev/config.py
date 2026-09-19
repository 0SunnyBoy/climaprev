import ipaddress
import json
from pathlib import Path
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import AliasChoices, Field, PrivateAttr, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CLIMAPREV_",
        validate_default=True,
        hide_input_in_errors=True,
        allow_inf_nan=False,
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("CLIMAPREV_REDIS_URL", "REDIS_URL"),
    )
    redis_password_file: Path | None = None
    _redis_password: SecretStr | None = PrivateAttr(default=None)
    environment: str = "development"
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
    http_max_connections: int = Field(default=20, gt=0)
    http_max_keepalive_connections: int = Field(default=10, gt=0)
    redis_socket_timeout_seconds: float = Field(default=1.0, gt=0)
    additional_retries: int = Field(default=2, ge=0)
    provider_budget_capacity: int = Field(default=60, gt=0)
    provider_budget_refill: int = Field(default=60, gt=0)
    provider_budget_window_seconds: int = Field(default=60, gt=0)
    load_scenario: str | None = None
    load_redis_operation_delay_ms: int = 50

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
            raise TypeError("environment must be a string")
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("environment must not be empty")
        return normalized

    @field_validator(
        "cors_allow_origins", "trusted_proxy_ips", "provider_allowed_hosts", mode="before"
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
            return tuple(str(ipaddress.ip_address(item)) for item in value)
        except ValueError as error:
            raise ValueError("trusted_proxy_ips must contain valid IP addresses") from error

    @model_validator(mode="after")
    def prevent_implicit_production_cors_wildcard(self) -> "Settings":
        if self.environment == "production" and "*" in self.cors_allow_origins:
            raise ValueError("cors_allow_origins must not contain wildcard in production")
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
                    and not url.fragment
                    and not any(character.isspace() for character in value)
                )
            except ValueError:
                valid = False
            if not valid:
                raise ValueError("invalid production provider destination")
        return self

    @model_validator(mode="after")
    def load_redis_password(self) -> "Settings":
        if self.redis_password_file is not None:
            try:
                value = self.redis_password_file.read_text().strip()
                if not value:
                    raise ValueError("empty secret")
            except (OSError, ValueError):
                raise ValueError("Redis secret file is missing, unreadable or empty") from None
            self._redis_password = SecretStr(value)
        return self

    @property
    def redis_password(self) -> str | None:
        return None if self._redis_password is None else self._redis_password.get_secret_value()
