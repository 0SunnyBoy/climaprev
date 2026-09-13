from __future__ import annotations

from hashlib import sha256
from urllib.parse import urlsplit

from climaprev.application.errors import ProviderRateLimited
from climaprev.config import Settings
from climaprev.infrastructure.rate_limit.redis_rate_limiter import RedisRateLimiter
from climaprev.infrastructure.redis_delay import RedisConnection


class ProviderBudget:
    """Shared token bucket consumed immediately before each external HTTP attempt."""

    def __init__(self, redis: RedisConnection, settings: Settings) -> None:
        self._limiter = RedisRateLimiter(
            redis, environment=f"{settings.environment}:provider-budget"
        )
        self._settings = settings

    async def consume(self, url: str) -> None:
        destination = urlsplit(url).netloc.lower()
        decision = await self._limiter.allow(
            sha256(destination.encode()).hexdigest(),
            limit=self._settings.provider_budget_refill,
            window_seconds=self._settings.provider_budget_window_seconds,
            burst=self._settings.provider_budget_capacity,
        )
        if not decision.allowed:
            raise ProviderRateLimited("provider request budget exhausted")
