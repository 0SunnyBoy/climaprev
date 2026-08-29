from dataclasses import dataclass, field


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
