from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from math import isfinite
from typing import Final
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx

from climaprev.application.errors import (
    LocationNotFound,
    WeatherDataInvalid,
)
from climaprev.config import Settings
from climaprev.domain.models import (
    CanonicalLocation,
    DailyForecast,
    DatePeriod,
    NormalizedForecast,
)
from climaprev.infrastructure.http.client import AsyncJsonHttpClient

_DAILY_FIELDS: Final = (
    "temperature_2m_min",
    "temperature_2m_max",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "weather_code",
)
_HOURLY_FIELDS: Final = (
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "precipitation_probability",
)



class OpenMeteoGeocodingClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        settings: Settings,
        *,
        on_retry: Callable[[], None] | None = None,
        before_send: Callable[[str], Awaitable[None]] | None = None,
    ) -> None:
        self._http = AsyncJsonHttpClient(
            client, settings, on_retry=on_retry, before_send=before_send
        )
        self._base_url = settings.geocoding_base_url.rstrip("/")

    async def resolve(self, text: str) -> CanonicalLocation:
        locations = await self.search(text)
        if not locations:
            raise LocationNotFound("location was not found")
        return locations[0]

    async def search(self, text: str) -> list[CanonicalLocation]:
        payload = await self._http.get_json(
            f"{self._base_url}/v1/search",
            {"name": text, "language": "pt"},
        )
        results = payload.get("results")
        # Open-Meteo omits empty fields: a real no-match response carries only
        # finite generation timing. Do not reinterpret arbitrary malformed data.
        generation_time = _number_or_none(payload.get("generationtime_ms"))
        if (
            set(payload) == {"generationtime_ms"}
            and generation_time is not None and generation_time >= 0
        ):
            return []
        if results is None:
            raise WeatherDataInvalid("geocoding results must be a list")
        if not isinstance(results, list):
            raise WeatherDataInvalid("geocoding results must be a list")
        locations: list[CanonicalLocation] = []
        for item in results:
            location = _canonical_location(item, include_context=True)
            if location is not None:
                locations.append(location)
        return locations


class OpenMeteoForecastClient:
    def __init__(
        self,
        client: httpx.AsyncClient,
        settings: Settings,
        *,
        on_retry: Callable[[], None] | None = None,
        before_send: Callable[[str], Awaitable[None]] | None = None,
    ) -> None:
        self._http = AsyncJsonHttpClient(
            client, settings, on_retry=on_retry, before_send=before_send
        )
        self._base_url = settings.forecast_base_url.rstrip("/")

    async def forecast(
        self,
        location: CanonicalLocation,
        period: DatePeriod,
    ) -> NormalizedForecast:
        payload = await self._http.get_json(
            f"{self._base_url}/v1/forecast",
            {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "start_date": period.start.isoformat(),
                "end_date": period.end.isoformat(),
                "timezone": "auto",
                "temperature_unit": "celsius",
                "precipitation_unit": "mm",
                "wind_speed_unit": "kmh",
                "daily": ",".join(_DAILY_FIELDS),
                "hourly": ",".join(_HOURLY_FIELDS),
            },
        )
        days, missing_fields = _normalize_forecast(payload, period)
        return NormalizedForecast(
            location=replace(
                location, timezone=_iana_timezone(payload.get("timezone"), "forecast timezone")
            ),
            period=period,
            days=days,
            provider="open-meteo",
            fetched_at=datetime.now(UTC),
            is_stale=False,
            missing_fields=missing_fields,
        )


def _canonical_location(
    item: object,
    *,
    include_context: bool = False,
) -> CanonicalLocation | None:
    if not isinstance(item, Mapping):
        return None
    name = item.get("name")
    latitude = _number_or_none(item.get("latitude"))
    longitude = _number_or_none(item.get("longitude"))
    provider_timezone = item.get("timezone")
    if not isinstance(name, str) or not name.strip():
        return None
    if latitude is None or longitude is None:
        return None
    if not isinstance(provider_timezone, str) or not provider_timezone.strip():
        return None
    display_name = name
    if include_context:
        context = [item.get("admin1"), item.get("country")]
        suffix = ", ".join(
            value.strip() for value in context if isinstance(value, str) and value.strip()
        )
        if suffix:
            display_name = f"{name}, {suffix}"
    return CanonicalLocation(
        name=display_name,
        latitude=latitude,
        longitude=longitude,
        timezone=_iana_timezone(provider_timezone, "geocoding timezone"),
        source="open-meteo-geocoding",
    )


