"""Explicit synthetic protocol, never an approval or a real campaign."""

from datetime import UTC, datetime, timedelta
from typing import Any

from climaprev.tools.historical_experiment import digest


def protocol_fixture() -> dict[str, Any]:
    protocol = {
        "schema": "climaprev-experiment-protocol-v1", "id": "synthetic",
        "code_version": "synthetic-revision",
        "stations": [{"code": "SYN", "name": "Synthetic", "latitude": 0.0,
                      "longitude": 0.0, "timezone": "UTC"}],
        "variables": [{"name": "precipitation_mm", "unit": "mm",
                       "semantics": "previous_hour_sum", "aggregation": "sum"}],
        "models": ["operational-baseline", "gfs_global"],
        "slots": ["2030-01-01T00:00:00+00:00"], "horizons": [1, 3, 7],
        "slot_window_minutes": 30, "provider_daily_call_limit": 30,
        "splits": {"adjustment": {"start": "2029-01-01", "end": "2029-03-31"},
                   "validation": {"start": "2029-04-01", "end": "2029-06-30"},
                   "test": {"start": "2030-01-01", "end": "2030-12-31"}},
        "criteria": {},
    }
    return {"protocol": protocol, "sha256": digest(protocol)}


def station_csv(extra_headers: list[str], extra_rows: list[list[str]]) -> bytes:
    text = ("ESTACAO:;Synthetic\nCODIGO (WMO):;SYN\nLATITUDE:;0\nLONGITUDE:;0\nALTITUDE:;10\n"
            "Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);VENTO, RAJADA MAXIMA (m/s);"
            "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C);"
            "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)")
    text += (";" + ";".join(extra_headers) if extra_headers else "") + "\n"
    for index, values in enumerate(extra_rows, 1):
        endpoint = datetime(2030, 1, 1, tzinfo=UTC) + timedelta(hours=index)
        text += f"{endpoint:%Y/%m/%d};{endpoint:%H%M} UTC;0;10;30;-10"
        text += (";" + ";".join(values) if values else "") + "\n"
    return text.encode()


def approval_fixture(envelope: dict[str, Any], gate: str = "E1") -> dict[str, Any]:
    return {"gate": gate, "protocol_sha256": envelope["sha256"], "reviewer": "synthetic-reviewer",
            "recorded_at": "2026-10-28T00:00:00+00:00", "reference": "synthetic-test-only"}
