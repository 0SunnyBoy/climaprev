"""Immutable input snapshots and paired offline policy/calibration experiments.

The initial target is explicitly v1-on-reanalysis, not observed disaster impact.
No function in this module performs network requests or promotes a configuration.
"""

import hashlib
import json
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, cast

from climaprev.domain.bias_correction import ForecastCalibration
from climaprev.domain.models import CanonicalLocation, DatePeriod, NormalizedForecast
from climaprev.domain.risk_evaluator import RiskEvaluator
from climaprev.domain.risk_policy import ExperimentalRiskPolicy, RiskPolicy, policy_fingerprint
from climaprev.domain.verification import Level, classify_pairs, numerical_pairs
from climaprev.tools.historical_data import (
    EVENT_FIELDS,
    EVENT_UNITS,
    event_level,
    normalize_hourly,
    payload_timezone,
)

SCHEMA = "climaprev-historical-input-v1"
_MAX_FILE_BYTES = 32 * 1024 * 1024


def algorithm_fingerprints() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1]
    return {
        name: hashlib.sha256((root / name).read_text(encoding="utf-8").encode()).hexdigest()
        for name in (
            "domain/risk_policy.py", "domain/risk_evaluator.py", "domain/bias_correction.py",
            "domain/verification.py", "tools/historical_data.py", "tools/historical_experiment.py",
        )
    }


def digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False, default=_json_value)


def _json_value(value: object) -> str:
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(f"unsupported snapshot value type: {type(value).__name__}")


def _object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("expected a JSON object")
    return cast(dict[str, Any], value)


def read_json(path: Path) -> dict[str, Any]:
    if path.stat().st_size > _MAX_FILE_BYTES:
        raise ValueError("historical input file exceeds size limit")
    return _object(json.loads(path.read_text(encoding="utf-8")))


def snapshot(
    configuration: dict[str, object], forecast: dict[str, object], observed: dict[str, object],
    requests: dict[str, object], *, collected_at: datetime | None = None,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA, "configuration": configuration, "requests": requests,
        "collected_at": (collected_at or datetime.now(UTC)).isoformat(),
        "algorithms_sha256": algorithm_fingerprints(),
        "reference": {
            "kind": "reference-v1-on-reanalysis", "policy": asdict(RiskPolicy()),
            "policy_sha256": policy_fingerprint(RiskPolicy()),
            "limitation": "heuristic agreement; not independent impact validation",
        },
        "forecast": forecast, "observed": observed,
    }


def save_snapshot(path: Path, data: dict[str, Any]) -> str:
    checksum = digest(data)
    envelope = {"sha256": checksum, "dataset": data}
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = load_snapshot(path)
        if digest(existing) != checksum:
            raise ValueError("refusing to replace an existing historical snapshot")
        return checksum
    with path.open("x", encoding="utf-8", newline="\n") as output:
        output.write(canonical_json(envelope) + "\n")
    return checksum


def load_snapshot(path: Path) -> dict[str, Any]:
    envelope = read_json(path)
    data = _object(envelope.get("dataset"))
    if data.get("schema") != SCHEMA or envelope.get("sha256") != digest(data):
        raise ValueError("historical snapshot schema or checksum is invalid")
    return data


def reference_policy(data: dict[str, Any]) -> RiskPolicy:
    reference = _object(data.get("reference"))
    if reference.get("kind") != "reference-v1-on-reanalysis":
        raise ValueError("unsupported observed reference definition")
    parameters = dict(_object(reference.get("policy")))
    if parameters.pop("policy_version", None) != "reference-v1":
        raise ValueError("observed reference must identify reference-v1")
    expected = set(asdict(RiskPolicy())) - {"policy_version"}
    if set(parameters) != expected:
        raise ValueError("observed reference policy fields are incomplete")
    # Reuse strict threshold validation without changing the stored target identity.
    ExperimentalRiskPolicy(**parameters)
    policy = RiskPolicy(**parameters)
    if policy_fingerprint(policy) != reference.get("policy_sha256"):
        raise ValueError("observed reference policy checksum is invalid")
    return policy


def load_candidate(path: Path) -> ExperimentalRiskPolicy:
    data = read_json(path)
    if set(data) != {"policy_version", "thresholds"}:
        raise ValueError("candidate requires policy_version and thresholds only")
    thresholds = _object(data["thresholds"])
    allowed = set(asdict(RiskPolicy())) - {"policy_version"}
    if set(thresholds) != allowed:
        raise ValueError("candidate must explicitly declare all thresholds")
    return ExperimentalRiskPolicy(policy_version=data["policy_version"], **thresholds)