def _normalize_forecast(
    payload: Mapping[str, object],
    period: DatePeriod,
) -> tuple[tuple[DailyForecast, ...], tuple[str, ...]]:
    timezone = _iana_timezone(payload.get("timezone"), "forecast timezone")
    daily = _object(payload.get("daily"), "daily")
    hourly = _object(payload.get("hourly"), "hourly")
    dates = _daily_dates(daily, period)
    missing_fields: list[str] = []
    daily_series = {
        field: _optional_series(daily, field, len(dates), "daily", missing_fields)
        for field in _DAILY_FIELDS
    }
    hourly_dates, expected_counts = _hourly_dates(hourly, period, timezone)
    hourly_series = {
        field: _optional_series(hourly, field, len(hourly_dates), "hourly", missing_fields)
        for field in _HOURLY_FIELDS
    }

    for field, series in (*daily_series.items(), *hourly_series.items()):
        _validate_weather_series(field, series)

    days = tuple(
        DailyForecast(
            date=day,
            temperature_min_c=_daily_number(daily_series["temperature_2m_min"], index),
            temperature_max_c=_daily_number(daily_series["temperature_2m_max"], index),
            temperature_mean_c=_mean_for_day(
                hourly_dates,
                hourly_series["temperature_2m"],
                day,
            ),
            humidity_mean_pct=_mean_for_day(
                hourly_dates,
                hourly_series["relative_humidity_2m"],
                day,
            ),
            precipitation_sum_mm=_daily_number(daily_series["precipitation_sum"], index),
            precipitation_probability_max_pct=_max_for_day(
                hourly_dates,
                hourly_series["precipitation_probability"],
                day,
            ),
            precipitation_max_hourly_mm=_max_for_day(
                hourly_dates,
                hourly_series["precipitation"],
                day,
            ),
            wind_max_kmh=_daily_number(daily_series["wind_speed_10m_max"], index),
            wind_gust_max_kmh=_daily_number(daily_series["wind_gusts_10m_max"], index),
            weather_code=_daily_integer(daily_series["weather_code"], index),
        )
        for index, day in enumerate(dates)
    )
    for day in days:
        if (
            day.temperature_min_c is not None
            and day.temperature_max_c is not None
            and day.temperature_min_c > day.temperature_max_c
        ):
            raise WeatherDataInvalid("minimum temperature exceeds maximum")
    for day in days:
        for field in day.__dataclass_fields__:
            if field != "date" and getattr(day, field) is None:
                missing_fields.append(f"days.{day.date.isoformat()}.{field}")
        temperatures = _values_for_day(hourly_dates, hourly_series["temperature_2m"], day.date)
        if len(temperatures) != expected_counts[day.date]:
            missing_fields.append(f"hourly.{day.date.isoformat()}.temperature_2m.coverage")
        precipitation = _values_for_day(hourly_dates, hourly_series["precipitation"], day.date)
        if len(precipitation) != expected_counts[day.date]:
            missing_fields.append(f"hourly.{day.date.isoformat()}.precipitation.coverage")
    return days, tuple(missing_fields)


