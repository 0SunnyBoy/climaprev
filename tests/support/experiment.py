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


def station_csv(
    extra_headers: list[str], extra_rows: list[list[str]], *, start: datetime | None = None,
) -> bytes:
    text = ("ESTACAO:;Synthetic\nCODIGO (WMO):;SYN\nLATITUDE:;0\nLONGITUDE:;0\nALTITUDE:;10\n"
            "Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);VENTO, RAJADA MAXIMA (m/s);"
            "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C);"
            "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)")
    text += (";" + ";".join(extra_headers) if extra_headers else "") + "\n"
    for index, values in enumerate(extra_rows, 1):
        endpoint = (start or datetime(2030, 1, 1, tzinfo=UTC)) + timedelta(hours=index)
        text += f"{endpoint:%Y/%m/%d};{endpoint:%H%M} UTC;0;10;30;-10"
        text += (";" + ";".join(values) if values else "") + "\n"
    return text.encode()


def approval_fixture(envelope: dict[str, Any], gate: str = "E1") -> dict[str, Any]:
    return {"gate": gate, "protocol_sha256": envelope["sha256"], "reviewer": "synthetic-reviewer",
            "recorded_at": "2026-10-28T00:00:00+00:00", "reference": "synthetic-test-only"}


def variable_report(
    model: str, predictions: list[float | None], observations: list[float | None],
    *, variable: str = "precipitation_mm", unit: str = "mm", aggregation: str = "sum",
) -> dict[str, Any]:
    slot = datetime(2029, 12, 31, tzinfo=UTC)
    rows = []
    for index, (predicted, observed) in enumerate(zip(predictions, observations, strict=True)):
        start = datetime(2030, 1, 1, tzinfo=UTC) + timedelta(days=index)
        rows.append({"date": start.date().isoformat(), "start_utc": start.isoformat(),
                     "end_utc": (start + timedelta(days=1)).isoformat(),
                     "forecast": predicted, "observed": observed, "exclusions": [],
                     "eligible_exploratory": True, "eligible_confirmatory": True,
                     "comparable_as_identical_measurement": True})
    return {"schema": "climaprev-variable-pairs-v1", "model": model, "variable": variable,
            "unit": unit, "aggregation": aggregation,
            "forecast_semantics": "previous_hour_sum", "observed_semantics": "observed_previous_hour_sum",
            "station": {"code": "SYN", "latitude": 0, "longitude": 0},
            "location": {"name": "Synthetic", "latitude": 0, "longitude": 0,
                         "timezone": "UTC", "source": "fixture"},
            "source_sha256": "synthetic-common-observation", "source_field": "synthetic-field",
            "collected_at": (slot + timedelta(minutes=5)).isoformat(),
            "collection_slot": slot.isoformat(),
            "collection_deadline": (slot + timedelta(minutes=30)).isoformat(),
            "run_evidence": None, "rows": rows}


def independent_evaluation_fixture(protocol: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Run a real evaluator on fabricated weather, with a clearly synthetic E2 record."""
    from climaprev.tools.historical_experiment import evaluate_frozen_test, snapshot

    times = [f"2030-01-01T{hour:02d}:00" for hour in range(24)]
    def payload(suffix: str, gust: float) -> dict[str, Any]:
        return {"timezone": "UTC", "hourly_units": {"temperature_2m" + suffix: "°C",
                "precipitation" + suffix: "mm", "wind_gusts_10m" + suffix: "km/h"},
                "hourly": {"time": times, "temperature_2m" + suffix: [25] * 24,
                           "precipitation" + suffix: [0] * 24, "wind_gusts_10m" + suffix: [gust] * 24}}
    data = snapshot({"latitude": 0.0, "longitude": 0.0, "start": "2030-01-01", "end": "2030-01-01",
                     "lead_days": 1, "minimum_coverage": 1.0, "forecast_model": "gfs_global",
                     "observed_model": "era5"}, payload("_previous_day1", 40), payload("", 70), {},
                    collected_at=datetime(2030, 2, 1, tzinfo=UTC))
    return evaluate_frozen_test(protocol, candidate, loader=lambda: [data],
                                frozen_protocol_sha256=protocol["sha256"],
                                frozen_candidate_sha256=candidate["sha256"],
                                approvals=[approval_fixture(protocol, "E2")])


def review_fixture(protocol: dict[str, Any], candidate: dict[str, Any], evaluation: dict[str, Any],
                   outcome: str = "promote") -> dict[str, Any]:
    return {"outcome": outcome, "reviewer": "synthetic-reviewer", "reference": "synthetic-only",
            "recorded_at": "2030-02-01T00:00:00+00:00", "protocol_sha256": protocol["sha256"],
            "candidate_sha256": candidate["sha256"], "evaluation_sha256": digest(evaluation)}
