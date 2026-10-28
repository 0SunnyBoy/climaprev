"""Versioned strategy records; registration alone never grants operational eligibility."""

import json
import re
from dataclasses import asdict
from typing import Any, cast

from climaprev.domain.bias_correction import ForecastCalibration
from climaprev.domain.risk_policy import ExperimentalRiskPolicy, RiskPolicy, policy_fingerprint
from climaprev.tools.experimental_protocol import validate_protocol
from climaprev.tools.historical_experiment import canonical_json, digest


def _sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _components(policy: dict[str, Any], calibration: dict[str, Any]) -> tuple[RiskPolicy, ForecastCalibration]:
    if set(policy) != set(asdict(RiskPolicy())) or set(calibration) != set(asdict(ForecastCalibration())):
        raise ValueError("strategy components require every explicit field")
    if policy["policy_version"] == "reference-v1":
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
    risk, profile = _components(policy or asdict(RiskPolicy()),
                                calibration or asdict(ForecastCalibration.disabled()))
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
