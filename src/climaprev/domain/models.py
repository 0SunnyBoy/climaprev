from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal


@dataclass(frozen=True, slots=True)
class CanonicalLocation:
    name: str
    latitude: float
    longitude: float
    timezone: str
    source: str


@dataclass(frozen=True, slots=True)
class DatePeriod:
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("start must be on or before end")

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1


@dataclass(frozen=True, slots=True)
class DailyForecast:
    date: date
    temperature_min_c: float | None
    temperature_max_c: float | None
    temperature_mean_c: float | None
    humidity_mean_pct: float | None
    precipitation_sum_mm: float | None
    precipitation_probability_max_pct: float | None
    precipitation_max_hourly_mm: float | None
    wind_max_kmh: float | None
    wind_gust_max_kmh: float | None
    weather_code: int | None


@dataclass(frozen=True, slots=True)
class NormalizedForecast:
    location: CanonicalLocation
    period: DatePeriod
    days: tuple[DailyForecast, ...]
    provider: str
    fetched_at: datetime
    is_stale: bool
    missing_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RiskCondition:
    type: str
    severity: Literal["moderate", "high"]
    value: float
    unit: str
    reason: str


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    level: Literal["low", "moderate", "high"]
    method: str
    policy_version: str
    conditions: tuple[RiskCondition, ...]


@dataclass(frozen=True, slots=True)
class OfficialAlert:
    source: str
    event: str
    severity: str
    effective_at: datetime
    expires_at: datetime | None
    geographic_scope: str
    source_url: str | None