def load_calibration(path: Path) -> ForecastCalibration:
    data = read_json(path)
    if set(data) != set(asdict(ForecastCalibration())):
        raise ValueError("calibration must explicitly declare all profile fields")
    if data.get("enabled") is not True or data.get("profile_version") in ("disabled", "", None):
        raise ValueError("experimental calibration must be enabled and have its own version")
    return ForecastCalibration(**data)


def _normalized(
    day: Any, location: CanonicalLocation, collected_at: datetime,
) -> NormalizedForecast:
    return NormalizedForecast(
        location, DatePeriod(day.forecast.date, day.forecast.date), (day.forecast,),
        "open-meteo-historical", collected_at, False, day.missing_fields,
    )


def evaluate_snapshots(
    datasets: Sequence[dict[str, Any]], *, candidate: ExperimentalRiskPolicy | None = None,
    calibration: ForecastCalibration | None = None, partition: str = "diagnostic",
    protocol: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not datasets:
        raise ValueError("at least one snapshot is required")
    bounds: tuple[date, date] | None = None
    if protocol is not None:
        splits = _object(protocol.get("splits"))
        previous_end: date | None = None
        for name in ("adjustment", "validation", "test"):
            split = _object(splits.get(name))
            start, end = date.fromisoformat(split["start"]), date.fromisoformat(split["end"])
            if start > end or (previous_end is not None and start <= previous_end):
                raise ValueError("protocol splits must be chronological and disjoint")
            if name == partition:
                bounds = start, end
            previous_end = end
    if partition != "diagnostic" and bounds is None:
        raise ValueError("named partitions require a protocol with chronological splits")
    variants: list[tuple[str, RiskPolicy, ForecastCalibration]] = [
        ("R0", RiskPolicy(), ForecastCalibration.disabled()),
    ]
    if candidate is not None:
        variants.append(("A", candidate, ForecastCalibration.disabled()))
    if calibration is not None:
        variants.append(("B", RiskPolicy(), calibration))
        if candidate is not None:
            variants.append(("AB", candidate, calibration))
    rows: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    classifications: dict[str, list[tuple[Level, Level]]] = {v[0]: [] for v in variants}
    requested = eligible_overall = outside_partition = 0
    seen: dict[str, str] = {}
    reference_identity: str | None = None
    evaluator = RiskEvaluator()
    for dataset in datasets:
        if dataset.get("algorithms_sha256") != algorithm_fingerprints():
            raise ValueError("snapshot algorithms differ; explicit dataset migration is required")
        reference = reference_policy(dataset)
        if reference_identity is None:
            reference_identity = policy_fingerprint(reference)
        if reference_identity != policy_fingerprint(reference):
            raise ValueError("all snapshots must share the same frozen observed target")
        config = _object(dataset.get("configuration"))
        period = DatePeriod(date.fromisoformat(config["start"]), date.fromisoformat(config["end"]))
        if period.days > 31:
            raise ValueError("each historical snapshot is limited to 31 days")
        lead_days = config["lead_days"]
        if isinstance(lead_days, bool) or not isinstance(lead_days, int) or not 1 <= lead_days <= 7:
            raise ValueError("snapshot lead_days must be between one and seven")
        forecast_payload, observed_payload = _object(dataset.get("forecast")), _object(
            dataset.get("observed")
        )
        forecast_zone = payload_timezone(forecast_payload)
        if forecast_zone != payload_timezone(observed_payload):
            raise ValueError("forecast and reference timezones must match")
        location = CanonicalLocation(
            config.get("name") or f"{config['latitude']},{config['longitude']}",
            config["latitude"], config["longitude"], forecast_zone, "historical-experiment",
        )
        coverage = config.get("minimum_coverage", 1.0)
        forecast_days = normalize_hourly(
            forecast_payload, period, suffix=f"_previous_day{lead_days}", minimum_coverage=coverage,
        )
        observed_days = normalize_hourly(observed_payload, period, minimum_coverage=coverage)
        collected = datetime.fromisoformat(dataset["collected_at"])
        if collected.tzinfo is None:
            raise ValueError("collection time must include a timezone")
        for day, forecast_day in forecast_days.items():
            if bounds is not None and not bounds[0] <= day <= bounds[1]:
                outside_partition += 1
                continue
            observed_day = observed_days[day]
            case_id = canonical_json([
                location.latitude, location.longitude, day.isoformat(), lead_days,
                config.get("forecast_model"), config.get("observed_model"),
            ])
            case_hash = digest([asdict(forecast_day), asdict(observed_day)])
            if case_id in seen:
                if seen[case_id] != case_hash:
                    raise ValueError("overlapping snapshots contain conflicting cases")
                continue
            seen[case_id] = case_hash
            requested += 1
            forecast = _normalized(forecast_day, location, collected)
            observed = _normalized(observed_day, location, collected)
            eligible = {
                event: forecast_day.eligible[event] and observed_day.eligible[event]
                for event in EVENT_FIELDS
            }
            complete = all(eligible.values())
            if complete:
                eligible_overall += 1
            for event, ok in eligible.items():
                if not ok:
                    exclusions.append({
                        "case_id": case_id, "date": day.isoformat(), "event": event,
                        "reason": "insufficient_hourly_coverage",
                        "forecast_expected_hours": forecast_day.expected_hours,
                        "observed_expected_hours": observed_day.expected_hours,
                        "forecast_valid_hours": forecast_day.valid_hours,
                        "observed_valid_hours": observed_day.valid_hours,
                    })
            for name, policy, profile in variants:
                adjusted = profile.apply(forecast)
                if complete:
                    classifications[name].append((
                        evaluator.evaluate(observed, reference).level,
                        evaluator.evaluate(adjusted, policy).level,
                    ))
                for event, ok in eligible.items():
                    if not ok:
                        continue
                    field = EVENT_FIELDS[event]
                    rows.append({
                        "case_id": case_id, "date": day.isoformat(), "variant": name,
                        "location": location.name, "lead_days": lead_days,
                        "month": day.month, "event": event, "unit": EVENT_UNITS[event],
                        "observed_level": event_level(observed.days[0], event, reference),
                        "predicted_level": event_level(adjusted.days[0], event, policy),
                        "observed_value": getattr(observed.days[0], field),
                        "predicted_value": getattr(adjusted.days[0], field),
                        "quality": {
                            "minimum_coverage": coverage,
                            "forecast_expected_hours": forecast_day.expected_hours,
                            "observed_expected_hours": observed_day.expected_hours,
                            "forecast_valid_hours": forecast_day.valid_hours,
                            "observed_valid_hours": observed_day.valid_hours,
                            "forecast_missing_fields": forecast_day.missing_fields,
                            "observed_missing_fields": observed_day.missing_fields,
                        },
                    })
    summaries: dict[str, Any] = {}
    for name, policy, profile in variants:
        variant_rows = [row for row in rows if row["variant"] == name]
        event_scores: dict[str, Any] = {}
        for event in EVENT_FIELDS:
            selected = [row for row in variant_rows if row["event"] == event]
            event_scores[event] = _score_rows(selected)
        strata: dict[str, Any] = {}
        for key in sorted({(r["location"], r["lead_days"], r["month"], r["event"])
                           for r in variant_rows}):
            selected = [r for r in variant_rows
                        if (r["location"], r["lead_days"], r["month"], r["event"]) == key]
            strata[canonical_json(key)] = _score_rows(selected)
        summaries[name] = {
            "policy": asdict(policy), "policy_sha256": policy_fingerprint(policy),
            "calibration": asdict(profile), "calibration_sha256": digest(asdict(profile)),
            "overall": asdict(classify_pairs(classifications[name])),
            "events": event_scores, "strata_location_lead_month_event": strata,
        }
    return {
        "schema": "climaprev-historical-comparison-v1", "partition": partition,
        "protocol_sha256": digest(protocol) if protocol is not None else None,
        "algorithms_sha256": algorithm_fingerprints(),
        "dataset_sha256": [digest(data) for data in datasets],
        "reference_kind": "reference-v1-on-reanalysis",
        "reference_policy_sha256": reference_identity,
        "requested_unique_days": requested, "eligible_overall_days": eligible_overall,
        "outside_partition_days": outside_partition, "excluded_events": exclusions,
        "variants": summaries, "cases": rows,
        "decision": "diagnostic_only_not_approved",
        "limitations": [
            "Observed targets are frozen v1 classifications on reanalysis, not impact labels.",
            "No promotion thresholds, sample sufficiency or uncertainty test approved.",
            "Month strata describe the sample; they are not validated regional seasons.",
        ],
    }


def _score_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "classification": asdict(classify_pairs([
            (row["observed_level"], row["predicted_level"]) for row in rows
        ])),
        "numerical": asdict(numerical_pairs([
            (row["observed_value"], row["predicted_value"]) for row in rows
        ])),
    }
