from typing import Literal

from climaprev.domain.models import NormalizedForecast

Completeness = Literal["complete", "partial", "unavailable"]
RISK_FIELDS = (
    "temperature_min_c", "temperature_max_c", "precipitation_sum_mm",
    "precipitation_max_hourly_mm", "wind_gust_max_kmh",
)


def completeness(forecast: NormalizedForecast) -> Completeness:
    present = [getattr(day, field) is not None for day in forecast.days for field in RISK_FIELDS]
    if not any(present):
        return "unavailable"
    coverage_missing = any(field.endswith(".precipitation.coverage")
                           for field in forecast.missing_fields)
    if all(present) and not coverage_missing:
        return "complete"
    return "partial"
