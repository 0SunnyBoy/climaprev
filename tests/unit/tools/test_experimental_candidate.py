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


def test_absent_opinion_stays_pending_without_scientific_conclusion():
    from climaprev.tools.experimental_candidate import record_decision

    result = record_decision(protocol_fixture(), candidate(), None)
    assert result["decision"]["outcome"] == "pending"
    assert result["decision"]["operational_eligible"] is False


@pytest.mark.parametrize("outcome", ["keep_v1", "reject", "inconclusive", "promote"])
def test_review_outcomes_bind_exact_evaluation_and_only_promotion_is_eligible(outcome):
    from tests.support.experiment import (
        approval_fixture,
        independent_evaluation_fixture,
        review_fixture,
    )

    from climaprev.tools.experimental_candidate import accepted_candidate, record_decision

    protocol, strategy = protocol_fixture(), candidate()
    evaluation = independent_evaluation_fixture(protocol, strategy)
    decision = record_decision(protocol, strategy, evaluation,
                               opinion=review_fixture(protocol, strategy, evaluation, outcome),
                               approvals=[approval_fixture(protocol, "E3")])
    assert decision["decision"]["outcome"] == outcome
    assert decision["decision"]["operational_eligible"] is (outcome == "promote")
    if outcome == "promote":
        assert accepted_candidate(protocol, strategy, evaluation, decision) == strategy["candidate"]
    else:
        with pytest.raises(ValueError, match="eligible"):
            accepted_candidate(protocol, strategy, evaluation, decision)


def test_other_hash_and_missing_e3_cannot_make_a_strategy_eligible():
    from tests.support.experiment import independent_evaluation_fixture, review_fixture

    from climaprev.tools.experimental_candidate import record_decision

    protocol, strategy = protocol_fixture(), candidate()
    evaluation = independent_evaluation_fixture(protocol, strategy)
    opinion = review_fixture(protocol, strategy, evaluation)
    with pytest.raises(ValueError, match="E3"):
        record_decision(protocol, strategy, evaluation, opinion=opinion)
    opinion["candidate_sha256"] = "c" * 64
    with pytest.raises(ValueError, match="identity"):
        record_decision(protocol, strategy, evaluation, opinion=opinion)


def test_rehashed_decision_cannot_change_a_pending_outcome_to_promote():
    from climaprev.tools.experimental_candidate import accepted_candidate, record_decision

    protocol, strategy = protocol_fixture(), candidate()
    decision = record_decision(protocol, strategy, None)
    decision["decision"].update(outcome="promote", operational_eligible=True)
    decision["sha256"] = digest(decision["decision"])
    with pytest.raises(ValueError, match="decision"):
        accepted_candidate(protocol, strategy, None, decision)


@pytest.mark.parametrize("component", ["policy", "calibration"])
@pytest.mark.parametrize("invalid", [{}, [], False, 0, ""])
def test_explicit_falsy_component_is_not_an_omitted_default(component, invalid):
    with pytest.raises((ValueError, TypeError)):
        candidate(**{component: invalid})


def test_explicit_none_retains_the_documented_baseline_defaults():
    result = candidate(policy=None, calibration=None)
    assert result["candidate"]["policy"]["policy_version"] == "reference-v1"
    assert result["candidate"]["calibration"] == asdict(ForecastCalibration.disabled())


@pytest.mark.parametrize("entry_point", ["register", "rehashed_envelope"])
def test_reference_v1_boolean_threshold_is_rejected_at_every_entry_point(entry_point):
    from climaprev.domain.risk_policy import RiskPolicy

    policy = asdict(RiskPolicy())
    policy["temperature_min_high_c"] = False
    if entry_point == "register":
        with pytest.raises(ValueError, match="finite numbers"):
            candidate(policy=policy)
    else:
        result = candidate(policy=None)
        result["candidate"]["policy"] = policy
        result["sha256"] = digest(result["candidate"])
        with pytest.raises(ValueError, match="finite numbers"):
            validate_candidate(result)
