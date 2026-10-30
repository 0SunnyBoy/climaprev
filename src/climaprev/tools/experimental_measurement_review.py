"""Additional review of declared instrument context, outside the frozen collection pipeline."""

import hashlib
from dataclasses import asdict, dataclass
from datetime import timedelta
from math import isfinite
from pathlib import Path
from typing import Any

from climaprev.tools.experimental_equivalence import check_equivalence
from climaprev.tools.experimental_normalization import Measurement, validate_measurements


@dataclass(frozen=True, slots=True)
class MeasurementContext:
    source_id: str
    latitude: float
    longitude: float
    sensor_height_m: float | None = None
    representativeness_reviewed: bool = False

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not isinstance(self.representativeness_reviewed, bool):
            raise ValueError("source identity and explicit review state required")
        for value, bound in ((self.latitude, 90), (self.longitude, 180)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or abs(value) > bound:
                raise ValueError("invalid measurement point")
        if self.sensor_height_m is not None and (
            isinstance(self.sensor_height_m, bool) or not isinstance(self.sensor_height_m, (int, float))
            or not isfinite(self.sensor_height_m) or self.sensor_height_m < 0
        ):
            raise ValueError("invalid sensor height")


def review_measurement(
    target: str, forecast: Measurement, observation: Measurement, *,
    forecast_context: MeasurementContext, observation_context: MeasurementContext,
) -> dict[str, Any]:
    """No interpolation or inferred heights. Context declarations are not authenticated.

    Sensor height above ground is not station altitude. Instantaneous wind never
    becomes a ten-minute mean merely because both inputs use km/h.
    """
    if target == "wind_previous_10_minute_mean":
        reasons = []
        for role, sample, semantics in (
            ("forecast", forecast, "previous_10_minute_mean"),
            ("observation", observation, "observed_previous_10_minute_mean"),
        ):
            try:
                validate_measurements([sample], unit="km/h", semantics=semantics)
                if (sample.variable != "wind_kmh" or sample.value is None or sample.end is None
                        or sample.end-sample.start != timedelta(minutes=10)):
                    reasons.append(f"{role}_wind_contract")
            except (ValueError, TypeError):
                reasons.append(f"{role}_wind_contract")
        if forecast.start != observation.start or forecast.end != observation.end:
            reasons.append("different_window")
    else:
        reasons = list(check_equivalence(target, forecast, observation).exclusions)
    metadata_reasons = []
    if any(abs(getattr(forecast_context, field)-getattr(observation_context, field)) > .0001
           for field in ("latitude", "longitude")):
        metadata_reasons.append("point_version_mismatch")
    if target != "rain_accumulation":
        if forecast_context.sensor_height_m is None or observation_context.sensor_height_m is None:
            metadata_reasons.append("sensor_height_unknown")
        elif forecast_context.sensor_height_m != observation_context.sensor_height_m:
            metadata_reasons.append("sensor_height_mismatch")
    if not (forecast_context.representativeness_reviewed and observation_context.representativeness_reviewed):
        metadata_reasons.append("representativeness_not_reviewed")
    return {
        "schema": "climaprev-declared-measurement-review-v1", "target": target,
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "measurement_contract_compatible": not reasons,
        "declared_instrumental_review_complete": not reasons and not metadata_reasons,
        "measurement_exclusions": reasons, "metadata_exclusions": metadata_reasons,
        "forecast_context": asdict(forecast_context), "observation_context": asdict(observation_context),
        "context_authenticity_verified": False,
        "scientific_approval": False, "promotion_allowed": False,
    }
