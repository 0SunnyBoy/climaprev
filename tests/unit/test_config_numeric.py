import math

import pytest
from pydantic import ValidationError

from climaprev.config import Settings


@pytest.mark.parametrize("field", ["rate_limit", "rate_limit_window_seconds", "rate_limit_burst"])
@pytest.mark.parametrize("value", [0, -1])
def test_limits_and_windows_must_be_positive(field, value):
    with pytest.raises(ValidationError) as raised:
        Settings(**{field: value})
    assert field in str(raised.value)
    assert "input_value" not in str(raised.value)


@pytest.mark.parametrize("field", ["connect_timeout_seconds", "read_timeout_seconds",
                                   "redis_socket_timeout_seconds"])
@pytest.mark.parametrize("value", [0, -0.1, math.nan, math.inf, -math.inf])
def test_timeouts_must_be_positive_and_finite(field, value):
    with pytest.raises(ValidationError) as raised:
        Settings(**{field: value})
    assert field in str(raised.value)
    assert "input_value" not in str(raised.value)


@pytest.mark.parametrize("value,expected", [(0, 0), (2, 2), (3, 2)])
def test_retries_keep_supported_values_and_clamp_only_above_two(value, expected):
    assert Settings(additional_retries=value).additional_retries == expected


def test_negative_retries_fail_before_startup():
    with pytest.raises(ValidationError) as raised:
        Settings(additional_retries=-1)
    assert "additional_retries" in str(raised.value)


def test_bad_environment_number_does_not_echo_raw_configuration(monkeypatch):
    monkeypatch.setenv("CLIMAPREV_CONNECT_TIMEOUT_SECONDS", "SentinelSecret")
    with pytest.raises(ValidationError) as raised:
        Settings()
    assert "SentinelSecret" not in str(raised.value)
    assert "connect_timeout_seconds" in str(raised.value)


def test_default_runtime_numbers_are_valid_and_keep_load_zero_delay():
    configured = Settings()
    assert configured.rate_limit == 60
    assert configured.rate_limit_burst == 10
    assert configured.rate_limit_window_seconds == 60
    assert configured.connect_timeout_seconds == 2
    assert configured.read_timeout_seconds == 5
    assert configured.redis_socket_timeout_seconds == 1
    assert configured.additional_retries == 2
    assert Settings(load_redis_operation_delay_ms=0).load_redis_operation_delay_ms == 0
