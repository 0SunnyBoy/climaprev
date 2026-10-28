"""Experimental measurements with explicit intervals; never fabricate hourly rain."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from itertools import pairwise
from math import isfinite
from typing import Any, cast


@dataclass(frozen=True, slots=True)
class Measurement:
    variable: str
    start: datetime
    end: datetime | None
    value: float | None
    unit: str
    semantics: str


def _object(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("expected an experimental JSON object")
    return cast(dict[str, Any], value)


def _number(value: Any, variable: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not isfinite(value):
        raise ValueError("measurement must be finite or null")
    if variable != "temperature_c" and value < 0:
        raise ValueError("negative non-temperature measurement")
    if variable == "humidity_pct" and value > 100:
        raise ValueError("humidity must be between zero and 100")
    return float(value)


def validate_measurements(
    samples: list[Measurement], *, unit: str, semantics: str,
) -> list[Measurement]:
    """Require the declared measurement contract without manufacturing coverage."""
    seen = set()
    for sample in samples:
        if sample.unit != unit or sample.semantics != semantics:
            raise ValueError("measurement contract unit or semantics differ")
        if sample.start.utcoffset() is None or (sample.end is not None
                                               and sample.end.utcoffset() is None):
            raise ValueError("measurement timestamps need UTC offsets")
        if (semantics == "instant" and sample.end is not None
                or semantics != "instant" and (sample.end is None or sample.end <= sample.start)):
            raise ValueError("measurement interval differs from its semantics")
        _number(sample.value, sample.variable)
        key = (sample.variable, sample.start, sample.end)
        if key in seen:
            raise ValueError("duplicate measurement interval")
        seen.add(key)
    return list(samples)


def open_meteo_measurements(payload: dict[str, Any]) -> list[Measurement]:
    hourly, units = _object(payload.get("hourly")), _object(payload.get("hourly_units"))
    times = hourly.get("time")
    if units.get("time") != "unixtime" or not isinstance(times, list) or not times:
        raise ValueError("explicit epoch timestamps are required")
    stamps = []
    for value in times:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError("invalid epoch timestamp")
        stamps.append(datetime.fromtimestamp(value, UTC))
    if any(a >= b for a, b in pairwise(stamps)):
        raise ValueError("timestamps must be strictly increasing")
    result = []
    fields = (
        ("temperature_2m", "temperature_c", "°C", "instant"),
        ("relative_humidity_2m", "humidity_pct", "%", "instant"),
        ("wind_speed_10m", "wind_kmh", "km/h", "instant"),
        ("wind_gusts_10m", "gust_kmh", "km/h", "previous_hour_max"),
        ("precipitation", "precipitation_mm", "mm", "previous_hour_sum"),
    )
    for field, variable, unit, semantics in fields:
        if field not in hourly:
            continue
        values = hourly[field]
        if (units.get(field) != unit or not isinstance(values, list)
                or len(values) != len(stamps)):
            raise ValueError("unexpected unit or inconsistent experimental series")
        for stamp, value in zip(stamps, values, strict=True):
            start = stamp if semantics == "instant" else stamp - timedelta(hours=1)
            result.append(Measurement(variable, start, None if semantics == "instant" else stamp,
                                      _number(value, variable), unit, semantics))
    return result


def met_norway_measurements(payload: dict[str, Any]) -> list[Measurement]:
    properties = _object(payload.get("properties"))
    units = _object(_object(properties.get("meta")).get("units"))
    series = properties.get("timeseries")
    if not isinstance(series, list) or not series:
        raise ValueError("MET Norway timeseries is missing")
    result: list[Measurement] = []
    previous = None
    rain_end: datetime | None = None
    for row in series:
        row = _object(row)
        if not isinstance(row.get("time"), str):
            raise TypeError("MET Norway timestamp is missing")
        stamp = datetime.fromisoformat(row["time"])
        if stamp.utcoffset() is None:
            raise ValueError("MET Norway timestamp needs an offset")
        stamp = stamp.astimezone(UTC)
        if previous is not None and stamp <= previous:
            raise ValueError("timestamps must be strictly increasing")
        previous = stamp
        data = _object(row.get("data"))
        details = _object(_object(data.get("instant", {})).get("details", {}))
        for field, variable, source_unit, unit, factor in (
            ("air_temperature", "temperature_c", "celsius", "°C", 1),
            ("relative_humidity", "humidity_pct", "%", "%", 1),
            ("wind_speed", "wind_kmh", "m/s", "km/h", 3.6),
        ):
            if field not in details:
                continue
            if units.get(field) != source_unit:
                raise ValueError("unexpected MET Norway unit")
            value = _number(details[field], variable)
            result.append(Measurement(variable, stamp, None,
                                      None if value is None else value * factor, unit, "instant"))
        # Gust-period semantics need separate approval; do not pretend they are hourly maxima.
        if rain_end is not None and stamp < rain_end:
            continue
        for hours in (1, 6, 12):
            period = data.get(f"next_{hours}_hours")
            if period is None:
                continue
            detail = _object(_object(period).get("details", {}))
            if "precipitation_amount" not in detail:
                continue
            if units.get("precipitation_amount") != "mm":
                raise ValueError("unexpected MET Norway precipitation unit")
            rain_end = stamp + timedelta(hours=hours)
            result.append(Measurement("precipitation_mm", stamp, rain_end,
                                      _number(detail["precipitation_amount"], "precipitation_mm"),
                                      "mm", f"next_{hours}_hours_sum"))
            break
    return result


def complete_rain_total(
    measurements: list[Measurement], start: datetime, end: datetime,
) -> float | None:
    """Return null for gaps, nulls, overlap or boundary-crossing accumulation."""
    if start.utcoffset() is None or end.utcoffset() is None:
        raise ValueError("rain interval needs timezone-aware bounds")
    start, end = start.astimezone(UTC), end.astimezone(UTC)
    if start >= end:
        raise ValueError("rain interval must be nonempty")
    periods = sorted((m for m in measurements if m.variable == "precipitation_mm"
                      and m.end is not None and m.start < end and m.end > start),
                     key=lambda m: m.start)
    cursor, total = start, 0.0
    for period in periods:
        if (period.start != cursor or period.end is None or period.end > end
                or period.value is None or period.unit != "mm"):
            return None
        total += period.value
        cursor = period.end
    return total if cursor == end else None
