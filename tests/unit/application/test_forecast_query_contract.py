from __future__ import annotations

from datetime import date

from climaprev.application.query import ForecastQuery
from climaprev.domain.units import TemperatureUnit


def test_application_query_carries_validated_http_values_without_importing_http_schema() -> None:
    query = ForecastQuery(
        location_text="Sao Paulo",
        latitude=None,
        longitude=None,
        start_date=date(2026, 8, 28),
        end_date=date(2026, 8, 28),
        temperature_unit=TemperatureUnit.CELSIUS,
    )

    assert query.location_text == "Sao Paulo"
    assert query.temperature_unit is TemperatureUnit.CELSIUS
