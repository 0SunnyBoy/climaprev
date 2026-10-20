"""Audit saved precipitation interval boundaries without changing experimental labels."""

import argparse
import json
from datetime import UTC, date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.models import DatePeriod
from climaprev.tools.historical_data import normalize_hourly
from climaprev.tools.historical_experiment import load_snapshot


def audit_snapshot(dataset: dict[str, Any]) -> dict[str, Any]:
    """Contrast timestamp-date totals with complete preceding-hour civil intervals.

    ISO values from the provider use the supplied fixed UTC offset.
    Missing boundary hours produce null, never a partial total.
    """
    config = dataset["configuration"]
    period = DatePeriod(date.fromisoformat(config["start"]), date.fromisoformat(config["end"]))
    zone = ZoneInfo(config["timezone"])
    sources: dict[str, Any] = {}
    for name in ("forecast", "observed"):
        payload = dataset[name]
        suffix = f"_previous_day{config['lead_days']}" if name == "forecast" else ""
        # Retain the experiment's input validation and nominal daily convention.
        expanded = normalize_hourly(
            payload, DatePeriod(period.start, period.end + timedelta(days=1)), suffix=suffix,
        )
        nominal = {day: checked for day, checked in expanded.items() if day <= period.end}
        hourly = payload["hourly"]
        fixed_zone = timezone(timedelta(seconds=payload["utc_offset_seconds"]))
        values: dict[datetime, float | None] = {}
        for raw, value in zip(hourly["time"], hourly[f"precipitation{suffix}"], strict=True):
            if isinstance(raw, str):
                stamp = datetime.fromisoformat(raw)
                if stamp.tzinfo is None:
                    stamp = stamp.replace(tzinfo=fixed_zone)
                stamp = stamp.astimezone(UTC)
            else:
                raise TypeError("this snapshot audit requires ISO timestamps")
            if stamp in values:
                raise ValueError("duplicate precipitation instant")
            values[stamp] = value
        days = []
        for day, checked in nominal.items():
            start = datetime.combine(day, time.min, zone).astimezone(UTC)
            end = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC)
            cursor = start + timedelta(hours=1)
            expected = []
            while cursor <= end:
                expected.append(cursor)
                cursor += timedelta(hours=1)
            complete = all(values.get(stamp) is not None for stamp in expected)
            interval_total = round(sum(
                value for stamp in expected if (value := values.get(stamp)) is not None
            ), 6) if complete else None
            days.append({
                "date": day.isoformat(), "expected_interval_hours": len(expected),
                "missing_interval_endpoints": [stamp.isoformat() for stamp in expected
                                               if values.get(stamp) is None],
                "timestamp_date_total_mm": checked.forecast.precipitation_sum_mm
                if checked.eligible["rain_daily"] else None,
                "civil_preceding_hour_total_mm": interval_total,
                "civil_preceding_hour_max_mm": max(
                    value for stamp in expected if (value := values.get(stamp)) is not None
                ) if complete else None,
            })
        nominal_totals = [checked.forecast.precipitation_sum_mm
                          if checked.eligible["rain_daily"] else None
                          for checked in nominal.values()]
        sources[name] = {
            "grid_latitude": payload["latitude"], "grid_longitude": payload["longitude"],
            "elevation_m": payload.get("elevation"),
            "timestamp_date_total_mm": round(sum(value for value in nominal_totals
                                                 if value is not None), 6)
            if all(value is not None for value in nominal_totals) else None,
            "days": days,
        }
    return {
        "schema": "climaprev-interval-audit-v1", "configuration": config,
        "sources": sources, "decision": "audit_only_labels_unchanged",
        "limitations": [
            "Grid values are not station measurements.",
            "Elevation metadata does not establish native grid terrain equivalence.",
            "Civil interval comparison requires next-day midnight endpoint.",
            "Original experiment labels retain their timestamp-date convention.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_snapshot(load_snapshot(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)
                           + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
