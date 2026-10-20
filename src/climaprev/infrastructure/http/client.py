from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable, Mapping
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
        before_send: Callable[[str], Awaitable[None]] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self._client = client
        self._headers = dict(headers) if headers is not None else None
        self._before_send = before_send
        self._additional_retries = settings.additional_retries
        self._on_retry = on_retry
        self._max_response_bytes = settings.provider_max_response_bytes
        self._total_timeout = settings.provider_total_timeout_seconds
        self._timeout = httpx.Timeout(
            connect=settings.connect_timeout_seconds,
            read=settings.read_timeout_seconds,
            write=settings.read_timeout_seconds,
            pool=settings.connect_timeout_seconds,
        )

    async def get_json(
        self, url: str, params: Mapping[str, str | float | int]
    ) -> dict[str, object]:
        try:
            async with asyncio.timeout(self._total_timeout):
                return await self._get_json(url, params)
        except TimeoutError:
            raise ProviderTransientError("provider operation timed out") from None

    async def _get_json(
        self, url: str, params: Mapping[str, str | float | int]
    ) -> dict[str, object]:
        attempts = self._additional_retries + 1
        for attempt in range(attempts):
            if self._before_send is not None:
                await self._before_send(url)
            try:
                async with self._client.stream(
                    "GET", url, params=params, headers=self._headers,
                    timeout=self._timeout, follow_redirects=False
                ) as response:
                    if response.status_code >= 500:
                        raise ProviderTransientError("provider server error")
                    if response.status_code == 429:
                        raise ProviderRateLimited("provider request limit reached")
                    if response.status_code >= 400:
                        raise ProviderPermanentError("provider rejected the request")
                    if 300 <= response.status_code < 400:
                        raise ProviderPermanentError("provider redirect rejected")
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        if len(body) + len(chunk) > self._max_response_bytes:
                            raise ProviderPermanentError("provider response exceeded size limit")
                        body.extend(chunk)
                    try:
                        payload: object = json.loads(body)
                    except (ValueError, UnicodeDecodeError):
                        raise WeatherDataInvalid("provider response is not valid JSON") from None
                    if not isinstance(payload, dict):
                        raise WeatherDataInvalid("provider response must be a JSON object")
                    return payload
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
            except ProviderRateLimited:
                raise
            except ProviderTransientError:
                if attempt + 1 == attempts:
                    raise
                await self._backoff(attempt)
                continue

        raise AssertionError("request retry loop must return or raise")

    async def _backoff(self, attempt: int) -> None:
        if self._on_retry is not None:
            self._on_retry()
        delay = min(_BACKOFF_SECONDS * (2**attempt), _MAX_BACKOFF_SECONDS)
        await asyncio.sleep(delay)
