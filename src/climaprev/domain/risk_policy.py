import hashlib
import json
from dataclasses import asdict, dataclass, field
from math import isfinite


@dataclass(frozen=True, slots=True)
class RiskPolicy:
    hourly_rain_moderate_mm: float = 20.0
    hourly_rain_high_mm: float = 30.0
    daily_rain_moderate_mm: float = 30.0
    daily_rain_high_mm: float = 50.0
    wind_gust_moderate_kmh: float = 40.0
    wind_gust_high_kmh: float = 61.0
    temperature_max_moderate_c: float = 35.0
    temperature_max_high_c: float = 40.0
    temperature_min_moderate_c: float = 5.0
    temperature_min_high_c: float = 0.0
    policy_version: str = field(default="reference-v1", init=False)


@dataclass(frozen=True, slots=True)
class ExperimentalRiskPolicy(RiskPolicy):
    """Offline candidate; never changes the application's reference-v1 defaults."""

    policy_version: str = "reference-candidate-1"

    def __post_init__(self) -> None:
        if (not isinstance(self.policy_version, str)
                or not self.policy_version.startswith("reference-candidate-")):
            raise ValueError("experimental policies require a reference-candidate- identifier")
        if not self.policy_version.removeprefix("reference-candidate-").strip():
            raise ValueError("experimental policy identifier must not be empty")
        for name, value in asdict(self).items():
            if name != "policy_version" and (
                isinstance(value, bool) or not isinstance(value, int | float) or not isfinite(value)
            ):
                raise ValueError("policy thresholds must be finite numbers")
        for moderate, high in (
            (self.hourly_rain_moderate_mm, self.hourly_rain_high_mm),
            (self.daily_rain_moderate_mm, self.daily_rain_high_mm),
            (self.wind_gust_moderate_kmh, self.wind_gust_high_kmh),
            (self.temperature_max_moderate_c, self.temperature_max_high_c),
        ):
            if moderate >= high:
                raise ValueError("moderate threshold must be below high threshold")
        if self.temperature_min_high_c >= self.temperature_min_moderate_c:
            raise ValueError("high cold threshold must be below moderate threshold")
        if min(self.hourly_rain_moderate_mm, self.daily_rain_moderate_mm,
               self.wind_gust_moderate_kmh) < 0:
            raise ValueError("rain and wind thresholds must not be negative")


def policy_fingerprint(policy: RiskPolicy) -> str:
    """Identify the exact parameters as well as the declared policy name."""
    content = json.dumps(asdict(policy), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(content.encode()).hexdigest()
