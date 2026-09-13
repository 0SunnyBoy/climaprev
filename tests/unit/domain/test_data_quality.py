from dataclasses import replace

import pytest

from climaprev.domain.data_quality import completeness
from tests.integration.application.test_forecast_query import forecast


@pytest.mark.parametrize("state,expected", [("zero", "complete"), ("none", "unavailable"),
                                           ("gap", "partial")])
def test_completeness_depends_on_policy_inputs_and_coverage(state, expected):
    value = forecast()
    day = replace(value.days[0], **dict.fromkeys(("temperature_min_c", "temperature_max_c", "precipitation_sum_mm",
                                 "precipitation_max_hourly_mm", "wind_gust_max_kmh"),
                                None if state == "none" else 0))
    value = replace(value, days=(day,), missing_fields=(
        ("hourly.2026-08-28.precipitation.coverage",) if state == "gap" else ()))
    assert completeness(value) == expected
