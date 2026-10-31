"""Fixed experimental blends/corrections, without fitting, ranking or runtime integration."""

import hashlib
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from math import isclose, isfinite
from pathlib import Path
from typing import Any, cast

from climaprev.tools.experimental_normalization import Measurement, validate_measurements
from climaprev.tools.historical_experiment import digest

_UNITS = {"precipitation_mm": "mm", "temperature_c": "°C", "humidity_pct": "%",
          "wind_kmh": "km/h", "gust_kmh": "km/h"}


@dataclass(frozen=True, slots=True)
class ForecastVariant:
    name: str
    variable: str
    unit: str
    weights: tuple[tuple[str, float], ...]
    scale: float = 1.
    offset: float = 0.

    def __post_init__(self) -> None:
        if (not self.name.strip() or self.name.strip() == "reference-v1"
                or _UNITS.get(self.variable) != self.unit or not self.weights):
            raise ValueError("named variable/unit contract and explicit weights required")
        if not isinstance(self.weights, tuple) or any(not isinstance(pair, tuple) for pair in self.weights):
            raise TypeError("weights must be an immutable tuple of pairs")
        models = [model for model, _ in self.weights]
        if any(not model.strip() for model in models) or len(set(models)) != len(models):
            raise ValueError("distinct model identities required")
        weights = [weight for _, weight in self.weights]
        for value in [*weights, self.scale, self.offset]:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError("finite coefficients required")
        if any(weight <= 0 for weight in weights) or not isclose(sum(weights), 1., abs_tol=1e-12, rel_tol=0):
            raise ValueError("positive weights summing to one required")
        if self.scale <= 0:
            raise ValueError("positive scale required")


def apply_variant(variant: ForecastVariant, samples: Mapping[str, Measurement]) -> dict[str, Any]:
    """Require identical native measurement windows and all specified arms.

    Missing arms never trigger weight renormalization. Physical clipping is
    explicit, not a calibrated forecast. Cross-variable mixing is prohibited.
    """
    weights = dict(variant.weights)
    if set(samples) - set(weights):
        raise ValueError("unexpected model input")
    missing = sorted(set(weights)-set(samples))
    reference = None
    for model, sample in sorted(samples.items()):
        validate_measurements([sample], unit=variant.unit, semantics=sample.semantics)
        if sample.variable != variant.variable:
            raise ValueError("variable differs from variant")
        if reference is not None and (sample.start != reference.start or sample.end != reference.end
                                      or sample.semantics != reference.semantics):
            raise ValueError("native measurement windows/semantics differ")
        reference = sample
        if sample.value is None:
            missing.append(model)
    inputs = {model: asdict(sample) for model, sample in sorted(samples.items())}
    result: dict[str, Any] = {
        "schema": "climaprev-fixed-forecast-variant-v1", "specification": asdict(variant),
        "variant_sha256": digest(asdict(variant)), "input_sha256": digest(inputs),
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "missing_models": sorted(missing), "value": None, "measurement": None,
        "physically_clipped": False, "status": "incomplete" if missing else "available",
        "fitted": False, "scientific_approval": False, "promotion_allowed": False,
        "limitations": ["Weights/corrections are caller-specified experimental alternatives.",
                        "Agreement or averaging is not a calibrated probability.",
                        "Blending can damp extremes and requires independent verification."],
    }
    if missing or reference is None:
        return result
    value = sum(weights[model]*cast(float, samples[model].value) for model in weights) * variant.scale + variant.offset
    if not isfinite(value):
        raise ValueError("variant calculation overflow")
    bounded = value if variant.variable == "temperature_c" else max(0., value)
    if variant.variable == "humidity_pct":
        bounded = min(100., bounded)
    measurement = Measurement(variant.variable, reference.start, reference.end, bounded,
                              variant.unit, reference.semantics)
    result.update(value=bounded, measurement=asdict(measurement), physically_clipped=bounded != value)
    return result
