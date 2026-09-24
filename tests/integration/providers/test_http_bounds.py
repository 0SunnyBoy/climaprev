"""HTTP-01: decompressed stream limits, total deadline and resource cleanup."""

import asyncio
import gzip
import json
import time

import httpx
import pytest

from climaprev.application.errors import (
    ProviderPermanentError,
    ProviderRateLimited,
    ProviderTransientError,
)
from climaprev.config import Settings
from climaprev.infrastructure.http.client import AsyncJsonHttpClient
from tests.contract.providers.test_open_meteo_payload import (
    valid_forecast_payload,
    valid_geocoding_payload,
)


class Stream(httpx.AsyncByteStream):
    def __init__(self, chunks, delay=0):
        self.chunks = chunks
        self.delay = delay
        self.closed = False
        self.started = asyncio.Event()
        self.read_count = 0

    async def __aiter__(self):
        self.started.set()
        for chunk in self.chunks:
            await asyncio.sleep(self.delay)
            self.read_count += 1
            yield chunk

    async def aclose(self):
        self.closed = True


@pytest.mark.parametrize("headers", [{}, {"content-length": "1"}, {"content-length": "999999999"}])
@pytest.mark.parametrize("extra", [0, 1])
async def test_decompressed_bytes_not_content_length_define_limit(headers, extra):
    payload = b'{"ok":true}'
    stream = Stream([payload[:3], payload[3:], b" " * extra])
    response = httpx.Response(200, headers=headers, stream=stream)
    sent = []
    def respond(request):
        sent.append(request)
        return response
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        client = AsyncJsonHttpClient(http, Settings(provider_max_response_bytes=len(payload)))
        if extra:
            with pytest.raises(ProviderPermanentError, match="size limit"):
                await client.get_json("https://forecast.test", {})
        else:
            assert await client.get_json("https://forecast.test", {}) == {"ok": True}
    assert len(sent) == 1
    assert stream.closed and response.is_closed


async def test_gzip_expansion_is_counted_and_not_retried():
    payload = json.dumps({"secret": "SyntheticSentinel" * 2000}).encode()
    compressed = gzip.compress(payload)
    assert len(compressed) < 1024 < len(payload)
    stream = Stream([compressed])
    sent = []
    def respond(request):
        sent.append(request)
        return httpx.Response(200, headers={"content-encoding": "gzip"}, stream=stream)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        client = AsyncJsonHttpClient(http, Settings(provider_max_response_bytes=1024))
        with pytest.raises(ProviderPermanentError) as raised:
            await client.get_json("https://forecast.test/SyntheticURL", {})
    assert "SyntheticSentinel" not in str(raised.value)
    assert "SyntheticURL" not in str(raised.value)
    assert len(sent) == 1 and stream.closed


async def test_limit_stops_before_reading_rest_of_stream():
    stream = Stream([b"x" * 11, b"must-not-be-read"])
    async with httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, stream=stream)
    )) as http:
        with pytest.raises(ProviderPermanentError):
            await AsyncJsonHttpClient(http, Settings(provider_max_response_bytes=10)).get_json(
                "https://forecast.test", {}
            )
    assert stream.read_count == 1
    assert stream.closed


async def test_total_deadline_interrupts_slow_stream_and_closes_connection():
    stream = Stream([b"{", b"}"], delay=1)
    sent = []
    def respond(request):
        sent.append(request)
        return httpx.Response(200, stream=stream)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        client = AsyncJsonHttpClient(http, Settings(provider_total_timeout_seconds=0.03))
        start = time.monotonic()
        with pytest.raises(ProviderTransientError, match="operation timed out"):
            await client.get_json("https://forecast.test", {})
        assert time.monotonic() - start < 0.5
    assert len(sent) == 1 and stream.closed


async def test_total_deadline_includes_backoff_and_budget_wait():
    sent = []
    def respond(request):
        sent.append(request)
        return httpx.Response(503)
    async def budget(url):
        await asyncio.sleep(1)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        settings = Settings(provider_total_timeout_seconds=0.01)
        for before_send, expected in ((None, 1), (budget, 1)):
            with pytest.raises(ProviderTransientError, match="operation timed out"):
                await AsyncJsonHttpClient(http, settings, before_send=before_send).get_json(
                    "https://forecast.test", {}
                )
            assert len(sent) == expected


async def test_cancellation_is_not_converted_or_retried_and_releases_response():
    stream = Stream([b"{}"], delay=60)
    async with httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, stream=stream)
    )) as http:
        task = asyncio.create_task(AsyncJsonHttpClient(http, Settings()).get_json("https://forecast.test", {}))
        await stream.started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert stream.closed


@pytest.mark.parametrize("status,error,attempts", [
    (302, ProviderPermanentError, 1), (429, ProviderRateLimited, 1),
    (404, ProviderPermanentError, 1), (503, ProviderTransientError, 3),
])
async def test_status_retries_redirect_policy_and_budget_accounting(status, error, attempts):
    responses = []
    budget_calls = []
    retries = []
    async def budget(url):
        budget_calls.append(url)
    def respond(request):
        response = httpx.Response(status, headers={"location": "https://forbidden.test"},
                                  stream=Stream([b"SensitiveProviderBody"]))
        responses.append(response)
        return response
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond), follow_redirects=True) as http:
        client = AsyncJsonHttpClient(http, Settings(), before_send=budget,
                                     on_retry=lambda: retries.append(True))
        with pytest.raises(error) as raised:
            await client.get_json("https://forecast.test/SyntheticURL", {})
    assert len(responses) == len(budget_calls) == attempts
    assert len(retries) == attempts - 1
    assert all(response.is_closed for response in responses)
    assert all(response.request.url.host == "forecast.test" for response in responses)
    assert "SensitiveProviderBody" not in str(raised.value)
    assert "SyntheticURL" not in str(raised.value)


@pytest.mark.parametrize("payload", [valid_forecast_payload(), valid_geocoding_payload(),
    {"hoje": {"fixture": {"evento": "Chuvas Intensas", "severidade": "moderate"}}},
])
async def test_representative_provider_json_fits_default_limit(payload):
    content = json.dumps(payload).encode()
    stream = Stream([content[index:index + 32] for index in range(0, len(content), 32)])
    async with httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, stream=stream)
    )) as http:
        assert await AsyncJsonHttpClient(http, Settings()).get_json("https://forecast.test", {}) == payload
    assert stream.closed
