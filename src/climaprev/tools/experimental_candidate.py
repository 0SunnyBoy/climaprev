"""Versioned strategy records; registration alone never grants operational eligibility."""

import json
import re
from collections.abc import Sequence
from dataclasses import asdict
from typing import Any, cast

from climaprev.domain.bias_correction import ForecastCalibration
from climaprev.domain.risk_policy import ExperimentalRiskPolicy, RiskPolicy, policy_fingerprint
from climaprev.tools.experimental_protocol import (
    aware_timestamp,
    execute_authorized,
    validate_protocol,
)
from climaprev.tools.historical_experiment import algorithm_fingerprints, canonical_json, digest


def _sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _components(policy: dict[str, Any], calibration: dict[str, Any]) -> tuple[RiskPolicy, ForecastCalibration]:
    if not isinstance(policy, dict) or not isinstance(calibration, dict):
        raise TypeError("strategy components must be objects")
    if set(policy) != set(asdict(RiskPolicy())) or set(calibration) != set(asdict(ForecastCalibration())):
        raise ValueError("strategy components require every explicit field")
    if policy["policy_version"] == "reference-v1":
        ExperimentalRiskPolicy(**{key: value for key, value in policy.items() if key != "policy_version"})
        if policy != asdict(RiskPolicy()):
            raise ValueError("reference-v1 parameters are frozen")
        risk: RiskPolicy = RiskPolicy()
    else:
        risk = ExperimentalRiskPolicy(**policy)
    if not isinstance(calibration["enabled"], bool):
        raise TypeError("calibration enabled must be boolean")
    for key, value in calibration.items():
        if key not in {"profile_version", "enabled"} and (isinstance(value, bool)
                                                        or not isinstance(value, (int, float))):
            raise ValueError("calibration coefficients must be numeric")
    profile = ForecastCalibration(**calibration)
    if ((not profile.enabled and profile != ForecastCalibration.disabled())
            or (profile.enabled and profile.profile_version == "disabled")):
        raise ValueError("disabled profile is frozen; enabled profiles need their own version")
    return risk, profile


