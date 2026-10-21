"""Validated cache representation; format and rejection rules are unchanged."""

from collections.abc import Mapping
from dataclasses import replace
from datetime import date, datetime, timedelta
from typing import Literal, cast

from climaprev.application.query_result import OfficialAlertsResult
from climaprev.domain.models import (
    CanonicalLocation,
    DailyForecast,
    DatePeriod,
    NormalizedForecast,
    OfficialAlert,
)


def encode_alerts(result: OfficialAlertsResult) -> dict[str, object]:
    return {
        "status": result.status,
        "items": [
            {
                "source": alert.source,
                "event": alert.event,
                "severity": alert.severity,
                "effective_at": alert.effective_at.isoformat(),
                "expires_at": alert.expires_at.isoformat() if alert.expires_at else None,
                "geographic_scope": alert.geographic_scope,
                "source_url": alert.source_url,
            }
            for alert in result.items
        ],
    }


def decode_alerts(value: object) -> OfficialAlertsResult | None:
    if not isinstance(value, Mapping):
        return None
    status = value.get("status")
    items = value.get("items")
    if status not in {"available", "unavailable"} or not isinstance(items, list):
        return None
    if status == "unavailable" and items:
        return None
    alerts: list[OfficialAlert] = []
    for item in items:
        if not isinstance(item, Mapping):
            return None
        source = _string(item.get("source"))
        event = _string(item.get("event"))
        severity = _string(item.get("severity"))
        effective_at = _datetime(item.get("effective_at"))
        expires_at_value = item.get("expires_at")
        expires_at = None if expires_at_value is None else _datetime(expires_at_value)
        geographic_scope = _string(item.get("geographic_scope"))
        source_url_value = item.get("source_url")
        source_url = None if source_url_value is None else _string(source_url_value)
        if (
            source is None
            or event is None
            or severity is None
            or effective_at is None
            or expires_at is None
            or (expires_at is not None and effective_at is not None and expires_at <= effective_at)
            or (expires_at_value is not None and expires_at is None)
            or geographic_scope is None
            or (source_url_value is not None and source_url is None)
        ):
            return None
        alerts.append(
            OfficialAlert(
                source=source,
                event=event,
                severity=severity,
                effective_at=effective_at,
                expires_at=expires_at,
                geographic_scope=geographic_scope,
                source_url=source_url,
            )
        )
    return OfficialAlertsResult(status=cast(Literal["available", "unavailable"], status), items=tuple(alerts))


def encode_location(location: CanonicalLocation) -> dict[str, object]:
    return {
        "name": location.name,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "timezone": location.timezone,
        "source": location.source,
    }


def decode_location(value: object) -> CanonicalLocation | None:
    if not isinstance(value, Mapping):
        return None
    name = _string(value.get("name"))
    latitude = _number(value.get("latitude"))
    longitude = _number(value.get("longitude"))
    timezone = _string(value.get("timezone"))
    source = _string(value.get("source"))
    if name is None or latitude is None or longitude is None or timezone is None or source is None:
        return None
    return CanonicalLocation(
        name=name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        source=source,
    )


def encode_forecast(forecast: NormalizedForecast) -> dict[str, object]:
    return {
        "location": encode_location(forecast.location),
        "period": {
            "start": forecast.period.start.isoformat(),
            "end": forecast.period.end.isoformat(),
        },
        "days": [
            {
                "date": day.date.isoformat(),
                "temperature_min_c": day.temperature_min_c,
                "temperature_max_c": day.temperature_max_c,
                "temperature_mean_c": day.temperature_mean_c,
                "humidity_mean_pct": day.humidity_mean_pct,
                "precipitation_sum_mm": day.precipitation_sum_mm,
                "precipitation_probability_max_pct": day.precipitation_probability_max_pct,
                "precipitation_max_hourly_mm": day.precipitation_max_hourly_mm,
                "wind_max_kmh": day.wind_max_kmh,
                "wind_gust_max_kmh": day.wind_gust_max_kmh,
                "weather_code": day.weather_code,
            }
            for day in forecast.days
        ],
        "provider": forecast.provider,
        "fetched_at": forecast.fetched_at.isoformat(),
        "is_stale": False,
        "missing_fields": list(forecast.missing_fields),
    }


