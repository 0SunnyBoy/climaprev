"""Import a local INMET automatic-station CSV into a quality-aware diagnostic report."""

import argparse
import csv
import hashlib
import io
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from math import isfinite
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from climaprev.domain.models import DatePeriod

MAX_BYTES = 32 * 1024 * 1024
CONVENTION = "civil-day-preceding-hour-v1"


def _label(value: str) -> str:
    plain = "".join(char for char in unicodedata.normalize("NFKD", value)
                    if not unicodedata.combining(char))
    return " ".join(plain.strip().upper().split())


_HEADERS = {
    "rain_mm": {"PRECIPITACAO TOTAL, HORARIO (MM)"},
    "gust_kmh": {"VENTO, RAJADA MAXIMA (M/S)"},
    "temperature_max_c": {"TEMPERATURA MAXIMA NA HORA ANT. (AUT) (°C)"},
    "temperature_min_c": {"TEMPERATURA MINIMA NA HORA ANT. (AUT) (°C)"},
}


@dataclass(frozen=True, slots=True)
class StationHour:
    endpoint: datetime
    rain_mm: float | None
    gust_kmh: float | None
    temperature_max_c: float | None
    temperature_min_c: float | None


def _number(value: str) -> float | None:
    if not value.strip():
        return None
    number = float(value.strip().replace(",", "."))
    if not isfinite(number):
        raise ValueError("INMET values must be finite")
    return None if number == -9999 else number


def parse_station_csv(raw: bytes, *, expected_station: str) -> tuple[dict[str, Any], list[StationHour]]:
    """Fail closed on unknown columns/units, identity mismatch or duplicate hours.

    This accepts the annual automatic-station semicolon CSV layout. It does not
    infer station identity, units or timezone from the filename.
    """
    if len(raw) > MAX_BYTES:
        raise ValueError("INMET CSV exceeds 32 MiB")
    try:
        text = raw.decode("utf-8-sig")
        encoding = "utf-8-sig"
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
        encoding = "cp1252"
    reader = csv.reader(io.StringIO(text), delimiter=";")
    metadata: dict[str, str] = {}
    for header in reader:
        if not header or not any(cell.strip() for cell in header):
            continue
        if _label(header[0]) in ("DATA", "DATA (YYYY-MM-DD)"):
            break
        key = _label(header[0]).rstrip(":")
        if key in metadata or len(header) < 2:
            raise ValueError("invalid or duplicate INMET metadata")
        metadata[key] = header[1].strip()
    else:
        raise ValueError("INMET data header not found")
    code = metadata.get("CODIGO (WMO)", "").upper()
    if not code or code != expected_station.strip().upper():
        raise ValueError("INMET station identity differs from expected station")
    station: dict[str, Any] = {"code": code, "name": metadata.get("ESTACAO", ""),
                               "encoding": encoding, "raw_metadata": metadata}
    if not station["name"]:
        raise ValueError("INMET station name is missing")
    for key, bound in (("latitude", 90), ("longitude", 180), ("altitude", None)):
        value = _number(metadata.get(key.upper(), ""))
        if value is None or (bound is not None and not -bound <= value <= bound):
            raise ValueError(f"invalid station {key}")
        station[key] = value
    labels = [_label(cell) for cell in header]
    if len(labels) < 2 or labels[1] != "HORA UTC":
        raise ValueError("INMET hour column must explicitly declare UTC")
    indexes: dict[str, int] = {}
    for field, accepted in _HEADERS.items():
        matches = [index for index, label in enumerate(labels) if label in accepted]
        if len(matches) != 1:
            raise ValueError(f"missing, ambiguous or unsupported units for {field}")
        indexes[field] = matches[0]
    hours = []
    seen = set()
    for row in reader:
        if not row or not any(cell.strip() for cell in row):
            continue
        if len(row) != len(header):
            raise ValueError("INMET row width differs from header")
        day = date.fromisoformat(row[0].strip().replace("/", "-"))
        clock = row[1].strip().upper()
        match = re.fullmatch(r"(\d{2}):?(\d{2})(?: UTC)?", clock)
        if match is None or match[2] != "00":
            raise ValueError("INMET endpoint must be aligned to a UTC hour")
        endpoint = datetime.combine(day, time(int(match[1])), UTC)
        if endpoint in seen:
            raise ValueError("duplicate INMET UTC endpoint")
        seen.add(endpoint)
        values = {field: _number(row[index]) for field, index in indexes.items()}
        for field in ("rain_mm", "gust_kmh"):
            value = values[field]
            if value is not None and value < 0:
                raise ValueError("INMET rain and gust must not be negative")
        gust = values["gust_kmh"]
        values["gust_kmh"] = gust * 3.6 if gust is not None else None
        tmin, tmax = values["temperature_min_c"], values["temperature_max_c"]
        if tmin is not None and tmax is not None and tmin > tmax:
            raise ValueError("INMET minimum temperature exceeds maximum")
        hours.append(StationHour(endpoint=endpoint, **values))
    if not hours:
        raise ValueError("INMET CSV has no observations")
    return station, sorted(hours, key=lambda hour: hour.endpoint)


