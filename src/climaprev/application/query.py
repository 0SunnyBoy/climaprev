from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from climaprev.domain.units import TemperatureUnit


@dataclass(frozen=True, slots=True)
class ForecastQuery:
    """Validated, framework-independent request for a forecast risk query."""

    location_text: str | None
    latitude: float | None
    longitude: float | None
    start_date: date
    end_date: date
    temperature_unit: TemperatureUnit