def decode_forecast(
    value: object,
    expected_location: CanonicalLocation,
    expected_period: DatePeriod,
) -> NormalizedForecast | None:
    if not isinstance(value, Mapping):
        return None
    location = decode_location(value.get("location"))
    period = _period_from_cache(value.get("period"))
    days = _days_from_cache(value.get("days"))
    provider = _string(value.get("provider"))
    fetched_at = _datetime(value.get("fetched_at"))
    missing_fields = _strings(value.get("missing_fields"))
    if not isinstance(value.get("is_stale"), bool):
        return None
    if (
        location is None
        or period is None
        or days is None
        or provider is None
        or fetched_at is None
        or missing_fields is None
    ):
        return None
    expected_days = tuple(period.start + timedelta(days=index) for index in range(period.days))
    if tuple(day.date for day in days) != expected_days:
        return None
    if (location.latitude != expected_location.latitude
            or location.longitude != expected_location.longitude or period != expected_period):
        return None
    return NormalizedForecast(
        location=replace(expected_location, timezone=location.timezone),
        period=period,
        days=days,
        provider=provider,
        fetched_at=fetched_at,
        is_stale=False,
        missing_fields=missing_fields,
    )


def _period_from_cache(value: object) -> DatePeriod | None:
    if not isinstance(value, Mapping):
        return None
    start = _date(value.get("start"))
    end = _date(value.get("end"))
    if start is None or end is None:
        return None
    try:
        return DatePeriod(start=start, end=end)
    except ValueError:
        return None


def _days_from_cache(value: object) -> tuple[DailyForecast, ...] | None:
    if not isinstance(value, list):
        return None
    days: list[DailyForecast] = []
    for item in value:
        if not isinstance(item, Mapping):
            return None
        parsed = _day_from_cache(item)
        if parsed is None:
            return None
        days.append(parsed)
    return tuple(days)


def _day_from_cache(value: Mapping[object, object]) -> DailyForecast | None:
    required_fields = (
        "date",
        "temperature_min_c",
        "temperature_max_c",
        "temperature_mean_c",
        "humidity_mean_pct",
        "precipitation_sum_mm",
        "precipitation_probability_max_pct",
        "precipitation_max_hourly_mm",
        "wind_max_kmh",
        "wind_gust_max_kmh",
        "weather_code",
    )
    if any(field not in value for field in required_fields):
        return None
    day_date = _date(value.get("date"))
    weather_code = _integer_or_none(value.get("weather_code"))
    numbers = {
        key: _number_or_none(value.get(key))
        for key in (
            "temperature_min_c",
            "temperature_max_c",
            "temperature_mean_c",
            "humidity_mean_pct",
            "precipitation_sum_mm",
            "precipitation_probability_max_pct",
            "precipitation_max_hourly_mm",
            "wind_max_kmh",
            "wind_gust_max_kmh",
        )
    }
    if day_date is None or isinstance(weather_code, _InvalidValue):
        return None
    if any(isinstance(number, _InvalidValue) for number in numbers.values()):
        return None
    return DailyForecast(
        date=day_date,
        temperature_min_c=cast(float | None, numbers["temperature_min_c"]),
        temperature_max_c=cast(float | None, numbers["temperature_max_c"]),
        temperature_mean_c=cast(float | None, numbers["temperature_mean_c"]),
        humidity_mean_pct=cast(float | None, numbers["humidity_mean_pct"]),
        precipitation_sum_mm=cast(float | None, numbers["precipitation_sum_mm"]),
        precipitation_probability_max_pct=cast(
            float | None, numbers["precipitation_probability_max_pct"]
        ),
        precipitation_max_hourly_mm=cast(float | None, numbers["precipitation_max_hourly_mm"]),
        wind_max_kmh=cast(float | None, numbers["wind_max_kmh"]),
        wind_gust_max_kmh=cast(float | None, numbers["wind_gust_max_kmh"]),
        weather_code=weather_code,
    )


class _InvalidValue:
    pass


_INVALID = _InvalidValue()


def _string(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


def _number_or_none(value: object) -> float | None | _InvalidValue:
    if value is None:
        return None
    number = _number(value)
    return _INVALID if number is None else number


def _integer_or_none(value: object) -> int | None | _InvalidValue:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        return _INVALID
    return value


def _date(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _datetime(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _strings(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None
    return tuple(value)


