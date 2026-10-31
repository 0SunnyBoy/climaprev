"""Describe daily peak times without shifting dates or optimizing event alignment."""

from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo


def daily_profile(
    series: dict[datetime, float | None], day: date, zone: str,
    *, preceding: bool, minimum: bool = False,
) -> dict[str, Any]:
    local = ZoneInfo(zone)
    start = datetime.combine(day, time.min, local).astimezone(UTC)
    end = datetime.combine(day + timedelta(days=1), time.min, local).astimezone(UTC)
    cursor = start + timedelta(hours=1) if preceding else start
    expected = []
    while cursor <= end if preceding else cursor < end:
        expected.append(cursor)
        cursor += timedelta(hours=1)
    missing = [stamp for stamp in expected if series.get(stamp) is None]
    samples = [{"utc": stamp.isoformat(), "local": stamp.astimezone(local).isoformat(),
                "value": series.get(stamp)} for stamp in expected]
    if missing:
        return {"complete": False, "samples": samples, "peak": None, "peak_utc": [],
                "missing_utc": [stamp.isoformat() for stamp in missing], "sum": None}
    values = [float(value) for stamp in expected if (value := series[stamp]) is not None]
    extreme = min(values) if minimum else max(values)
    return {"complete": True, "samples": samples, "peak": extreme,
            "peak_utc": [stamp.isoformat() for stamp in expected if series[stamp] == extreme],
            "missing_utc": [], "sum": sum(values)}


def nearest_peak_lag(observation: dict[str, Any], model: dict[str, Any]) -> float | None:
    """Nearest tied-peak endpoint separation; neither unique timing nor causation."""
    if not observation["peak_utc"] or not model["peak_utc"]:
        return None
    return min(abs((datetime.fromisoformat(left) - datetime.fromisoformat(right)).total_seconds())
               / 3600 for left in observation["peak_utc"] for right in model["peak_utc"])
