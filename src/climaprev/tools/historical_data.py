"""Quality-aware daily cases from saved hourly provider payloads."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from climaprev.application.errors import WeatherDataInvalid
from climaprev.domain.models import DailyForecast, DatePeriod
from climaprev.domain.risk_policy import RiskPolicy
from climaprev.domain.verification import Level

EVENT_FIELDS = {
    "rain_hourly": "precipitation_max_hourly_mm",
    "rain_daily": "precipitation_sum_mm",
    "wind_gust": "wind_gust_max_kmh",
    "heat": "temperature_max_c",
    "cold": "temperature_min_c",
}
EVENT_UNITS = {
    "rain_hourly": "mm/h", "rain_daily": "mm/day", "wind_gust": "km/h",
    "heat": "celsius", "cold": "celsius",
}
_FIELDS = (
    "temperature_2m", "precipitation", "wind_gusts_10m",
    "relative_humidity_2m", "weather_code",
)
_EVENT_SERIES = {
    "rain_hourly": "precipitation", "rain_daily": "precipitation",
    "wind_gust": "wind_gusts_10m", "heat": "temperature_2m", "cold": "temperature_2m",
}


@dataclass(frozen=True, slots=True)
class CheckedDay:
    forecast: DailyForecast
    expected_hours: int
    valid_hours: dict[str, int]
    eligible: dict[str, bool]
    missing_fields: tuple[str, ...]


def payload_timezone(payload: Mapping[str, object]) -> str:
    value = payload.get("timezone")
    if not isinstance(value, str):
        raise WeatherDataInvalid("historical timezone is missing")
    try:
        ZoneInfo(value)
    except (ValueError, ZoneInfoNotFoundError) as error:
        raise WeatherDataInvalid("historical timezone is invalid") from error
    return value


def _timeline(day: date, zone: ZoneInfo) -> list[datetime]:
    start = datetime.combine(day, time.min, zone).astimezone(UTC)
    end = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC)
    result: list[datetime] = []
    while start < end:
        result.append(start)
        start += timedelta(hours=1)
    return result


def _number(value: object, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float) or not isfinite(value):
        raise WeatherDataInvalid("historical values must be finite numbers or null")
    if field in ("precipitation", "wind_gusts_10m") and value < 0:
        raise WeatherDataInvalid("historical rain and wind must not be negative")
    if field == "relative_humidity_2m" and not 0 <= value <= 100:
        raise WeatherDataInvalid("historical humidity must be between zero and 100")
    return float(value)


def normalize_hourly(
    payload: Mapping[str, object], period: DatePeriod, *, suffix: str = "",
    minimum_coverage: float = 1.0,
) -> dict[date, CheckedDay]:
    if (isinstance(minimum_coverage, bool) or not isinstance(minimum_coverage, int | float)
            or not isfinite(minimum_coverage) or not 0 < minimum_coverage <= 1):
        raise ValueError("minimum coverage must be between zero (exclusive) and one")
    zone = ZoneInfo(payload_timezone(payload))
    hourly = payload.get("hourly")
    if not isinstance(hourly, Mapping):
        raise WeatherDataInvalid("historical hourly payload must be an object")
    raw_times = hourly.get("time")
    if not isinstance(raw_times, list):
        raise WeatherDataInvalid("historical hourly.time must be a list")
    days = [period.start + timedelta(days=index) for index in range(period.days)]
    timeline = [instant for day in days for instant in _timeline(day, zone)]
    local_timeline = [instant.astimezone(zone).replace(tzinfo=None) for instant in timeline]
    dates: list[date] = []
    position = 0
    for value in raw_times:
        if not isinstance(value, str):
            raise WeatherDataInvalid("historical timestamps must be ISO datetimes")
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as error:
            raise WeatherDataInvalid("historical timestamp is invalid") from error
        # Naive repeated hours are valid only when the civil timeline repeats them.
        while position < len(timeline):
            expected = timeline[position] if parsed.tzinfo else local_timeline[position]
            if parsed == expected:
                break
            position += 1
        if position == len(timeline):
            raise WeatherDataInvalid("historical timestamps are duplicated or misaligned")
        dates.append(timeline[position].astimezone(zone).date())
        position += 1
    series: dict[str, list[float | None]] = {}
    units = payload.get("hourly_units")
    if not isinstance(units, Mapping):
        raise WeatherDataInvalid("historical hourly_units must be explicit")
    expected_units = {"temperature_2m": "°C", "precipitation": "mm",
                      "wind_gusts_10m": "km/h"}
    for field in _FIELDS:
        key = field + suffix
        raw = hourly.get(key)
        if raw is None:
            raw = [None] * len(dates)
        if not isinstance(raw, list) or len(raw) != len(dates):
            raise WeatherDataInvalid("historical series is misaligned")
        if (field in expected_units and key in hourly
                and units.get(key) != expected_units[field]):
            raise WeatherDataInvalid("historical field has unexpected units")
        series[field] = [_number(value, field) for value in raw]
    result: dict[date, CheckedDay] = {}
    for day in days:
        indexes = [index for index, value in enumerate(dates) if value == day]
        values = {
            field: [series[field][index] for index in indexes if series[field][index] is not None]
            for field in _FIELDS
        }
        expected_hours = len(_timeline(day, zone))
        counts = {field: len(items) for field, items in values.items()}
        eligible = {
            event: counts[field] > 0 and counts[field] / expected_hours >= minimum_coverage
            for event, field in _EVENT_SERIES.items()
        }
        # A partial sum is never a full-day precipitation total.
        eligible["rain_daily"] = counts["precipitation"] == expected_hours
        missing = tuple(
            f"hourly.{day.isoformat()}.{field}.coverage"
            for field in ("temperature_2m", "precipitation", "wind_gusts_10m")
            if counts[field] < expected_hours
        )
        temperatures = [v for v in values["temperature_2m"] if v is not None]
        rain = [v for v in values["precipitation"] if v is not None]
        gusts = [v for v in values["wind_gusts_10m"] if v is not None]
        humidity = [v for v in values["relative_humidity_2m"] if v is not None]
        codes = [v for v in values["weather_code"] if v is not None]
        forecast = DailyForecast(
            day, min(temperatures) if temperatures else None,
            max(temperatures) if temperatures else None,
            sum(temperatures) / len(temperatures) if temperatures else None,
            sum(humidity) / len(humidity) if humidity else None,
            sum(rain) if rain else None, None, max(rain) if rain else None, None,
            max(gusts) if gusts else None, int(codes[0]) if codes else None,
        )
        result[day] = CheckedDay(forecast, expected_hours, counts, eligible, missing)
    return result


def event_level(day: DailyForecast, event: str, policy: RiskPolicy) -> Level:
    """Keep diagnostics separate even when the public response groups conditions."""
    field = EVENT_FIELDS[event]
    value = getattr(day, field)
    if value is None:
        raise ValueError("cannot label an event without its meteorological value")
    moderate, high = {
        "rain_hourly": (policy.hourly_rain_moderate_mm, policy.hourly_rain_high_mm),
        "rain_daily": (policy.daily_rain_moderate_mm, policy.daily_rain_high_mm),
        "wind_gust": (policy.wind_gust_moderate_kmh, policy.wind_gust_high_kmh),
        "heat": (policy.temperature_max_moderate_c, policy.temperature_max_high_c),
        "cold": (policy.temperature_min_moderate_c, policy.temperature_min_high_c),
    }[event]
    if event == "cold":
        return "high" if value <= high else "moderate" if value <= moderate else "low"
    return "high" if value >= high else "moderate" if value >= moderate else "low"
