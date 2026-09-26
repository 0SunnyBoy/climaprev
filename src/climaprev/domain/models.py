from dataclasses import dataclass
from datetime import date, datetime
from math import isfinite
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True, slots=True)
class CanonicalLocation:
    name: str
    latitude: float
    longitude: float
    timezone: str
    source: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("location name must not be empty")
        if not self.source.strip():
            raise ValueError("location source must not be empty")
        if not isfinite(self.latitude) or not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be finite and between -90 and 90")
        if not isfinite(self.longitude) or not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be finite and between -180 and 180")
        try:
            ZoneInfo(self.timezone)
        except (ZoneInfoNotFoundError, ValueError) as error:
            raise ValueError("timezone must be a valid IANA timezone") from error


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
class RiskDayAssessment:
    date: date
    level: Literal["low", "moderate", "high"]
    conditions: tuple[RiskCondition, ...]


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    level: Literal["low", "moderate", "high"]
    method: str
    policy_version: str
    conditions: tuple[RiskCondition, ...]
    daily: tuple[RiskDayAssessment, ...] = ()
    peak_days: tuple[date, ...] = ()


@dataclass(frozen=True, slots=True)
class RiskOverview:
    level: Literal["low", "moderate", "high"]
    source: Literal["forecast_heuristic", "official_alert"]
    peak_days: tuple[date, ...]


@dataclass(frozen=True, slots=True)
class OfficialAlert:
    source: str
    event: str
    severity: str
    effective_at: datetime
    expires_at: datetime | None
    geographic_scope: str
    source_url: str | None