def import_station(raw: bytes, *, expected_station: str, period: DatePeriod,
                   timezone: str) -> dict[str, Any]:
    station, hours = parse_station_csv(raw, expected_station=expected_station)
    if period.days > 366:
        raise ValueError("station diagnostic is limited to 366 days per report")
    zone = ZoneInfo(timezone)
    by_endpoint = {hour.endpoint: hour for hour in hours}
    days = []
    for index in range(period.days):
        day = period.start + timedelta(days=index)
        start = datetime.combine(day, time.min, zone).astimezone(UTC)
        end = datetime.combine(day + timedelta(days=1), time.min, zone).astimezone(UTC)
        cursor = start + timedelta(hours=1)
        endpoints = []
        while cursor <= end:
            endpoints.append(cursor)
            cursor += timedelta(hours=1)
        fields: dict[str, Any] = {}
        for field in _HEADERS:
            missing = [stamp for stamp in endpoints
                       if stamp not in by_endpoint or getattr(by_endpoint[stamp], field) is None]
            valid = [getattr(by_endpoint[stamp], field) for stamp in endpoints
                     if stamp in by_endpoint and getattr(by_endpoint[stamp], field) is not None]
            fields[field] = {
                "eligible": not missing, "valid_hours": len(valid),
                "missing_endpoints_utc": [stamp.isoformat() for stamp in missing],
                "value": None if missing else round(
                    sum(valid) if field == "rain_mm" else
                    min(valid) if field == "temperature_min_c" else max(valid), 6),
            }
            if field == "rain_mm":
                fields[field]["max_hourly_mm"] = None if missing else max(valid)
        days.append({"date": day.isoformat(), "expected_hours": len(endpoints), "fields": fields})
    return {
        "schema": "climaprev-inmet-observations-v1", "convention": CONVENTION,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "importer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "station": station, "timezone": timezone,
        "period": {"start": period.start.isoformat(), "end": period.end.isoformat()},
        "source_rows": len(hours), "days": days,
        "units": {"rain_mm": "mm", "gust_kmh": "km/h",
                  "temperature_max_c": "°C", "temperature_min_c": "°C"},
        "decision": "diagnostic_only_not_approved",
        "limitations": ["CSV integrity does not prove authenticity or sensor quality.",
                        "Station representativeness and forecast alignment require review.",
                        "Temperature fields are preceding-hour extrema, not instantaneous samples."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--station", required=True)
    parser.add_argument("--timezone", required=True)
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.input.stat().st_size > MAX_BYTES:
            raise ValueError("INMET CSV exceeds 32 MiB")
        report = import_station(args.input.read_bytes(), expected_station=args.station,
                                period=DatePeriod(args.start, args.end), timezone=args.timezone)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    except (ValueError, OSError, KeyError, UnicodeError, csv.Error) as error:
        parser.exit(2, f"INMET import failed: {error}\n")


if __name__ == "__main__":
    main()