def _object(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise WeatherDataInvalid(f"{field} must be an object")
    return value


def _daily_dates(daily: Mapping[str, object], period: DatePeriod) -> tuple[date, ...]:
    values = _required_series(daily, "time", "daily")
    dates = tuple(_parse_date(value, "daily.time") for value in values)
    expected = tuple(period.start + timedelta(days=index) for index in range(period.days))
    if dates != expected:
        raise WeatherDataInvalid("daily dates do not match the requested period")
    return dates


def _hourly_dates(
    hourly: Mapping[str, object],
    period: DatePeriod,
    timezone: str,
) -> tuple[tuple[date, ...], dict[date, int]]:
    zone = ZoneInfo(timezone)
    expected: list[datetime] = []
    counts: dict[date, int] = {}
    for index in range(period.days):
        day = period.start + timedelta(days=index)
        instant = datetime.combine(day, datetime.min.time(), zone).astimezone(UTC)
        end = datetime.combine(day + timedelta(days=1), datetime.min.time(), zone).astimezone(UTC)
        counts[day] = 0
        while instant < end:
            expected.append(instant.astimezone(zone).replace(tzinfo=None))
            counts[day] += 1
            instant += timedelta(hours=1)
    values = _required_series(hourly, "time", "hourly")
    parsed = tuple(_parse_hour(value) for value in values)
    # The provider series must be a subsequence of the civil timeline. Repeated
    # local hours are legitimate only when the timezone timeline repeats them.
    position = 0
    for hour in parsed:
        while position < len(expected) and expected[position] != hour:
            position += 1
        if position == len(expected):
            raise WeatherDataInvalid("hourly timestamps do not match the civil timeline")
        position += 1
    return tuple(hour.date() for hour in parsed), counts


def _iana_timezone(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise WeatherDataInvalid(f"{field} must be a valid IANA timezone")
    try:
        ZoneInfo(value)
    except (ValueError, ZoneInfoNotFoundError) as error:
        raise WeatherDataInvalid(f"{field} must be a valid IANA timezone") from error
    return value


def _required_series(
    source: Mapping[str, object],
    field: str,
    section: str,
) -> Sequence[object]:
    value = source.get(field)
    if not isinstance(value, list):
        raise WeatherDataInvalid(f"{section}.{field} must be a list")
    return value


def _optional_series(
    source: Mapping[str, object],
    field: str,
    expected_length: int,
    section: str,
    missing_fields: list[str],
) -> Sequence[object] | None:
    value = source.get(field)
    if value is None:
        missing_fields.append(f"{section}.{field}")
        return None
    if not isinstance(value, list) or len(value) != expected_length:
        raise WeatherDataInvalid(f"{section}.{field} is not aligned with its time series")
    return value


def _parse_date(value: object, field: str) -> date:
    if not isinstance(value, str):
        raise WeatherDataInvalid(f"{field} must contain ISO dates")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise WeatherDataInvalid(f"{field} must contain ISO dates") from error


def _parse_hour(value: object) -> datetime:
    if not isinstance(value, str):
        raise WeatherDataInvalid("hourly.time must contain ISO datetimes")
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise WeatherDataInvalid("hourly.time must contain ISO datetimes") from error


def _daily_number(series: Sequence[object] | None, index: int) -> float | None:
    if series is None:
        return None
    return _number_or_none(series[index])


def _daily_integer(series: Sequence[object] | None, index: int) -> int | None:
    if series is None:
        return None
    value = series[index]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise WeatherDataInvalid("daily.weather_code must contain integers")
    return value


def _mean_for_day(
    hourly_dates: Sequence[date],
    series: Sequence[object] | None,
    day: date,
) -> float | None:
    values = _values_for_day(hourly_dates, series, day)
    if not values:
        return None
    return sum(values) / len(values)


def _max_for_day(
    hourly_dates: Sequence[date],
    series: Sequence[object] | None,
    day: date,
) -> float | None:
    values = _values_for_day(hourly_dates, series, day)
    if not values:
        return None
    return max(values)


def _values_for_day(
    hourly_dates: Sequence[date],
    series: Sequence[object] | None,
    day: date,
) -> list[float]:
    if series is None:
        return []
    values: list[float] = []
    for hourly_date, value in zip(hourly_dates, series, strict=True):
        parsed = _number_or_none(value)
        if hourly_date == day and parsed is not None:
            values.append(parsed)
    return values


def _number_or_none(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise WeatherDataInvalid("weather series must contain numbers or null")
    number = float(value)
    if not isfinite(number):
        raise WeatherDataInvalid("weather values must be finite")
    return number


def _validate_weather_series(field: str, series: Sequence[object] | None) -> None:
    if series is None:
        return
    for raw in series:
        value = _number_or_none(raw)
        if value is None:
            continue
        if ("probability" in field or "humidity" in field) and not 0 <= value <= 100:
            raise WeatherDataInvalid("percentage must be between zero and one hundred")
        if field.startswith(("precipitation", "wind_")) and value < 0:
            raise WeatherDataInvalid("precipitation and wind must not be negative")
