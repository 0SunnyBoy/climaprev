"""Additional station variables without modifying the frozen historical importer."""

import csv
import hashlib
import io
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from typing import Any

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.experimental_normalization import Measurement, validate_measurements
from climaprev.tools.inmet_observations import _label, _number, parse_station_csv

_UNITS = {"precipitation_mm": "mm", "gust_kmh": "km/h", "temperature_c": "°C", "humidity_pct": "%"}


def station_variable_measurements(
    raw: bytes, *, station: str,
) -> tuple[dict[str, Any], list[Measurement]]:
    """Read declared CSV fields; instrument/height equivalence is not certified.

    The preceding-hour convention is inherited from the existing importer.
    INMET's glossary identifies air temperature as a preceding-hour mean.
    Humidity aggregation is not explicit enough to assert an instantaneous
    sample. Wind is withheld: the source's 10-minute mean is not model instant.
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
            semantics = ("observed_previous_hour_mean" if variable == "temperature_c"
                         else "observed_previous_hour_unspecified")
            measurements.append(Measurement(variable, stamp - timedelta(hours=1), stamp,
                                              value, unit, semantics))
    return {**metadata, "optional_fields_missing": missing,
            "semantics_source": "https://portal.inmet.gov.br/glossario/nublado",
            "instantaneous_temperature_observation_available": False,
            "instantaneous_humidity_observation_verified": False,
            "sustained_wind": "withheld_model_instant_vs_observed_10min_mean"}, measurements


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
        ("temperature_c", "observed_previous_hour_mean", True),
        ("humidity_pct", "observed_previous_hour_unspecified", True),
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
        "measurement_coverage_ready": matching and all(
            row["coverage"] >= min_coverage for row in coverage.values()),
        "technical_pairing_ready": False,
        "semantic_blockers": ["temperature_hourly_mean_is_not_model_instant",
                              "humidity_sampling_aggregation_unverified",
                              "wind_10min_mean_is_not_model_instant"],
        "minimum_coverage": min_coverage, "scientific_approval": False,
        "limitation": "Coverage/metadata are not certification of sensor calibration or representativeness.",
    }


_EXTRA_FIELDS = {
    "temperature_c": ("TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)", "°C",
                      "observed_previous_hour_mean", timedelta(hours=1), 1.0),
    "wind_kmh": ("VENTO, VELOCIDADE HORARIA (m/s)", "km/h",
                 "observed_previous_10_minute_mean", timedelta(minutes=10), 3.6),
    "gust_kmh": ("VENTO, RAJADA MAXIMA (m/s)", "km/h",
                 "observed_previous_hour_max", timedelta(hours=1), 3.6),
    "humidity_pct": ("UMIDADE RELATIVA DO AR, HORARIA (%)", "%",
                     "observed_hourly_humidity", timedelta(hours=1), 1.0),
    "precipitation_mm": ("PRECIPITAÇÃO TOTAL, HORÁRIO (mm)", "mm",
                         "observed_previous_hour_sum", timedelta(hours=1), 1.0),
    "temperature_max_c": ("TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)", "°C",
                          "observed_previous_hour_max", timedelta(hours=1), 1.0),
    "temperature_min_c": ("TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)", "°C",
                          "observed_previous_hour_min", timedelta(hours=1), 1.0),
}


def parse_observations(
    raw: bytes, *, expected_station: str, variables: Sequence[str] = ("temperature_c",),
) -> dict[str, Any]:
    if any(variable not in _EXTRA_FIELDS for variable in variables):
        raise ValueError("unsupported observational variable")
    station, _ = parse_station_csv(raw, expected_station=expected_station)
    reader = csv.reader(io.StringIO(raw.decode(station["encoding"])), delimiter=";")
    for header in reader:
        if header and _label(header[0]) in {"DATA", "DATA (YYYY-MM-DD)"}:
            break
    labels = [_label(label) for label in header]
    indexes = {}
    source_fields = {}
    missing = []
    for variable in dict.fromkeys(variables):
        label, unit, semantics, duration, factor = _EXTRA_FIELDS[variable]
        matches = [i for i, name in enumerate(labels) if name == _label(label)]
        if len(matches) > 1:
            raise ValueError("duplicate observational field")
        if not matches:
            missing.append(variable)
        else:
            indexes[variable] = matches[0]
            source_fields[variable] = header[matches[0]]
    measurements = []
    for row in reader:
        if not row or not any(cell.strip() for cell in row):
            continue
        day = date.fromisoformat(row[0].strip().replace("/", "-"))
        endpoint = datetime.combine(day, time(int(row[1].strip()[:2])), UTC)
        for variable, index in indexes.items():
            _, unit, semantics, duration, factor = _EXTRA_FIELDS[variable]
            value = _number(row[index])
            sample = Measurement(variable, endpoint - duration, endpoint,
                                 None if value is None else value * factor, unit, semantics)
            validate_measurements([sample], unit=unit, semantics=semantics)
            measurements.append(asdict(sample))
    measurements.sort(key=lambda sample: (sample["start"], sample["variable"]))
    return {"schema": "climaprev-station-measurements-v1", "station": station,
            "measurements": measurements, "source_fields": source_fields,
            "missing_fields": missing, "source_sha256": hashlib.sha256(raw).hexdigest(),
            "semantics_reference": "https://portal.inmet.gov.br/glossario/nublado",
            "scientific_approval": False}


def _measurement(data: dict[str, Any]) -> Measurement:
    def stamp(value: Any) -> datetime:
        return value if isinstance(value, datetime) else datetime.fromisoformat(value)

    return Measurement(data["variable"], stamp(data["start"]),
                       stamp(data["end"]) if data["end"] is not None else None,
                       data["value"], data["unit"], data["semantics"])


def pair_temperature_instants(
    forecast: list[Measurement], observations: dict[str, Any],
) -> list[dict[str, Any]]:
    """Pair only actual point measurements; hourly station averages stay excluded."""
    predicted = [sample for sample in forecast if sample.variable == "temperature_c"
                 and sample.semantics == "instant"]
    observed = [_measurement(row) for row in observations["measurements"]
                if row["variable"] == "temperature_c" and row["semantics"] == "instant"]
    validate_measurements(predicted, unit="°C", semantics="instant")
    validate_measurements(observed, unit="°C", semantics="instant")
    reference = {sample.start: sample for sample in observed}
    pairs = []
    for sample in sorted(predicted, key=lambda item: item.start):
        match = reference.get(sample.start)
        if match is not None and sample.value is not None and match.value is not None:
            pairs.append({"at_utc": sample.start.astimezone(UTC).isoformat(),
                          "forecast": sample.value, "observed": match.value, "unit": "°C",
                          "source_field": observations["source_fields"]["temperature_c"],
                          "source_sha256": observations["source_sha256"]})
    return pairs