def register_candidate(
    *, protocol: dict[str, Any], normalization: dict[str, str], models: dict[str, str],
    code_version: str, policy: dict[str, Any] | None = None,
    calibration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    frozen_protocol = validate_protocol(protocol)
    risk, profile = _components(policy if policy is not None else asdict(RiskPolicy()),
                                calibration if calibration is not None else asdict(ForecastCalibration.disabled()))
    if (not code_version.strip() or set(normalization) != {"version", "sha256"}
            or not normalization["version"].strip() or not _sha(normalization["sha256"])
            or not models or not set(models) <= set(frozen_protocol["models"])
            or any(not _sha(value) for value in models.values())):
        raise ValueError("strategy requires versioned normalization, models and code")
    value = {"schema": "climaprev-candidate-v1", "protocol_sha256": protocol["sha256"],
             "code_version": code_version, "policy": asdict(risk),
             "policy_sha256": policy_fingerprint(risk), "calibration": asdict(profile),
             "calibration_sha256": digest(asdict(profile)), "normalization": normalization,
             "models": models, "operational_eligible": False}
    return cast(dict[str, Any], json.loads(canonical_json({"candidate": value, "sha256": digest(value)})))


def validate_candidate(envelope: dict[str, Any]) -> dict[str, Any]:
    value = envelope.get("candidate")
    if (set(envelope) != {"candidate", "sha256"} or not isinstance(value, dict)
            or value.get("schema") != "climaprev-candidate-v1" or envelope["sha256"] != digest(value)):
        raise ValueError("invalid candidate schema or hash")
    expected = {"schema", "protocol_sha256", "code_version", "policy", "policy_sha256",
                "calibration", "calibration_sha256", "normalization", "models", "operational_eligible"}
    if set(value) != expected or not _sha(value["protocol_sha256"]) or not value["code_version"].strip():
        raise ValueError("invalid frozen candidate fields")
    risk, profile = _components(value["policy"], value["calibration"])
    normalization = value["normalization"]
    if (value["policy_sha256"] != policy_fingerprint(risk)
            or value["calibration_sha256"] != digest(asdict(profile))
            or set(normalization) != {"version", "sha256"} or not normalization["version"].strip()
            or not _sha(normalization["sha256"]) or not value["models"]
            or any(not name.strip() or not _sha(checksum) for name, checksum in value["models"].items())
            or value["operational_eligible"] is not False):
        raise ValueError("invalid candidate component hash or identity")
    return cast(dict[str, Any], json.loads(canonical_json(value)))


def record_decision(
    protocol: dict[str, Any], candidate: dict[str, Any], evaluation: dict[str, Any] | None,
    *, opinion: dict[str, Any] | None = None, approvals: Sequence[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Record a human conclusion against exact inputs, without inventing an opinion."""
    validate_protocol(protocol)
    value = validate_candidate(candidate)
    if value["protocol_sha256"] != protocol["sha256"]:
        raise ValueError("candidate protocol identity differs")
    evaluation_sha = digest(evaluation) if evaluation is not None else None
    if evaluation is not None and (evaluation.get("schema") != "climaprev-independent-evaluation-v1"
                                   or evaluation.get("protocol_sha256") != protocol["sha256"]
                                   or evaluation.get("candidate_sha256") != candidate["sha256"]):
        raise ValueError("evaluation identity differs")
    outcome = "pending"
    if opinion is not None:
        outcome = opinion.get("outcome", "")
        if (outcome not in {"keep_v1", "reject", "inconclusive", "promote"}
                or any(not isinstance(opinion.get(k), str) or not opinion[k].strip()
                       for k in ("reviewer", "reference", "recorded_at"))
                or opinion.get("protocol_sha256") != protocol["sha256"]
                or opinion.get("candidate_sha256") != candidate["sha256"]
                or opinion.get("evaluation_sha256") != evaluation_sha):
            raise ValueError("human opinion identity or conclusion is invalid")
        aware_timestamp(opinion["recorded_at"])
    if outcome == "promote":
        if evaluation is None or evaluation.get("mode") != "confirmatory":
            raise ValueError("promotion needs an independent confirmatory evaluation")
        report = evaluation["report"]
        if report.get("algorithms_sha256") != algorithm_fingerprints():
            raise ValueError("promotion evaluation algorithms differ from installed code")
        if (report.get("partition") != "test" or report.get("protocol_sha256") != digest(protocol["protocol"])
                or evaluation["population"]["eligible_overall_days"] < 1
                or any(evaluation["population"][key] != report[key] for key in evaluation["population"])
                or not any(v["policy_sha256"] == value["policy_sha256"]
                           and v["calibration_sha256"] == value["calibration_sha256"]
                           for v in report["variants"].values())):
            raise ValueError("promotion evaluation lacks the frozen strategy or test population")
        execute_authorized(protocol, "operational", lambda _: None, approvals=approvals)
    decision = {"schema": "climaprev-candidate-decision-v1", "outcome": outcome,
                "protocol_sha256": protocol["sha256"], "candidate_sha256": candidate["sha256"],
                "evaluation_sha256": evaluation_sha, "opinion": opinion,
                "approvals": list(approvals), "operational_eligible": outcome == "promote"}
    return cast(dict[str, Any], json.loads(canonical_json({"decision": decision, "sha256": digest(decision)})))


def accepted_candidate(
    protocol: dict[str, Any], candidate: dict[str, Any], evaluation: dict[str, Any] | None,
    decision: dict[str, Any],
) -> dict[str, Any]:
    value = decision.get("decision", {})
    expected = record_decision(protocol, candidate, evaluation, opinion=value.get("opinion"),
                               approvals=value.get("approvals", ()))
    if decision != expected:
        raise ValueError("decision differs from its evidence-bound outcome")
    if expected["decision"]["operational_eligible"] is not True:
        raise ValueError("candidate is not operationally eligible")
    return validate_candidate(candidate)
