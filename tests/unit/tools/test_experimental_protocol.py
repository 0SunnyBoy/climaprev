from copy import deepcopy

import pytest
from tests.support.experiment import protocol_fixture

from climaprev.tools.experimental_protocol import validate_protocol
from climaprev.tools.historical_experiment import digest


def test_valid_protocol_is_copied_without_external_effects(tmp_path):
    envelope = protocol_fixture()
    result = validate_protocol(envelope)
    assert result == envelope["protocol"]
    result["models"].append("test-only")
    assert envelope["protocol"]["models"] == ["operational-baseline", "gfs_global"]
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("field", ["id", "stations", "variables", "models", "slots",
                                    "horizons", "slot_window_minutes",
                                    "provider_daily_call_limit", "code_version", "splits"])
def test_missing_required_field_is_rejected(field):
    envelope = protocol_fixture()
    del envelope["protocol"][field]
    envelope["sha256"] = digest(envelope["protocol"])
    with pytest.raises(ValueError, match="protocol"):
        validate_protocol(envelope)


@pytest.mark.parametrize("limit", [float("nan"), float("inf"), True, 0, -1, 1.5])
def test_invalid_call_budget_is_rejected(limit):
    envelope = protocol_fixture()
    envelope["protocol"]["provider_daily_call_limit"] = limit
    with pytest.raises(ValueError):
        validate_protocol(envelope)


def test_unknown_protocol_version_is_rejected_even_with_matching_hash():
    envelope = protocol_fixture()
    envelope["protocol"]["schema"] = "unknown"
    envelope["sha256"] = digest(envelope["protocol"])
    with pytest.raises(ValueError, match="schema"):
        validate_protocol(envelope)


def test_altered_protocol_is_rejected_without_rehash():
    envelope = protocol_fixture()
    envelope["protocol"]["id"] = "changed"
    with pytest.raises(ValueError, match="hash"):
        validate_protocol(envelope)


@pytest.mark.parametrize("field,value", [
    ("stations", []), ("models", []), ("variables", []), ("horizons", [True]),
    ("slots", ["2030-01-01T00:00:00"]), ("slot_window_minutes", 0),
])
def test_invalid_protocol_bounds_are_rejected(field, value):
    envelope = deepcopy(protocol_fixture())
    envelope["protocol"][field] = value
    envelope["sha256"] = digest(envelope["protocol"])
    with pytest.raises(ValueError):
        validate_protocol(envelope)
