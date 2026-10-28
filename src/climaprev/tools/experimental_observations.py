"""Versioned multivariable observations without changing the legacy CSV importer.

INMET describes automatic dry-bulb temperature as a previous-hour mean:
https://portal.inmet.gov.br/glossario/nublado
It must not silently become a model's instantaneous temperature.
"""

import csv
import hashlib
import io
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

from climaprev.tools.experimental_normalization import Measurement, validate_measurements
from climaprev.tools.inmet_observations import _label, _number, parse_station_csv

_EXTRA_FIELDS = {
    "temperature_c": ("TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)", "°C",
                      "observed_previous_hour_mean", timedelta(hours=1), 1.0),
    "wind_kmh": ("VENTO, VELOCIDADE HORARIA (m/s)", "km/h",
                 "observed_previous_10_minute_mean", timedelta(minutes=10), 3.6),
    "gust_kmh": ("VENTO, RAJADA MAXIMA (m/s)", "km/h",
                 "observed_previous_hour_max", timedelta(hours=1), 3.6),
    "humidity_pct": ("UMIDADE RELATIVA DO AR, HORARIA (%)", "%",
                     "observed_hourly_humidity", timedelta(hours=1), 1.0),
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
