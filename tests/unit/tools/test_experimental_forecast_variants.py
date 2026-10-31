from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from climaprev.tools.experimental_forecast_variants import ForecastVariant, apply_variant
from climaprev.tools.experimental_normalization import Measurement

START = datetime(2030, 1, 1, tzinfo=UTC)


def sample(value, **overrides):
    return replace(Measurement("precipitation_mm", START, START+timedelta(hours=1), value,
                                "mm", "previous_hour_sum"), **overrides)


def variant(**overrides):
    return replace(ForecastVariant("synthetic-blend", "precipitation_mm", "mm", (("a", .25), ("b", .75))), **overrides)


def test_explicit_blend_and_correction_are_reproducible_without_fitting_or_promotion():
    spec = variant(scale=1.2, offset=-.2)
    inputs = {"a": sample(2.), "b": sample(6.)}
    result = apply_variant(spec, inputs)
    assert result["value"] == pytest.approx(5.8)
    assert result == apply_variant(spec, dict(reversed(list(inputs.items()))))
    assert result["variant_sha256"] != apply_variant(variant(), inputs)["variant_sha256"]
    assert not result["fitted"] and not result["promotion_allowed"]


def test_missing_model_or_value_does_not_renormalize_weights():
    result = apply_variant(variant(), {"a": sample(2.)})
    assert result["value"] is None and result["missing_models"] == ["b"]
    result = apply_variant(variant(), {"a": sample(None), "b": sample(6.)})
    assert result["value"] is None and result["missing_models"] == ["a"]


@pytest.mark.parametrize("overrides", [
    {"unit": "km/h"}, {"variable": "gust_kmh"},
    {"start": START+timedelta(hours=1), "end": START+timedelta(hours=2)},
    {"semantics": "next_1_hours_sum"},
])
def test_incompatible_native_inputs_rejected(overrides):
    with pytest.raises(ValueError):
        apply_variant(variant(), {"a": sample(2.), "b": sample(6., **overrides)})


def test_clipping_is_explicit_and_negative_temperature_remains_valid():
    clipped = apply_variant(variant(offset=-100.), {"a": sample(2.), "b": sample(6.)})
    assert clipped["value"] == 0. and clipped["physically_clipped"]
    spec = ForecastVariant("synthetic-temperature", "temperature_c", "°C", (("a", 1.),), offset=-10.)
    result = apply_variant(spec, {"a": sample(-5., variable="temperature_c", unit="°C")})
    assert result["value"] == -15. and not result["physically_clipped"]


@pytest.mark.parametrize("overrides", [
    {"weights": (("a", .2), ("b", .2))}, {"weights": (("a", 1.), ("b", -1.))},
    {"weights": (("a", .5), ("a", .5))}, {"scale": float("nan")},
    {"scale": True}, {"name": "reference-v1"},
])
def test_invalid_coefficients_or_reserved_identity_rejected(overrides):
    with pytest.raises(ValueError):
        variant(**overrides)
