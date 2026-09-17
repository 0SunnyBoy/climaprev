from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Protocol

from climaprev.domain.models import (
    CanonicalLocation,
    DatePeriod,
    NormalizedForecast,
    OfficialAlert,
    RiskAssessment,
)

if TYPE_CHECKING:
    from typing import Any

    RiskPolicy = Any


@dataclass(frozen=True, slots=True)
class CacheEntry:
    value: object
    is_stale: bool
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    retry_after_seconds: int


class GeocodingPort(Protocol):
    async def resolve(self, text: str) -> CanonicalLocation:
        pass


class WeatherProviderPort(Protocol):
    async def forecast(
        self,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> NormalizedForecast:
        pass


class OfficialAlertPort(Protocol):
    async def get_alerts(
        self,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> list[OfficialAlert]:
        pass


class RiskEvaluatorPort(Protocol):
    def evaluate(
        self,
        forecast: NormalizedForecast,
        policy: RiskPolicy,
    ) -> RiskAssessment:
        pass


class CachePort(Protocol):
    async def get(self, key: str) -> CacheEntry | None:
        pass

    async def set(
        self,
        key: str,
        value: CacheEntry,
        fresh_ttl_seconds: int,
        stale_ttl_seconds: int,
    ) -> None:
        pass


class LockPort(Protocol):
    async def acquire(self, key: str, ttl_seconds: int) -> str | None:
        pass

    async def refresh(self, key: str, token: str, ttl_seconds: int) -> bool:
        pass

    async def release(self, key: str, token: str) -> bool:
        pass


class RateLimiterPort(Protocol):
    async def allow(
        self,
        identity: str,
        limit: int,
        window_seconds: int,
        burst: int,
    ) -> RateLimitDecision:
        pass


class MetricsPort(Protocol):
    def record_cache_status(self, status: str) -> None:
        pass

    def record_provider_request(self, provider: str, duration_seconds: float, outcome: str) -> None:
        pass

    def record_upstream_error(self) -> None:
        pass

    def record_risk_evaluation(self, assessment: RiskAssessment) -> None:
        pass

    def record_missing_fields(self, fields: tuple[str, ...]) -> None:
        pass
