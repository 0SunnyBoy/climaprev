"""Frozen strategies include every value-changing component."""

from dataclasses import asdict

import pytest
from tests.support.experiment import protocol_fixture

from climaprev.domain.bias_correction import ForecastCalibration
from climaprev.domain.risk_policy import ExperimentalRiskPolicy
from climaprev.tools.experimental_candidate import register_candidate, validate_candidate
from climaprev.tools.historical_experiment import digest


def candidate(**changes):
    values = {"protocol": protocol_fixture(), "policy": asdict(ExperimentalRiskPolicy()),
              "calibration": asdict(ForecastCalibration.disabled()),
              "normalization": {"version": "synthetic", "sha256": "a" * 64},
              "models": {"gfs_global": "b" * 64}, "code_version": "synthetic-revision"}
    values.update(changes)
    return register_candidate(**values)


def test_baseline_registry_preserves_reference_v1_disabled_defaults():
    result = register_candidate(protocol=protocol_fixture(),
                                normalization={"version": "synthetic", "sha256": "a" * 64},
                                models={"operational-baseline": "b" * 64}, code_version="fixture")
    value = validate_candidate(result)
    assert value["policy"]["policy_version"] == "reference-v1"
    assert value["calibration"] == asdict(ForecastCalibration.disabled())
    assert value["operational_eligible"] is False


def test_candidate_hash_identifies_all_components_and_protocol():
    result = candidate()
    value = validate_candidate(result)
    assert value["policy"]["policy_version"] == "reference-candidate-1"
    assert value["protocol_sha256"] == protocol_fixture()["sha256"]
    assert value["policy_sha256"]
    changed = candidate(normalization={"version": "synthetic", "sha256": "c" * 64})
    assert changed["sha256"] != result["sha256"]
    assert candidate() == result


@pytest.mark.parametrize("mutation", ["nan", "inverted", "tampered_normalization", "disabled_coefficients"])
def test_invalid_or_changed_candidate_is_refused(mutation):
    if mutation == "tampered_normalization":
        result = candidate()
        result["candidate"]["normalization"]["sha256"] = "c" * 64
        with pytest.raises(ValueError, match="hash"):
            validate_candidate(result)
        return
    policy = asdict(ExperimentalRiskPolicy())
    calibration = asdict(ForecastCalibration.disabled())
    if mutation == "nan":
        policy["daily_rain_high_mm"] = float("nan")
    elif mutation == "inverted":
        policy["daily_rain_high_mm"] = 20
    else:
        calibration["wind_multiplier"] = 2
    with pytest.raises(ValueError):
        candidate(policy=policy, calibration=calibration)


def test_rehashed_invalid_candidate_still_checks_internal_component_hashes():
    result = candidate()
    result["candidate"]["policy"]["daily_rain_high_mm"] = 60
    result["sha256"] = digest(result["candidate"])
    with pytest.raises(ValueError, match="hash"):
        validate_candidate(result)
