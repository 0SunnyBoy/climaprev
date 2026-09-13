from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from typing import Final

import httpx

from climaprev.application.errors import (
    ProviderPermanentError,
    ProviderRateLimited,
    ProviderTransientError,
    WeatherDataInvalid,
)
from climaprev.config import Settings

__all__ = [
    "AsyncJsonHttpClient",
    "ProviderPermanentError",
    "ProviderRateLimited",
    "ProviderTransientError",
    "WeatherDataInvalid",
]

_BACKOFF_SECONDS: Final = 0.05
_MAX_BACKOFF_SECONDS: Final = 0.1


class AsyncJsonHttpClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        settings: Settings,
        *,
        on_retry: Callable[[], None] | None = None,
    ) -> None:
        self._client = client
        self._additional_retries = settings.additional_retries
        self._on_retry = on_retry
        self._timeout = httpx.Timeout(
            connect=settings.connect_timeout_seconds,
            read=settings.read_timeout_seconds,
            write=settings.read_timeout_seconds,
            pool=settings.connect_timeout_seconds,
        )

    async def get_json(self, url: str, params: Mapping[str, str | float | int]) -> dict[str, object]:
        attempts = self._additional_retries + 1
        for attempt in range(attempts):
            try:
                response = await self._client.get(url, params=params, timeout=self._timeout)
            except httpx.TimeoutException as error:
                if attempt + 1 == attempts:
                    raise ProviderTransientError("provider request timed out") from error
                await self._backoff(attempt)
                continue
            except httpx.RequestError as error:
                if attempt + 1 == attempts:
                    raise ProviderTransientError("provider request failed") from error
                await self._backoff(attempt)
                continue

            if response.status_code >= 500:
                if attempt + 1 == attempts:
                    raise ProviderTransientError("provider server error")
                await self._backoff(attempt)
                continue
            if response.status_code == 429:
                raise ProviderRateLimited("provider request limit reached")
            if response.status_code >= 400:
                raise ProviderPermanentError("provider rejected the request")

            try:
                payload: object = response.json()
            except ValueError as error:
                raise WeatherDataInvalid("provider response is not valid JSON") from error
            if not isinstance(payload, dict):
                raise WeatherDataInvalid("provider response must be a JSON object")
            return payload

        raise AssertionError("request retry loop must return or raise")

    async def _backoff(self, attempt: int) -> None:
        if self._on_retry is not None:
            self._on_retry()
        delay = min(_BACKOFF_SECONDS * (2**attempt), _MAX_BACKOFF_SECONDS)
        await asyncio.sleep(delay)
