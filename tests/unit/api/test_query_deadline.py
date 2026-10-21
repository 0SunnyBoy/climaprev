import asyncio
from datetime import date
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from starlette.requests import Request
from tests.support.forecast import (
    FakeProvider,
    InMemoryCache,
    InMemoryLock,
    forecast,
    service,
)

from climaprev.api.routes.risk import _execute_risk
from climaprev.api.schemas.risk import RiskQueryParams
from climaprev.application.errors import WeatherProviderUnavailable
from climaprev.config import Settings


class BlockingOperation:
    def __init__(self):
        self.cancelled = False

    async def block(self, *args, **kwargs):
        try:
            await asyncio.sleep(30)
        finally:
            self.cancelled = True


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["geocoding", "cache", "provider", "lock", "alerts"])
async def test_global_deadline_cancels_each_phase_without_leaving_forecast_lock(monkeypatch, phase):
    monkeypatch.setattr("climaprev.api.forecast_window.utc_today", lambda: date(2026, 8, 28))
    blocked = BlockingOperation()
    cache, lock = InMemoryCache(), InMemoryLock()
    provider = FakeProvider(forecast())
    kwargs = {"cache": cache, "lock": lock, "provider": provider}
    if phase == "geocoding":
        kwargs["geocoder"] = SimpleNamespace(resolve=blocked.block)
    elif phase == "cache":
        monkeypatch.setattr(cache, "get", blocked.block)
    elif phase == "provider":
        monkeypatch.setattr(provider, "forecast", blocked.block)
    elif phase == "lock":
        monkeypatch.setattr(lock, "acquire", blocked.block)
    else:
        kwargs["alerts"] = SimpleNamespace(get_alerts=blocked.block)
    query_service = service(**kwargs)
    app = SimpleNamespace(state=SimpleNamespace(settings=Settings(query_total_timeout_seconds=0.02)))
    request = Request({"type": "http", "app": app})
    request.state.request_id = "deadline-test"
    query = RiskQueryParams(location_text="Sao Paulo", start_date=date(2026, 8, 28))
    with pytest.raises(WeatherProviderUnavailable, match="deadline"):
        await asyncio.wait_for(_execute_risk(request, query, query_service), timeout=1)
    assert blocked.cancelled
    assert lock._held is False
    if phase == "provider":
        assert len(lock.releases) == 1
        assert not any(key.startswith("forecast:") for key in cache.entries)


@pytest.mark.parametrize("value", [0, -1, 8.01, float("nan"), float("inf")])
def test_deadline_configuration_is_bounded_and_finite(value):
    with pytest.raises(ValidationError):
        Settings(query_total_timeout_seconds=value)


def test_default_service_budget_is_shorter_than_client_wait():
    assert Settings().query_total_timeout_seconds == 7
