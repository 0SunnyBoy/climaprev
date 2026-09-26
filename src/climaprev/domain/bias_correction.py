"""Conservative, optional forecast calibration.

The default profile is identity and therefore preserves the provider forecast.
An enabled profile must come from reviewed historical validation; this module
does not estimate coefficients automatically.
"""

from dataclasses import dataclass, replace
from math import isfinite

from climaprev.domain.models import DailyForecast, NormalizedForecast


@dataclass(frozen=True, slots=True)
class ForecastCalibration:
    profile_version: str = "disabled"
    enabled: bool = False
    temperature_offset_c: float = 0.0
    precipitation_multiplier: float = 1.0
    wind_multiplier: float = 1.0

    def __post_init__(self) -> None:
        if not self.profile_version.strip():
            raise ValueError("calibration profile_version must not be empty")
        if not isfinite(self.temperature_offset_c):
            raise ValueError("temperature_offset_c must be finite")
        if not isfinite(self.precipitation_multiplier) or self.precipitation_multiplier < 0:
            raise ValueError("precipitation_multiplier must be finite and non-negative")
        if not isfinite(self.wind_multiplier) or self.wind_multiplier < 0:
            raise ValueError("wind_multiplier must be finite and non-negative")

    @classmethod
    def disabled(cls) -> "ForecastCalibration":
        return cls()

    def apply(self, forecast: NormalizedForecast) -> NormalizedForecast:
        if not self.enabled:
            return forecast
        return replace(forecast, days=tuple(self._apply_day(day) for day in forecast.days))

    def _apply_day(self, day: DailyForecast) -> DailyForecast:
        return replace(
            day,
            temperature_min_c=_offset(day.temperature_min_c, self.temperature_offset_c),
            temperature_max_c=_offset(day.temperature_max_c, self.temperature_offset_c),
            temperature_mean_c=_offset(day.temperature_mean_c, self.temperature_offset_c),
            precipitation_sum_mm=_scale(day.precipitation_sum_mm, self.precipitation_multiplier),
            precipitation_max_hourly_mm=_scale(
                day.precipitation_max_hourly_mm, self.precipitation_multiplier
            ),
            wind_max_kmh=_scale(day.wind_max_kmh, self.wind_multiplier),
            wind_gust_max_kmh=_scale(day.wind_gust_max_kmh, self.wind_multiplier),
        )


def _offset(value: float | None, amount: float) -> float | None:
    return None if value is None else value + amount


def _scale(value: float | None, multiplier: float) -> float | None:
    return None if value is None else max(0.0, value * multiplier)
