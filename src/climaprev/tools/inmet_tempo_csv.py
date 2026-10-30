"""Explicit adapter for official TEMPO exports; preserves the frozen annual importer."""

import csv
import hashlib
import io
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from climaprev.tools.historical_experiment import digest
from climaprev.tools.inmet_observations import MAX_BYTES, _number, parse_station_csv

_FIELDS = {
    "Chuva (mm)": "PRECIPITAÇÃO TOTAL, HORÁRIO (mm)",
    "Raj. Vento (m/s)": "VENTO, RAJADA MAXIMA (m/s)",
    "Temp. Max. (C)": "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)",
    "Temp. Min. (C)": "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)",
    "Umi. Ins. (%)": "UMIDADE RELATIVA DO AR, HORARIA (%)",
}


@dataclass(frozen=True, slots=True)
class TempoImport:
    csv: bytes
    provenance: dict[str, Any]


def convert_tempo_csv(
    raw: bytes, *, station: dict[str, Any], source_url: str,
    displayed_station: str, retrieved_at: datetime,
) -> TempoImport:
    """Bind an identity-free export to an explicit catalogue/UI observation.

    Binding is a caller declaration, not provider authentication. Source bytes
    must be archived separately. No instantaneous temperature is manufactured.
    Only entirely blank future weather rows may be omitted, with a count.
    """
    code = station["CD_ESTACAO"]
    if (not isinstance(code, str) or not re.fullmatch(r"A\d{3}", code)
            or source_url != f"https://tempo.inmet.gov.br/TabelaEstacoes/{code}"
            or not displayed_station.strip().endswith(f" {code}")
            or retrieved_at.utcoffset() is None or len(raw) > MAX_BYTES):
        raise ValueError("explicit station binding, bounded CSV and aware retrieval time required")
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig")), delimiter=";")
    header = next(reader, [])
    if (header[:2] != ["Data", "Hora (UTC)"] or len(set(header)) != len(header)
            or any(field not in header for field in _FIELDS)):
        raise ValueError("unexpected or ambiguous TEMPO CSV columns/units")
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\n")
    for key, value in (
        ("CODIGO (WMO):", code), ("ESTACAO:", station["DC_NOME"]),
        ("LATITUDE:", station["VL_LATITUDE"]), ("LONGITUDE:", station["VL_LONGITUDE"]),
        ("ALTITUDE:", station["VL_ALTITUDE"]),
    ):
        writer.writerow([key, value])
    writer.writerow(["Data", "Hora UTC", *_FIELDS.values()])
    seen = set()
    imported, future_blank = 0, 0
    for row in reader:
        if not row or not any(cell.strip() for cell in row):
            continue
        if len(row) != len(header) or not re.fullmatch(r"\d{2}00", row[1]):
            raise ValueError("invalid TEMPO row width or UTC hour")
        stamp = datetime.strptime(f"{row[0]} {row[1]}", "%d/%m/%Y %H%M").replace(tzinfo=UTC)
        if stamp in seen:
            raise ValueError("duplicate TEMPO timestamp")
        seen.add(stamp)
        if stamp > retrieved_at:
            if any(cell.strip() for cell in row[2:]):
                raise ValueError("future TEMPO row contains weather values")
            future_blank += 1
            continue
        values = [row[header.index(field)] for field in _FIELDS]
        humidity = _number(values[-1])
        if humidity is not None and not 0 <= humidity <= 100:
            raise ValueError("invalid observed humidity")
        writer.writerow([stamp.date().isoformat(), stamp.strftime("%H%M") + " UTC", *values])
        imported += 1
    normalized = output.getvalue().encode("utf-8")
    parse_station_csv(normalized, expected_station=code)
    return TempoImport(normalized, {
        "schema": "climaprev-tempo-csv-conversion-v1", "station": code,
        "source_url": source_url, "displayed_station": displayed_station,
        "retrieved_at": retrieved_at.astimezone(UTC).isoformat(),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "normalized_sha256": hashlib.sha256(normalized).hexdigest(),
        "catalogue_station_sha256": digest(station),
        "rows_imported": imported, "blank_future_rows_omitted": future_blank,
        "field_mapping": _FIELDS,
        "identity_basis": "explicit_UI_and_catalogue_binding_not_embedded_in_export",
        "temperature_instant_imported": False,
        "scientific_approval": False, "promotion_allowed": False,
    })
