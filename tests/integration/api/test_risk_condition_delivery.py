"""Real use case/evaluator/HTTP mapping with controlled upstream forecasts."""

from dataclasses import replace

import httpx
import pytest

from climaprev.api.deps import enforce_rate_limit, get_forecast_query_service
from climaprev.config import Settings
from climaprev.main import create_app
from tests.support.forecast import FakeProvider, forecast, service


@pytest.mark.asyncio
@pytest.mark.parametrize("unit", ["celsius", "fahrenheit"])
@pytest.mark.parametrize("changes,expected,level", [
    ({"precipitation_max_hourly_mm": 20}, {"heavy_rain_proxy", "flooding_risk_proxy"}, "moderate"),
    ({"precipitation_sum_mm": 50}, {"heavy_rain_proxy", "flooding_risk_proxy"}, "high"),
    ({"wind_gust_max_kmh": 61}, {"strong_wind_proxy"}, "high"),
    ({"temperature_max_c": 40}, {"temperature_extreme_proxy"}, "high"),
    ({"temperature_min_c": 0}, {"temperature_extreme_proxy"}, "high"),
    ({"wind_gust_max_kmh": None, "temperature_max_c": 40}, {"temperature_extreme_proxy"}, "high"),
    ({"precipitation_sum_mm": 50, "wind_gust_max_kmh": 61, "temperature_max_c": 40},
     {"heavy_rain_proxy", "flooding_risk_proxy", "strong_wind_proxy", "temperature_extreme_proxy"},
     "high"),
])
async def test_all_conditions_survive_real_use_case_and_http(changes, expected, level, unit):
    original = forecast()
    values = {"temperature_min_c": 18, "temperature_max_c": 28,
              "precipitation_sum_mm": 0, "precipitation_max_hourly_mm": 0,
              "wind_gust_max_kmh": 20, **changes}
    controlled = replace(original, days=(replace(original.days[0], **values),))
    case = service(provider=FakeProvider(controlled))
    app = create_app(Settings(allowed_hosts=("testserver",)))
    app.dependency_overrides[get_forecast_query_service] = lambda: case
    app.dependency_overrides[enforce_rate_limit] = lambda: None
    # ASGI transport does not start production resources: cache/lock/provider are local doubles.
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
                                  base_url="http://testserver") as client:
        response = await client.post("/api/v1/risk", json={
            "location_text": "synthetic-location", "start_date": "2026-08-28",
            "temperature_unit": unit,
        })
    assert response.status_code == 200
    result = response.json()
    risk = result["forecast_risk"]
    assert risk["level"] == level
    assert {c["type"] for c in risk["conditions"]} == expected
    assert {c["type"] for c in risk["daily"][0]["conditions"]} == expected
    assert result["risk_overview"]["level"] == level
    assert result["official_alerts"]["status"] == "not_configured"
    assert risk["policy_version"] == "reference-v1"
    if changes.get("wind_gust_max_kmh", 20) is None:
        assert result["data_quality"]["completeness"] == "partial"
    for condition in risk["conditions"]:
        if condition["type"] == "temperature_extreme_proxy":
            assert condition["unit"] == unit
