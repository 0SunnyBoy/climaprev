"""Additional station variables without modifying the frozen historical importer."""

import csv
import io
from collections.abc import Sequence
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from typing import Any

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_normalization import Measurement
from climaprev.tools.inmet_observations import _label, _number, parse_station_csv

_UNITS = {"precipitation_mm": "mm", "gust_kmh": "km/h", "temperature_c": "°C", "humidity_pct": "%"}


def station_variable_measurements(
    raw: bytes, *, station: str,
) -> tuple[dict[str, Any], list[Measurement]]:
    """Read declared CSV fields; instrument/height equivalence is not certified.

    The preceding-hour convention is inherited from the existing importer.
    Hourly air-temperature/humidity fields are exposed as declared endpoint
    samples; sustained wind is withheld until averaging semantics are verified.
    """
    metadata, hours = parse_station_csv(raw, expected_station=station)
    measurements = []
    for hour in hours:
        start = hour.endpoint - timedelta(hours=1)
        for variable, value, unit, semantics in (
            ("precipitation_mm", hour.rain_mm, "mm", "observed_previous_hour_sum"),
            ("gust_kmh", hour.gust_kmh, "km/h", "observed_previous_hour_max"),
            ("temperature_c", hour.temperature_max_c, "°C", "observed_previous_hour_max"),
            ("temperature_c", hour.temperature_min_c, "°C", "observed_previous_hour_min"),
        ):
            measurements.append(Measurement(variable, start, hour.endpoint, value, unit, semantics))
    reader = csv.reader(io.StringIO(raw.decode(metadata["encoding"])), delimiter=";")
    for header in reader:
        if header and _label(header[0]) in {"DATA", "DATA (YYYY-MM-DD)"}:
            break
    labels = [_label(cell) for cell in header]
    optional = {
        "temperature_c": ("TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)", "°C"),
        "humidity_pct": ("UMIDADE RELATIVA DO AR, HORARIA (%)", "%"),
    }
    selected = {}
    missing = []
    for variable, (label, unit) in optional.items():
        indexes = [i for i, candidate in enumerate(labels) if candidate == label]
        if len(indexes) > 1:
            raise ValueError("ambiguous optional station column")
        if not indexes:
            missing.append(variable)
        else:
            selected[variable] = (indexes[0], unit)
    for row in reader:
        if not row or not any(cell.strip() for cell in row):
            continue
        # Required parser already validated UTC alignment, shape and duplicates.
        day = date.fromisoformat(row[0].strip().replace("/", "-"))
        clock = row[1].strip().split()[0].replace(":", "")
        stamp = datetime.combine(day, time(int(clock[:2])), UTC)
        for variable, (index, unit) in selected.items():
            value = _number(row[index])
            if variable == "humidity_pct" and value is not None and not 0 <= value <= 100:
                raise ValueError("observed humidity outside zero to 100")
            measurements.append(Measurement(variable, stamp, None, value, unit, "observed_instant"))
    return {**metadata, "optional_fields_missing": missing,
            "instant_semantics_basis": "declared_hourly_endpoint_not_instrument_certification",
            "sustained_wind": "withheld_pending_averaging_equivalence"}, measurements


def qualify_observation_window(
    metadata: dict[str, Any], observations: Sequence[Measurement], location: CanonicalLocation,
    *, start: datetime, end: datetime, checked_at: datetime, min_coverage: float,
) -> dict[str, Any]:
    """Operational coverage only; stale annual data cannot satisfy a recent window."""
    if (any(stamp.utcoffset() is None for stamp in (start, end, checked_at))
            or not start < end <= checked_at or (end - start).total_seconds() % 3600
            or isinstance(min_coverage, bool) or not 0 < min_coverage <= 1):
        raise ValueError("aware completed hourly window and positive coverage required")
    expected = int((end - start).total_seconds() // 3600)
    matching = all(abs(metadata[field] - getattr(location, field)) <= 0.0001
                   for field in ("latitude", "longitude"))
    indexed = {}
    for item in observations:
        if item.start.utcoffset() is None or (item.end and item.end.utcoffset() is None):
            raise ValueError("aware observations required")
        value = item.value
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value)
            or (item.variable != "temperature_c" and value < 0)
            or (item.variable == "humidity_pct" and value > 100)
        ):
            raise ValueError("invalid observation value")
        key = (item.variable, item.semantics, item.start.astimezone(UTC),
               item.end.astimezone(UTC) if item.end else None)
        if key in indexed:
            raise ValueError("duplicate observation identity")
        indexed[key] = item
    coverage = {}
    for variable, semantics, interval in (
        ("precipitation_mm", "observed_previous_hour_sum", True),
        ("gust_kmh", "observed_previous_hour_max", True),
        ("temperature_c", "observed_instant", False),
        ("humidity_pct", "observed_instant", False),
    ):
        valid = 0
        cursor = start.astimezone(UTC)
        for _ in range(expected):
            key = (variable, semantics, cursor, cursor + timedelta(hours=1) if interval else None)
            found = indexed.get(key)
            valid += found is not None and found.value is not None and found.unit == _UNITS[variable]
            cursor += timedelta(hours=1)
        coverage[variable] = {"expected_hours": expected, "valid_hours": valid,
                              "coverage": valid / expected}
    return {
        "schema": "climaprev-observation-window-readiness-v1", "station": metadata["code"],
        "start_utc": start.astimezone(UTC).isoformat(), "end_utc": end.astimezone(UTC).isoformat(),
        "station_version_matches": matching, "variables": coverage,
        "technical_pairing_ready": matching and all(
            row["coverage"] >= min_coverage for row in coverage.values()),
        "minimum_coverage": min_coverage, "scientific_approval": False,
        "limitation": "Coverage/metadata are not certification of sensor calibration or representativeness.",
    }
